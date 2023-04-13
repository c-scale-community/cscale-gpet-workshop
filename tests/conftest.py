from pathlib import Path

import pytest


@pytest.fixture
def resources():
    return Path(__file__).parent / "resources"
