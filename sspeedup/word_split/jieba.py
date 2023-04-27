from collections import Counter
from typing import Generator, Set

from jieba import add_word, cut, cut_for_search, load_userdict
from jieba import logging as jieba_logging
from jieba.posseg import cut as cut_poseg

from sspeedup.word_split._base import WordSplitter

jieba_logging.disable()


class JiebaSplitter(WordSplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        self.stopwords = word_list

    def add_hotwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_hotwords_need_to_process(word_list)
        for word in word_list_to_add:
            add_word(word)

        self.hotwords = self.hotwords.union(word_list_to_add)

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            self.stopwords = {x.strip() for x in f.readlines()}

    def set_allowed_word_type(self, types: Set[str]) -> None:
        del types
        raise NotImplementedError

    def add_hotwords_file(self, file_name: str) -> None:
        load_userdict(file_name)

    def set_allowed_word_types_file(self, file_name: str) -> None:
        del file_name
        raise NotImplementedError

    def split(self, text: str) -> Generator[str, None, None]:
        for word in cut(text):
            if len(word) == 1 or word in self.stopwords:
                continue

            yield word

    def get_word_freq(self, text: str) -> Counter:
        return Counter(x for x in cut(text) if len(x) != 1 and x not in self.stopwords)


class JiebaSearchSplitter(WordSplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        self.stopwords = word_list

    def add_hotwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_hotwords_need_to_process(word_list)
        for word in word_list_to_add:
            add_word(word)

        self.hotwords = self.hotwords.union(word_list_to_add)

    def set_allowed_word_type(self, types_list: Set[str]) -> None:
        del types_list
        raise NotImplementedError

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            self.stopwords = {x.strip() for x in f.readlines()}

    def add_hotwords_file(self, file_name: str) -> None:
        load_userdict(file_name)

    def set_allowed_word_types_file(self, file_name: str) -> None:
        del file_name
        raise NotImplementedError

    def split(self, text: str) -> Generator[str, None, None]:
        for word in cut_for_search(text):
            if len(word) == 1 or word in self.stopwords:
                continue

            yield word

    def get_word_freq(self, text: str) -> Counter:
        return Counter(
            x for x in cut_for_search(text) if len(x) != 1 and x not in self.stopwords
        )


class JiebaPossegSplitter(WordSplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        self.stopwords = word_list

    def add_hotwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_hotwords_need_to_process(word_list)
        for word in word_list_to_add:
            add_word(word)

        self.hotwords = self.hotwords.union(word_list_to_add)

    def set_allowed_word_type(self, types: Set[str]) -> None:
        self.allowed_word_types = types

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            self.stopwords = {x.strip() for x in f.readlines()}

    def add_hotwords_file(self, file_name: str) -> None:
        load_userdict(file_name)

    def set_allowed_word_types_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            self.allowed_word_types = {x.strip() for x in f.readlines()}

    def split(self, text: str) -> Generator[str, None, None]:
        for pair in cut_poseg(text):
            if (
                len(pair.word) == 1
                or pair.flag not in self.allowed_word_types
                or pair.word in self.stopwords
            ):
                continue

            yield pair.word

    def get_word_freq(self, text: str) -> Counter:
        return Counter(
            pair.word
            for pair in cut_poseg(text)
            if len(pair.word) != 1
            and pair.flag in self.allowed_word_types
            and pair.word not in self.stopwords
        )
