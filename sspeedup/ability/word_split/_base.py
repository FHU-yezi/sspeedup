from abc import ABC, abstractmethod
from collections import Counter
from typing import AsyncGenerator, Optional, Set

from httpx import AsyncClient


class AbilitySplitter(ABC):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6001,
        https: bool = False,
        stopwords: Optional[Set[str]] = None,
        allowed_word_types: Optional[Set[str]] = None,
        stopwords_file: Optional[str] = None,
        allowed_word_types_file: Optional[str] = None,
    ) -> None:
        self._client = AsyncClient(
            base_url=f"{'https' if https else 'http'}://{host}:{port}/api",
            timeout=20,
        )
        self._stopwords: Set[str] = set()
        self._allowed_word_types: Set[str] = set()

        if stopwords:
            self.add_stopwords(stopwords)
        if allowed_word_types:
            self.set_allowed_word_type(allowed_word_types)

        if stopwords_file:
            self.add_stopwords_file(stopwords_file)
        if allowed_word_types_file:
            self.set_allowed_word_types_file(allowed_word_types_file)

    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_stopwords(self, word_list: Set[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_allowed_word_type(self, types: Set[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_stopwords_file(self, file_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_allowed_word_types_file(self, file_name: str) -> None:
        raise NotImplementedError

    def _get_stopwords_need_to_process(self, word_list: Set[str]) -> Set[str]:
        return word_list - self._stopwords

    @abstractmethod
    async def split(self, text: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    @abstractmethod
    async def get_word_freq(self, text: str) -> Counter:
        raise NotImplementedError
