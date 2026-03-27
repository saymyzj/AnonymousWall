import json
import os
import re
import ssl
import urllib.error
import urllib.request

from django.conf import settings


class DFAFilter:
    """DFA-based sensitive word filter."""
    instance = None

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = cls()
            cls.instance.load_from_db()
        return cls.instance

    @classmethod
    def rebuild(cls):
        cls.instance = None

    def load_from_db(self):
        from .models import SensitiveWord
        self.keyword_chains = {}
        self.word_levels = {}
        try:
            for sw in SensitiveWord.objects.all():
                self.add_word(sw.word, sw.level)
        except Exception:
            pass

    def add_word(self, keyword, level='soft'):
        keyword = keyword.lower().strip()
        if not keyword:
            return
        self.word_levels[keyword] = level
        chars = keyword
        level_dict = self.keyword_chains
        for char in chars:
            if char not in level_dict:
                level_dict[char] = {}
            level_dict = level_dict[char]
        level_dict[self.delimit] = self.delimit

    def _normalize(self, text):
        text = text.lower()
        text = re.sub(r'[\s\*\-\_\.\,\!\@\#\$\%\^\&\(\)\+\=]+', '', text)
        return text

    def check(self, text):
        normalized = self._normalize(text)
        hard_words = []
        soft_words = []

        i = 0
        while i < len(normalized):
            level_dict = self.keyword_chains
            j = i
            found_word = None
            while j < len(normalized):
                char = normalized[j]
                if char in level_dict:
                    level_dict = level_dict[char]
                    if self.delimit in level_dict:
                        found_word = normalized[i:j + 1]
                    j += 1
                else:
                    break

            if found_word:
                level = self.word_levels.get(found_word, 'soft')
                if level == 'hard':
                    hard_words.append(found_word)
                else:
                    soft_words.append(found_word)
                i = j
            else:
                i += 1

        return hard_words, soft_words


def _extract_json_payload(content):
    if isinstance(content, dict):
        return content

    normalized = (content or '').strip()
    if normalized.startswith('```'):
        normalized = re.sub(r'^```(?:json)?\s*', '', normalized)
        normalized = re.sub(r'\s*```$', '', normalized)
    return json.loads(normalized)


def audit_with_deepseek(text, content_type='post'):
    api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
    model = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')
    base_url = getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com').rstrip('/')
    timeout = getattr(settings, 'DEEPSEEK_TIMEOUT', 25)

    if not api_key:
        return {
            'enabled': False,
            'decision': 'unknown',
            'reason': '未配置 DEEPSEEK_API_KEY，已跳过 AI 审核',
            'model': model,
        }

    prompt = (
        '你是校园匿名社区的内容审核助手。'
        '请只返回 JSON，字段为 decision、risk_level 和 reason。'
        'decision 只能是 accept、confuse、reject 三个值。'
        'risk_level 只能是 high、medium、low、none 四个值。'
        '遇到辱骂、人身攻击、色情低俗、隐私泄露、违法违规、广告引流等内容时从严判断。'
        f'当前审核对象类型: {content_type}。'
    )

    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': prompt},
            {
                'role': 'user',
                'content': f'请审核以下内容是否适合发布，并给出简短中文原因：\n{text}',
            },
        ],
        'temperature': 0.1,
        'stream': False,
        'response_format': {
            'type': 'json_object',
        },
    }

    request = urllib.request.Request(
        f'{base_url}/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        cafile = os.environ.get('SSL_CERT_FILE') or '/etc/ssl/cert.pem'
        ssl_context = ssl.create_default_context(cafile=cafile)

        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            raw = json.loads(response.read().decode('utf-8'))
        content = raw['choices'][0]['message']['content']
        parsed = _extract_json_payload(content)
        decision = parsed.get('decision', 'confuse')
        legacy_map = {
            'safe': 'accept',
            'review': 'confuse',
            'reject': 'reject',
        }
        decision = legacy_map.get(decision, decision)
        if decision not in {'accept', 'confuse', 'reject'}:
            decision = 'confuse'
        risk_level = parsed.get('risk_level', 'none')
        if risk_level not in {'high', 'medium', 'low', 'none'}:
            risk_level = 'medium' if decision == 'confuse' else ('high' if decision == 'reject' else 'none')
        return {
            'enabled': True,
            'decision': decision,
            'risk_level': risk_level,
            'reason': parsed.get('reason', 'AI 未返回原因'),
            'model': model,
        }
    except urllib.error.HTTPError as error:
        detail = ''
        try:
            detail = error.read().decode('utf-8')[:300]
        except Exception:
            detail = str(error)
        reason = 'AI 审核调用失败，已自动转入人工复核'
        if detail:
            reason = f'{reason}：{detail}'
        return {
            'enabled': True,
            'decision': 'confuse',
            'risk_level': 'medium',
            'reason': reason,
            'model': model,
        }
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, IndexError):
        return {
            'enabled': True,
            'decision': 'confuse',
            'risk_level': 'medium',
            'reason': 'AI 审核调用失败，已自动转入人工复核',
            'model': model,
        }


def check_content(text, content_type='post'):
    """
    Returns:
      {
        is_blocked: bool,
        is_suspect: bool,
        hard_words: list,
        soft_words: list,
        ai_decision: str,
        ai_risk_level: str,
        ai_reason: str,
        ai_enabled: bool,
        ai_model: str,
        moderation_source: str,
        moderation_reason: str,
      }
    """
    dfa = DFAFilter.get_instance()
    hard_words, soft_words = dfa.check(text)

    if hard_words:
        reason = f'命中硬拦截敏感词：{"、".join(hard_words)}'
        return {
            'is_blocked': True,
            'is_suspect': True,
            'hard_words': hard_words,
            'soft_words': soft_words,
            'ai_decision': 'not_run',
            'ai_risk_level': 'high',
            'ai_reason': reason,
            'ai_enabled': False,
            'ai_model': '',
            'moderation_source': 'hard_word',
            'moderation_reason': reason,
        }

    if soft_words:
        reason = f'命中软标记敏感词：{"、".join(soft_words)}'
        return {
            'is_blocked': False,
            'is_suspect': True,
            'hard_words': hard_words,
            'soft_words': soft_words,
            'ai_decision': 'not_run',
            'ai_risk_level': 'medium',
            'ai_reason': reason,
            'ai_enabled': False,
            'ai_model': '',
            'moderation_source': 'soft_word',
            'moderation_reason': reason,
        }

    ai_result = audit_with_deepseek(text, content_type=content_type)
    ai_decision = ai_result['decision']
    ai_risk_level = ai_result.get('risk_level', 'none')

    return {
        'is_blocked': False,
        'is_suspect': ai_decision in {'confuse', 'reject'},
        'hard_words': hard_words,
        'soft_words': soft_words,
        'ai_decision': ai_decision,
        'ai_risk_level': ai_risk_level,
        'ai_reason': ai_result['reason'],
        'ai_enabled': ai_result['enabled'],
        'ai_model': ai_result['model'],
        'moderation_source': 'ai',
        'moderation_reason': ai_result['reason'],
    }
