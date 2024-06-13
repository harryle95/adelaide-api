from thefuzz import process
from dataclasses import dataclass, fields
from typing import Any, ClassVar, Generic, TypeVar
from collections import UserDict


@dataclass
class Base:
    index: ClassVar[str]
    signature: ClassVar[set[str] | None] = None

    @classmethod
    def params(cls) -> set[str]:
        if cls.signature is None:
            cls.signature = {item["name"] for item in fields(cls)}
        return cls.signature

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "Base":
        field_dict = {key: item[key] for key in cls.params()}
        return cls(**field_dict)


T = TypeVar("T", bound=Base)


@dataclass
class Career(Base):
    FIELDVALUE: str
    XLATLONGNAME: str
    index: ClassVar[str] = "FIELDVALUE"


@dataclass
class Campus(Base):
    CAMPUS: str
    DESCR: str
    index: ClassVar[str] = "CAMPUS"


@dataclass
class Term(Base):
    TERM: str
    DESCR: str
    ACAD_YEAR: str
    CURRENT: bool
    index: ClassVar[str] = "TERM"


@dataclass
class Subject(Base):
    SUBJECT: str
    DESCR: str
    index: ClassVar[str] = "SUBJECT"


class DataCollection(UserDict, Generic[T]):
    def __init__(self, data: list[dict[str, Any]], data_class: type[T]) -> None:
        self._data = data
        self._parsed_data = None
        self.data_class = data_class

    def parse_data(self) -> dict[str, T]:
        index = self.data_class.index
        return {item[index]: self.data_class.from_dict(item) for item in self._data}

    @property
    def data(self) -> dict[str, T]:
        if self._parsed_data is None:
            self._parsed_data = self.parse_data()
        return self._parsed_data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: str) -> T | None:
        if key in self.data:
            return self.data[key]
        return process.extractOne(key, self.data)

    def __contains__(self, key: str) -> bool:
        return self.__getitem__(key) is not None
