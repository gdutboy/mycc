import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def sample_target():
    return {"text": "发送", "bbox": [0, 0, 20, 10], "center": [10, 5]}


@pytest.fixture
def empty_context():
    return {}
