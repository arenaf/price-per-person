import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app=app)

message = "Incorrect data entry. All fields must be filled in and in numerical format."


@pytest.fixture()
def url_price():
    url_price = "/price"
    return url_price


# Test: returns the expected result
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Calculate the total amount to be paid per person on the route: /price"
    }


def test_get_price_per_person(url_price):
    response = client.post(url_price, json={"price": 199.99, "people": 4, "tip": 1.5})
    assert response.status_code == 200
    assert response.json() == {"result": "Total price per person: 50.75"}


# Test: lower than expected values
@pytest.mark.parametrize(
    "price, people, tip, expected_code, expected_output",
    [
        (
            -1,
            4,
            1.5,
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": "price",
                        "msg": "Input should be greater than or equal to 0",
                    }
                ],
            },
        ),
        (
            199.99,
            -1,
            1.5,
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": "people",
                        "msg": "Input should be greater than or equal to 1",
                    }
                ],
            },
        ),
        (
            199.99,
            4,
            -1,
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": "tip",
                        "msg": "Input should be greater than or equal to 0",
                    }
                ],
            },
        ),
    ],
)
def test_check_lower_value(
    url_price, price, people, tip, expected_code, expected_output
):
    response = client.post(
        url_price, json={"price": price, "people": people, "tip": tip}
    )
    assert response.status_code == expected_code
    assert response.json() == expected_output


# Test: invalid value string
@pytest.mark.parametrize(
    "price, people, tip, expected_code, expected_output",
    [
        (
            "fifteen",
            4,
            1.5,
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "float_parsing",
                        "loc": "price",
                        "msg": "Input should be a valid number, unable to parse string as a number",
                    }
                ],
            },
        ),
        (
            199.99,
            "four",
            1.5,
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "int_parsing",
                        "loc": "people",
                        "msg": "Input should be a valid integer, unable to parse string as an integer",
                    }
                ],
            },
        ),
        (
            199.99,
            4,
            "no tip",
            422,
            {
                "Error": message,
                "detail": [
                    {
                        "type": "float_parsing",
                        "loc": "tip",
                        "msg": "Input should be a valid number, unable to parse string as a number",
                    }
                ],
            },
        ),
    ],
)
def test_check_invalid_value_str(
    url_price, price, people, tip, expected_code, expected_output
):
    response = client.post(
        url_price, json={"price": price, "people": people, "tip": tip}
    )
    assert response.status_code == expected_code
    assert response.json() == expected_output


# Test: people float value instead of int
def test_input_people_as_float(url_price):
    response = client.post(url_price, json={"price": 60, "people": 2.5, "tip": 1.5})
    assert response.status_code == 422
    assert response.json() == {
        "Error": message,
        "detail": [
            {
                "type": "int_from_float",
                "loc": "people",
                "msg": "Input should be a valid integer, got a number with a fractional part",
            }
        ],
    }


# Test: removing a field
def test_price_data_entry_field_missing(url_price):
    response = client.post(url_price, json={"people": 2, "tip": 0.5})
    assert response.status_code == 422
    assert response.json() == {
        "Error": message,
        "detail": [{"type": "missing", "loc": "price", "msg": "Field required"}],
    }


def test_people_data_entry_field_missing(url_price):
    response = client.post(url_price, json={"price": 60, "tip": 1.5})
    assert response.status_code == 422
    assert response.json() == {
        "Error": message,
        "detail": [{"type": "missing", "loc": "people", "msg": "Field required"}],
    }


def test_tip_data_entry_field_missing(url_price):
    response = client.post(url_price, json={"price": 60, "people": 2})
    assert response.status_code == 422, response.text
    assert response.json() == {
        "Error": message,
        "detail": [{"type": "missing", "loc": "tip", "msg": "Field required"}],
    }
