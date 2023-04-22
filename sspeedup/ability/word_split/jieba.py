from collections import Counter
from typing import Any, Dict, Generator, Set

from httpx import Client

from sspeedup.ability.exceptions import AbilityCallHTTPError, AbilityCallServiceError
from sspeedup.ability.word_split._base import AbilitySplitter

HTTPX_CLIENT = Client(timeout=20)


class AbilityJiebaSplitterV1(AbilitySplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_stopwords_need_to_process(word_list)
        self.stopwords = word_list_to_add

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            word_list_to_add = self._get_stopwords_need_to_process(
                {x.strip() for x in f.readlines()},
            )

        self.stopwords = self.stopwords.union(word_list_to_add)

    def set_allowed_word_type(self, types: Set[str]) -> None:
        del types
        raise NotImplementedError

    def set_allowed_word_types_file(self, file_name: str) -> None:
        del file_name
        raise NotImplementedError

    def split(self, text: str) -> Generator[str, None, None]:
        url = self.api_route + "/split/normal"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        yield from (
            x for x in response_json["data"]["splitted_text"] if x not in self.stopwords
        )

    def get_word_freq(self, text: str) -> Counter:
        url = self.api_route + "/freq/normal"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        return Counter(
            {
                key: value
                for key, value in response_json["data"]["word_freq"].items()
                if key not in self.stopwords
            }
        )


class AbilityJiebaSearchSplitterV1(AbilitySplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_stopwords_need_to_process(word_list)
        self.stopwords = word_list_to_add

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            word_list_to_add = self._get_stopwords_need_to_process(
                {x.strip() for x in f.readlines()},
            )

        self.stopwords = self.stopwords.union(word_list_to_add)

    def set_allowed_word_type(self, types: Set[str]) -> None:
        del types
        raise NotImplementedError

    def set_allowed_word_types_file(self, file_name: str) -> None:
        del file_name
        raise NotImplementedError

    def split(self, text: str) -> Generator[str, None, None]:
        url = self.api_route + "/split/search"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        yield from (
            x for x in response_json["data"]["splitted_text"] if x not in self.stopwords
        )

    def get_word_freq(self, text: str) -> Counter:
        url = self.api_route + "/freq/search"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        return Counter(
            {
                key: value
                for key, value in response_json["data"]["word_freq"].items()
                if key not in self.stopwords
            }
        )


class AbilityJiebaPossegSplitterV1(AbilitySplitter):
    def init(self) -> None:
        pass

    def add_stopwords(self, word_list: Set[str]) -> None:
        word_list_to_add: Set[str] = self._get_stopwords_need_to_process(word_list)
        self.stopwords = word_list_to_add

    def add_stopwords_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            word_list_to_add = self._get_stopwords_need_to_process(
                {x.strip() for x in f.readlines()},
            )

        self.stopwords = self.stopwords.union(word_list_to_add)

    def set_allowed_word_type(self, types: Set[str]) -> None:
        self.allowed_word_types = types

    def set_allowed_word_types_file(self, file_name: str) -> None:
        with open(file_name, encoding="utf-8") as f:
            self.allowed_word_types = {x.strip() for x in f.readlines()}

    def split(self, text: str) -> Generator[str, None, None]:
        url = self.api_route + "/split/posseg"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }
        if self.allowed_word_types:
            data["allowed_word_types"] = tuple(self.allowed_word_types)

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        yield from (
            x for x in response_json["data"]["splitted_text"] if x not in self.stopwords
        )

    def get_word_freq(self, text: str) -> Counter:
        url = self.api_route + "/freq/posseg"
        data: Dict[str, Any] = {
            "library": "jieba",
            "text": text,
        }
        if self.allowed_word_types:
            data["allowed_word_types"] = tuple(self.allowed_word_types)

        response = HTTPX_CLIENT.post(url=url, json=data)

        if response.status_code != 200:
            raise AbilityCallHTTPError(code=response.status_code)

        response_json = response.json()

        if not response_json["ok"]:
            raise AbilityCallServiceError(
                code=response_json["code"],
                message=response_json["message"],
            )

        return Counter(
            {
                key: value
                for key, value in response_json["data"]["word_freq"].items()
                if key not in self.stopwords
            }
        )
