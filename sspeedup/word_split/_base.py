from abc import ABC, abstractmethod
from collections import Counter
from typing import Generator, Optional, Set


class WordSplitter(ABC):
    def __init__(
        self,
        stopwords: Optional[Set[str]] = None,
        hotwords: Optional[Set[str]] = None,
        allowed_word_types: Optional[Set[str]] = None,
        stopwords_file: Optional[str] = None,
        hotwords_file: Optional[str] = None,
        allowed_word_types_file: Optional[str] = None,
    ) -> None:
        self.stopwords: Set[str] = set()
        self.hotwords: Set[str] = set()
        self.allowed_word_types: Set[str] = set()

        if stopwords:
            self.add_stopwords(stopwords)
        if hotwords:
            self.add_hotwords(hotwords)
        if allowed_word_types:
            self.set_allowed_word_type(allowed_word_types)

        if stopwords_file:
            self.add_stopwords_file(stopwords_file)
        if hotwords_file:
            self.add_hotwords_file(hotwords_file)
        if allowed_word_types_file:
            self.set_allowed_word_types_file(allowed_word_types_file)

    @abstractmethod
    def init(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_stopwords(self, word_list: Set[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_hotwords(self, word_list: Set[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_allowed_word_type(self, types: Set[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_stopwords_file(self, file_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_hotwords_file(self, file_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_allowed_word_types_file(self, file_name: str) -> None:
        raise NotImplementedError

    def _get_hotwords_need_to_process(self, word_list: Set[str]) -> Set[str]:
        return word_list - self.hotwords

    @abstractmethod
    def split(self, text: str) -> Generator[str, None, None]:
        raise NotImplementedError

    @abstractmethod
    def get_word_freq(self, text: str) -> Counter:
        raise NotImplementedError
