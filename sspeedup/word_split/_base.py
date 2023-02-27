from abc import ABC, abstractmethod
from collections import Counter
from typing import Generator, Set


class WordSplitter(ABC):
    def __init__(self) -> None:
        self.stopwords: Set[str] = set()
        self.hotwords: Set[str] = set()
        self.allowed_word_type: Set[str] = set()

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
    def add_stopwords_file(self, file_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_hotwords_file(self, file_name: str) -> None:
        raise NotImplementedError

    def _get_stopwords_need_to_process(self, word_list: Set[str]) -> Set[str]:
        return word_list - self.stopwords

    def _get_hotwords_need_to_process(self, word_list: Set[str]) -> Set[str]:
        return word_list - self.hotwords

    @abstractmethod
    def split(self, sentence: str) -> Generator[str, None, None]:
        raise NotImplementedError

    @abstractmethod
    def get_word_freq(self, sentence: str) -> Counter:
        raise NotImplementedError
