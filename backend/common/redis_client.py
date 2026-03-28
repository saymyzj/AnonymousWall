from functools import lru_cache
import socket
from urllib.parse import urlparse

from django.conf import settings


class RedisUnavailable(Exception):
    pass


class MinimalRedisClient:
    def __init__(self, url: str, timeout: float = 0.5):
        parsed = urlparse(url)
        self.host = parsed.hostname or '127.0.0.1'
        self.port = parsed.port or 6379
        self.password = parsed.password
        self.db = int((parsed.path or '/0').lstrip('/') or 0)
        self.timeout = timeout

    def get(self, key: str):
        return self._execute('GET', key)

    def mget(self, keys: list[str]):
        if not keys:
            return []
        return self._execute('MGET', *keys)

    def set(self, key: str, value, ex: int | None = None):
        parts = ['SET', key, str(value)]
        if ex:
            parts.extend(['EX', str(ex)])
        return self._execute(*parts)

    def delete(self, *keys: str):
        if not keys:
            return 0
        return self._execute('DEL', *keys)

    def _execute(self, *parts):
        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                sock.settimeout(self.timeout)
                reader = sock.makefile('rb')
                if self.password:
                    self._send_command(sock, 'AUTH', self.password)
                    self._read_response(reader)
                if self.db:
                    self._send_command(sock, 'SELECT', str(self.db))
                    self._read_response(reader)
                self._send_command(sock, *parts)
                return self._read_response(reader)
        except OSError as exc:
            raise RedisUnavailable(str(exc)) from exc

    def _send_command(self, sock: socket.socket, *parts):
        payload = [f'*{len(parts)}\r\n'.encode('utf-8')]
        for part in parts:
            raw = str(part).encode('utf-8')
            payload.append(f'${len(raw)}\r\n'.encode('utf-8'))
            payload.append(raw + b'\r\n')
        sock.sendall(b''.join(payload))

    def _read_response(self, reader):
        prefix = reader.read(1)
        if not prefix:
            raise RedisUnavailable('empty response from redis')

        if prefix == b'+':
            return reader.readline().decode('utf-8').rstrip('\r\n')
        if prefix == b'-':
            message = reader.readline().decode('utf-8').rstrip('\r\n')
            raise RedisUnavailable(message)
        if prefix == b':':
            return int(reader.readline().decode('utf-8').rstrip('\r\n'))
        if prefix == b'$':
            length = int(reader.readline().decode('utf-8').rstrip('\r\n'))
            if length == -1:
                return None
            data = reader.read(length)
            reader.read(2)
            return data.decode('utf-8')
        if prefix == b'*':
            length = int(reader.readline().decode('utf-8').rstrip('\r\n'))
            if length == -1:
                return None
            return [self._read_response(reader) for _ in range(length)]

        raise RedisUnavailable(f'unexpected redis prefix: {prefix!r}')


@lru_cache(maxsize=1)
def get_redis_client():
    redis_url = getattr(settings, 'REDIS_URL', '').strip()
    if not redis_url:
        return None

    try:
        import redis  # type: ignore
    except ImportError:
        return MinimalRedisClient(redis_url, timeout=getattr(settings, 'REDIS_TIMEOUT', 0.5))

    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=getattr(settings, 'REDIS_TIMEOUT', 0.5),
        socket_timeout=getattr(settings, 'REDIS_TIMEOUT', 0.5),
    )
