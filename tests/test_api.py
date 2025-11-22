# -*- coding: utf-8 -*-
import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("data")
    db_path = db_dir / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from main import app  # Importa después de configurar la URL

    with TestClient(app) as test_client:
        yield test_client

    if db_path.exists():
        db_path.unlink()
    if db_dir.exists():
        db_dir.rmdir()


def test_create_auto_and_get_with_sales(client: TestClient):
    auto_payload = {
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2022,
        "numero_chasis": "TOYTEST001",
    }
    resp = client.post("/autos", json=auto_payload)
    assert resp.status_code == 201
    auto = resp.json()
    assert auto["numero_chasis"] == auto_payload["numero_chasis"]

    auto_id = auto["id"]
    resp = client.get(f"/autos/{auto_id}/with-ventas")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == auto_id
    assert data["ventas"] == []


def test_create_venta_and_fetch(client: TestClient):
    auto_payload = {
        "marca": "Ford",
        "modelo": "Focus",
        "año": 2021,
        "numero_chasis": "FOCUSTEST002",
    }
    auto_resp = client.post("/autos", json=auto_payload)
    assert auto_resp.status_code == 201
    auto_id = auto_resp.json()["id"]

    venta_payload = {
        "nombre_comprador": "Juan Perez",
        "precio": 19500.50,
        "auto_id": auto_id,
        "fecha_venta": datetime.utcnow().isoformat(),
    }
    resp = client.post("/ventas", json=venta_payload)
    assert resp.status_code == 201
    venta = resp.json()
    assert venta["auto_id"] == auto_id

    venta_id = venta["id"]
    resp = client.get(f"/ventas/{venta_id}/with-auto")
    assert resp.status_code == 200
    data = resp.json()
    assert data["auto"]["id"] == auto_id
    assert data["precio"] == pytest.approx(venta_payload["precio"])


def test_create_venta_invalid_auto(client: TestClient):
    venta_payload = {
        "nombre_comprador": "Comprador X",
        "precio": 15000,
        "auto_id": 9999,
        "fecha_venta": datetime.utcnow().isoformat(),
    }
    resp = client.post("/ventas", json=venta_payload)
    assert resp.status_code == 404
