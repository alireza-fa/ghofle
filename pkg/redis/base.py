from abc import ABC
from typing import Dict, List, Any
from ast import literal_eval

from redis import Redis as BaseRedis


class Redis(ABC):

    def __init__(self, host: str, port: int, password: str) -> None:
        self.r = BaseRedis(host=host, port=port, password=password)

    def set(self, key: str, value: str | int | Dict | List, timeout: int | None = None) -> None:
        """
        Timeout base on second.
        """
        if isinstance(value, list) or isinstance(value, dict):
            value = str(value)
        self.r.set(name=key, value=value)
        if timeout:
            self.set_expire(key=key, timeout=timeout)

    def get(self, key: str) -> Any | None:
        value = self.r.get(name=key)
        if not value:
            return None
        try:
            value = literal_eval(value.decode())
        except (ValueError, SyntaxError):
            return value.decode()
        return value

    def delete(self, *keys) -> None:
        self.r.delete(*keys)

    def incr_by(self, key: str, amount: int = 1, timeout: int | None = None) -> None:
        """
        Set expiry only when the key has no expiry
        """
        self.r.incrby(name=key, amount=amount)
        if timeout:
            self.set_expire(key=key, timeout=timeout, nx=True)

    def incr(self, key: str, timeout: int | None = None) -> None:
        """
        Set expiry only when the key has no expiry
        """
        self.incr_by(key=key)
        if timeout:
            self.set_expire(key=key, timeout=timeout, nx=True)

    def decr_by(self, key: str, amount: int = 1, timeout: int | None = None) -> None:
        """
        Set expiry only when the key has no expiry
        """
        self.r.decr(name=key, amount=amount)
        if timeout:
            self.set_expire(key=key, timeout=timeout, nx=True)

    def decr(self, key: str, timeout: int | None = None) -> None:
        """
        Set expiry only when the key has no expiry
        """
        self.decr_by(key=key)
        if timeout:
            self.set_expire(key=key, timeout=timeout, nx=True)

    def set_expire(self, key: str, timeout: int,
                   nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False) -> None:
        """
        Valid options are:
            NX -> Set expiry only when the key has no expiry
            XX -> Set expiry only when the key has an existing expiry
            GT -> Set expiry only when the new expiry is greater than current one
            LT -> Set expiry only when the new expiry is less than current one
        """
        self.r.expire(name=key, time=timeout, nx=nx, xx=xx, gt=gt, lt=lt)

    def delete_all(self) -> None:
        self.r.flushall()

    def close(self) -> None:
        self.r.close()
