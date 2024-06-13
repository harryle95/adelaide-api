import pytest
import responses
from src.adelaide_api.fetch import Fetcher, CAMPUS_PAYLOAD, BASE_URL
from typing import Generator, Any


@pytest.fixture
def campus_response() -> dict:
    return {
        "status": "success",
        "data": {
            "query": {
                "numrows": 4,
                "queryname=": "CSP_ACAD_CAREER",
                "rows": [
                    {
                        "attr:rownumber": 1,
                        "FIELDVALUE": "NAWD",
                        "XLATLONGNAME": "Non Award",
                    },
                    {
                        "attr:rownumber": 2,
                        "FIELDVALUE": "PGCW",
                        "XLATLONGNAME": "Postgraduate Coursework",
                    },
                    {
                        "attr:rownumber": 3,
                        "FIELDVALUE": "UGRD",
                        "XLATLONGNAME": "Undergraduate",
                    },
                    {
                        "attr:rownumber": 4,
                        "FIELDVALUE": "ULAW",
                        "XLATLONGNAME": "Undergraduate Law (LLB)",
                    },
                ],
            }
        },
    }


@pytest.fixture()
def campus_fetcher() -> Fetcher:
    return Fetcher(CAMPUS_PAYLOAD, BASE_URL)


@pytest.fixture()
def mock_campus_response_success(
    campus_fetcher: Fetcher, campus_response: dict
) -> Generator[Any, None, None]:
    with responses.RequestsMock() as response_mock:
        response_mock.add(
            responses.GET,
            BASE_URL + "?" + campus_fetcher.params,
            status=200,
            content_type="application/json",
            json=campus_response,
        )
        yield

@pytest.fixture()
def additional_kwargs()->dict[str, str]:
    return {"path": "path/to/something", "value": "random_value"}

@pytest.fixture()
def mock_campus_additional_kwargs_success(
    campus_fetcher: Fetcher, campus_response: dict
) -> Generator[Any, None, None]:
    with responses.RequestsMock() as response_mock:
        response_mock.add(
            responses.GET,
            BASE_URL + "?" + campus_fetcher.params + "",
            status=200,
            content_type="application/json",
            json=campus_response,
        )
        yield


@pytest.fixture()
def mock_campus_response_failure(
    campus_fetcher: Fetcher,
) -> Generator[Any, None, None]:
    with responses.RequestsMock() as response_mock:
        response_mock.add(
            responses.GET,
            BASE_URL + "?" + campus_fetcher.params,
            status=404,
            content_type="application/json",
        )
        yield


def test_request_success(
    campus_fetcher: Fetcher, campus_response: dict, mock_campus_response_success: None
) -> None:
    fetch_response = campus_fetcher()
    assert fetch_response.status_code == 200
    assert fetch_response.json() == campus_response


def test_request_fails(
    campus_fetcher: Fetcher, mock_campus_response_failure: None
) -> None:
    with pytest.raises(ConnectionError):
        campus_fetcher()


def test_call_with_additional_kwargs(campus_fetcher: Fetcher) -> None:
    args = {"first": 10, "second": "path/to/sth"}
    param_str = campus_fetcher.encode_params(**args)
    assert param_str == campus_fetcher.params + "&first=10&second=path/to/sth"
