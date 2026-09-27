import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class FakeResponse:
    def __init__(self, js=None, text="", status=200, content=b"", headers=None, url="https://example.test/x"):
        self._js, self.text, self.status_code = js, text, status
        self.content, self.headers, self.url = content, headers or {}, url

    def json(self):
        return self._js


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    import utils.storage as storage

    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr("time.sleep", lambda *_: None)
    return tmp_path
