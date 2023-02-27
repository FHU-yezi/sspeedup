from collections import Counter
from typing import Generator, Set

from jieba import add_word, cut, load_userdict
from jieba import logging as jieba_logging

from sspeedup.word_split._base import WordSplitter

jieba_logging.disable()

class JiebaSplitter(WordSplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_stopwords_need_to_process(word_list)
        self.stopwords = self.stopwords.union(word_list_to_add)

    def add_hotwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_hotwords_need_to_process(word_list)
        for word in word_list_to_add:
            add_word(word)

        self.hotwords = self.hotwords.union(word_list_to_add)

    def add_stopwords_file(self, file_name: str) -> None:
        load_userdict(file_name)

    def add_hotwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            word_list_to_add = self._get_hotwords_need_to_process(
                {x.strip() for x in f.readlines()},
            )

        self.hotwords = self.hotwords.union(word_list_to_add)

    def split(self, sentence: str) -> Generator[str, None, None]:
        for word in cut(sentence):
            if word in self.stopwords:
                continue

            yield word

    def get_word_freq(self, sentence: str) -> Counter:
        return Counter(x for x in cut(sentence) if x not in self.stopwords)
