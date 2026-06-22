from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from aioresponses import aioresponses

from desslyhub_api.client import DesslyHubClient

BASE_URL = "https://desslyhub.com"


@pytest.fixture
def mock_api() -> Iterator[aioresponses]:
    """Перехватывает реальные HTTP-запросы aiohttp на время теста."""
    with aioresponses() as mocked:
        yield mocked


@pytest_asyncio.fixture
async def client() -> AsyncIterator[DesslyHubClient]:
    """Создаёт запущенный клиент DesslyHub и закрывает его после теста."""
    async with DesslyHubClient("test-key", "test-secret", base_url=BASE_URL) as instance:
        yield instance
