import copy
from unittest.mock import patch, Mock

import pytest
import requests

import app as app_module
import cli

ORIGINAL_INVENTORY = copy.deepcopy(app_module.inventory)


@pytest.fixture
def client():
    app_module.inventory[:] = copy.deepcopy(ORIGINAL_INVENTORY)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()



def test_get_all(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_one(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_one_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_post_item(client):
    response = client.post("/inventory", json={"product_name": "Tea", "price": 2.5, "stock": 10})
    assert response.status_code == 201
    assert response.get_json()["id"] == 3
    assert len(app_module.inventory) == 3


def test_post_missing_name(client):
    response = client.post("/inventory", json={"price": 2})
    assert response.status_code == 400


def test_post_bad_price(client):
    response = client.post("/inventory", json={"product_name": "Tea", "price": "abc"})
    assert response.status_code == 400


def test_patch_item(client):
    response = client.patch("/inventory/1", json={"price": 9.99, "stock": 5})
    assert response.status_code == 200
    assert response.get_json()["price"] == 9.99
    assert app_module.inventory[0]["stock"] == 5


def test_patch_not_found(client):
    response = client.patch("/inventory/999", json={"price": 1})
    assert response.status_code == 404


def test_patch_bad_price(client):
    response = client.patch("/inventory/1", json={"price": "abc"})
    assert response.status_code == 400


def test_delete_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    assert len(app_module.inventory) == 1


def test_delete_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404



@patch("app.requests.get")
def test_lookup_by_barcode(mock_get, client):
    mock_get.return_value.json.return_value = {
        "status": 1,
        "product": {"product_name": "Test Juice", "brands": "TestBrand",
                    "ingredients_text": "Water, apple"},
    }
    response = client.get("/lookup?barcode=123")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Test Juice"


@patch("app.requests.get")
def test_lookup_by_name(mock_get, client):
    mock_get.return_value.json.return_value = {
        "products": [{"code": "123", "product_name": "Test Juice", "brands": "TestBrand"}]
    }
    response = client.get("/lookup?name=juice")
    assert response.status_code == 200
    assert response.get_json()["barcode"] == "123"


@patch("app.requests.get")
def test_lookup_not_found(mock_get, client):
    mock_get.return_value.json.return_value = {"status": 0}
    response = client.get("/lookup?barcode=000")
    assert response.status_code == 404


@patch("app.requests.get")
def test_lookup_api_down(mock_get, client):
    mock_get.side_effect = requests.exceptions.ConnectionError()
    response = client.get("/lookup?barcode=123")
    assert response.status_code == 502


def test_lookup_no_input(client):
    response = client.get("/lookup")
    assert response.status_code == 400


@patch("app.requests.get")
def test_import_item(mock_get, client):
    mock_get.return_value.json.return_value = {
        "status": 1,
        "product": {"product_name": "Test Juice", "brands": "TestBrand"},
    }
    response = client.post("/inventory/import", json={"barcode": "123", "price": 2, "stock": 7})
    assert response.status_code == 201
    assert len(app_module.inventory) == 3
    assert app_module.inventory[-1]["stock"] == 7


def test_import_no_barcode(client):
    response = client.post("/inventory/import", json={"price": 2})
    assert response.status_code == 400



def fake_response(data, status=200):
    response = Mock()
    response.status_code = status
    response.json.return_value = data
    return response


@patch("cli.requests.request")
def test_cli_list(mock_request, capsys):
    mock_request.return_value = fake_response(
        [{"id": 1, "product_name": "Milk", "brands": "Silk", "price": 3, "stock": 4}]
    )
    cli.main(["list"])
    assert "Milk" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_add(mock_request, capsys):
    mock_request.return_value = fake_response(
        {"id": 4, "product_name": "Tea", "brands": "", "price": 2, "stock": 1}, 201
    )
    cli.main(["add", "Tea", "--price", "2", "--stock", "1"])
    assert "Added" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_update(mock_request, capsys):
    mock_request.return_value = fake_response(
        {"id": 1, "product_name": "Milk", "brands": "Silk", "price": 5, "stock": 4}
    )
    cli.main(["update", "1", "--price", "5"])
    assert "Updated" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_delete(mock_request, capsys):
    mock_request.return_value = fake_response({"message": "Item deleted"})
    cli.main(["delete", "1"])
    assert "Item deleted" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_find(mock_request, capsys):
    mock_request.return_value = fake_response(
        {"barcode": "123", "product_name": "Test Juice", "brands": "TestBrand",
         "ingredients_text": "Water"}
    )
    cli.main(["find", "--barcode", "123"])
    assert "Test Juice" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_error_message(mock_request, capsys):
    mock_request.return_value = fake_response({"error": "Item not found"}, 404)
    cli.main(["view", "999"])
    assert "Item not found" in capsys.readouterr().out


@patch("cli.requests.request")
def test_cli_server_down(mock_request, capsys):
    mock_request.side_effect = requests.exceptions.ConnectionError()
    cli.main(["list"])
    assert "could not reach" in capsys.readouterr().out