class AbilityCallHTTPError(Exception):
    def __init__(self, code: int, message: str = "") -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"


class AbilityCallServiceError(Exception):
    def __init__(self, code: int, message: str = "") -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code}, message={self.message})"
