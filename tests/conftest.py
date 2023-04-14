from pathlib import Path

import pytest


@pytest.fixture
def resources():
    return Path(__file__).parent / "resources"


@pytest.fixture
def out_put(tmp_path):
    o = tmp_path / "out"
    o.mkdir(exist_ok=True)
    return o
