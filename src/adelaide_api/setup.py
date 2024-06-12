import dataclasses
import datetime
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests  # type: ignore
from pandas import DataFrame  # type: ignore

BASE_URL = "https://courseplanner-api.adelaide.edu.au/api/course-planner-query/v1/"
YEAR = datetime.datetime.today().year
MAPPING = {
    "ACAD_CAREER": "academic_career",
    "ACAD_CAREER_DESCR": "academic_career_description",
    "CAMPUS": "campus",
    "CATALOG_NBR": "catalogue_number",
    "CLASS_NBR": "class_number",
    "COURSE_ID": "course_id",
    "COURSE_OFFER_NBR": "course_offer_number",
    "COURSE_TITLE": "course_title",
    "SUBJECT": "subject",
    "TERM": "term",
    "TERM_DESCR": "term_description",
    "UNITS": "units",
    "YEAR": "year",
}
RESOURCE_DIR = Path(__file__).parent / "resources"


@dataclasses.dataclass
class Course:
    academic_career: str
    academic_career_description: str
    campus: str
    catalogue_number: str
    class_number: int
    course_id: str
    course_offer_number: int
    course_title: str
    subject: str
    term: str
    term_description: str
    units: int
    year: str


class Fetcher:
    def __init__(
        self,
        cache_period: int = 604800,
    ) -> None:
        self.cache_period = datetime.timedelta(seconds=cache_period)
        self.career = self.get_academic_career()
        self.campus = self.get_campus()
        self.subject = self.get_subject()
        self.term = self.get_term()

    def _validate_cache(self, path: Path) -> dict[str, str] | None:
        if not path.exists():
            return None
        with path.open(mode="r") as file:
            data_dict = json.load(file)
        ts = datetime.datetime.fromtimestamp(data_dict["time"])
        if datetime.datetime.now() - ts > self.cache_period:
            return None
        return data_dict["data"]

    def _save_response(self, path: Path, data: dict[str, str]) -> None:
        json_data: dict[str, Any] = {}
        json_data["data"] = data
        json_data["time"] = datetime.datetime.now().timestamp()
        with path.open(mode="w") as file:
            json.dump(json_data, file)

    def _make_request(
        self,
        payload: dict[str, Any],
    ) -> list[dict]:
        param_str = urlencode(payload, safe="/")
        response = requests.get(BASE_URL, params=param_str)
        if response.status_code != 200:
            raise ConnectionError("Network error")
        try:
            return response.json()["data"]["query"]["rows"]
        except KeyError as e:
            raise KeyError("Invalid schema") from e

    def _extract_response(
        self, payload: dict[str, Any], key: str, value: str
    ) -> dict[str, str]:
        response = self._make_request(payload)
        return {item[key]: item[value] for item in response}

    def read_cache_or_make_request(
        self, payload: dict[str, Any], path: Path, key: str, value: str
    ) -> dict[str, str]:
        data = self._validate_cache(path)
        if data:
            return data
        response = self._extract_response(payload, key, value)
        self._save_response(path, response)
        return response

    def get_academic_career(self) -> dict[str, str]:
        return self.read_cache_or_make_request(
            {"target": "/system/CSP_ACAD_CAREER/queryx", "MaxRows": 99999},
            RESOURCE_DIR / "CSP_ACAD_CAREER.json",
            "FIELDVALUE",
            "XLATLONGNAME",
        )

    def get_campus(self) -> dict[str, str]:
        return self.read_cache_or_make_request(
            {"target": "/system/CAMPUS/queryx", "MaxRows": 99999},
            RESOURCE_DIR / "CAMPUS.json",
            "CAMPUS",
            "DESCR",
        )

    def get_subject(self) -> dict[str, str]:
        return self.read_cache_or_make_request(
            {
                "target": "/system/SUBJECTS_BY_YEAR/queryx",
                "virtual": "Y",
                "year_from": YEAR,
                "year_to": YEAR,
            },
            RESOURCE_DIR / "SUBJECT.json",
            "SUBJECT",
            "DESCR",
        )

    def get_term(self) -> dict[str, str]:
        return self.read_cache_or_make_request(
            {
                "target": "/system/TERMS/queryx",
                "virtual": "Y",
                "year_from": YEAR,
                "year_to": YEAR,
            },
            RESOURCE_DIR / "TERM.json",
            "TERM",
            "DESCR",
        )

    def get_course(
        self,
        course_title: str | None = None,
        campus: str | None = None,
        year: str | int = YEAR,
        subject: str | None = None,
        catalogue_number: str | int | None = None,
        term: str | int | None = None,
        career: str | None = None,
        page_number: int = 1,
        page_size: int = 9999,
    ) -> DataFrame:
        payload = {"target": "/system/COURSE_SEARCH/queryx", "virtual": "Y"}
        if course_title:
            payload["course_title"] = course_title
        if campus:
            if campus not in self.campus:
                raise ValueError("Invalid campus: ", campus)
            payload["campus"] = campus
        if subject:
            if subject not in self.subject:
                raise ValueError("Invalid subject: ", subject)
            payload["subject"] = subject
        if catalogue_number:
            payload["catalog_nbr"] = str(catalogue_number)
        if term:
            if str(term) not in self.term:
                raise ValueError("Invalid term: ", term)
            payload["term"] = str(term)
        if career:
            if career not in self.career:
                raise ValueError("Invalid career: ", career)
            payload["career"] = career
        payload["year"] = str(year)
        payload["pagenbr"] = str(page_number)
        payload["pagesize"] = str(page_size)
        response = self._make_request(payload)
        return DataFrame.from_records(response).rename(columns=MAPPING)


if __name__ == "__main__":
    fetcher = Fetcher()
    print("End")
