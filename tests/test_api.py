import os
import sys

import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from httpx import AsyncClient

from index import app


@pytest.mark.asyncio
async def test_health_check(snapshot):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    snapshot.assert_match(response.json())


@pytest.mark.asyncio
async def test_health_check_alternative(snapshot):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    snapshot.assert_match(response.json())


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_askAPI(snapshot):
    payload = {"query": "志工平台是什麼?"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ask", json=payload)
    assert response.status_code == 200
    snapshot.assert_match(response.json())


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_askAPI_empty_query(snapshot):
    payload = {"query": ""}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ask", json=payload)
    assert response.status_code == 422
    snapshot.assert_match(response.json())


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_chatbot(snapshot):
    data = {"text": "志工平台是什麼?"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/chatbot", data=data)
    assert response.status_code == 200
    snapshot.assert_match(response.json())
