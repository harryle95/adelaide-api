from urllib.parse import urlencode
from typing import Any
import requests
from requests import Response
import datetime
from copy import deepcopy

__all__ = (
    "Fetcher",
    "CAREER_PAYLOAD",
    "CAMPUS_PAYLOAD",
    "TERM_PAYLOAD",
    "COURSE_PAYLOAD",
    "SUBJECT_PAYLOAD",
    "BASE_URL",
)

BASE_URL = "https://courseplanner-api.adelaide.edu.au/api/course-planner-query/v1/"
YEAR = datetime.datetime.today().year
CAREER_PAYLOAD = {"target": "/system/CSP_ACAD_CAREER/queryx", "MaxRows": 99999}
CAMPUS_PAYLOAD = {"target": "/system/CAMPUS/queryx", "MaxRows": 99999}
SUBJECT_PAYLOAD = {
    "target": "/system/SUBJECTS_BY_YEAR/queryx",
    "virtual": "Y",
    "year_from": YEAR,
    "year_to": YEAR,
}
TERM_PAYLOAD = {
    "target": "/system/TERMS/queryx",
    "virtual": "Y",
    "year_from": YEAR,
    "year_to": YEAR,
}
COURSE_PAYLOAD = {
    "target": "/system/COURSE_SEARCH/queryx",
    "virtual": "Y",
    "year": YEAR,
}


class Fetcher:
    def __init__(self, payload: dict[str, Any], url: str = BASE_URL) -> None:
        self.url = url
        self.payload = payload
        self.params = self.encode_params()

    def encode_params(self, **kwargs: Any) -> str:
        payload = deepcopy(self.payload)
        if kwargs:
            payload.update(**kwargs)
        return urlencode(payload, safe="/")

    def __call__(
        self,
        **kwargs: Any,
    ) -> Response:
        if kwargs:
            response = requests.get(self.url, params=self.encode_params(**kwargs))
        else:
            response = requests.get(self.url, params=self.params)
        if response.status_code != 200:
            raise ConnectionError("Network error")
        return response
