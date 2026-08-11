import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_search_empty_query():
    res = client.post('/products/search', json={"query": "  "})
    assert res.status_code == 422 or res.status_code == 400


def test_search_valid():
    res = client.post('/products/search', json={"query": "tornillo 1/2"})
    assert res.status_code == 200
    j = res.json()
    assert 'results' in j
    assert len(j['results']) <= 5


def test_customer_not_found():
    res = client.get('/customers/NOPE/suggested-sale')
    assert res.status_code == 404


def test_customer_suggested():
    res = client.get('/customers/C001/suggested-sale')
    assert res.status_code == 200
    j = res.json()
    assert isinstance(j, list)
