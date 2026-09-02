from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_interface_renders_without_runtime_exception():
    project_root = Path(__file__).resolve().parents[2]

    app = AppTest.from_file(str(project_root / "src/interface/app.py")).run(timeout=30)

    assert not app.exception
