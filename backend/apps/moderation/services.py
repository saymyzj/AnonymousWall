import re


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
        for i, char in enumerate(chars):
            if char not in level_dict:
                level_dict[char] = {}
            level_dict = level_dict[char]
        level_dict[self.delimit] = self.delimit

    def _normalize(self, text):
        """Remove common obfuscation characters."""
        text = text.lower()
        # Remove spaces, special chars between words
        text = re.sub(r'[\s\*\-\_\.\,\!\@\#\$\%\^\&\(\)\+\=]+', '', text)
        return text

    def check(self, text):
        """Check text for sensitive words. Returns (hard_words, soft_words)."""
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
                        found_word = normalized[i:j+1]
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


def check_content(text):
    """Check content for sensitive words.
    Returns: (is_blocked: bool, is_suspect: bool, hard_words: list, soft_words: list)
    """
    dfa = DFAFilter.get_instance()
    hard_words, soft_words = dfa.check(text)
    return bool(hard_words), bool(soft_words), hard_words, soft_words
