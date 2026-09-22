import importlib
import importlib.util
from pathlib import Path
import pytest


def test_static_assets_and_spa_fallback(client, monkeypatch, tmp_path):
    main = importlib.import_module("app.main")
    monkeypatch.setattr(main, "frontend", tmp_path)
    (tmp_path / "index.html").write_text('<script type="module" src="/assets/app.js"></script>')
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app.js").write_text('console.log("loaded")')
    for route in ("/", "/renders"):
        response = client.get(route)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-cache"
        assert response.headers["content-type"].startswith("text/html")
    script = client.get("/assets/app.js")
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    assert "immutable" in script.headers["cache-control"]
    for route in ("/assets/missing.js", "/missing.css", "/api/v1/missing"):
        response = client.get(route)
        assert response.status_code == 404
        assert "text/html" not in response.headers["content-type"]


def test_deploy_rejects_stale_html(tmp_path):
    path = Path(__file__).resolve().parents[2] / "scripts/verify_frontend.py"
    spec = importlib.util.spec_from_file_location("verify_frontend", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "index.html").write_text('<script type="module" src="/assets/old.js"></script>')
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/new.js").write_text("export default 1")
    with pytest.raises(ValueError, match="old.js"):
        module.verify(tmp_path)
    (tmp_path / "index.html").write_text('<script type="module" src="/assets/new.js"></script>')
    module.verify(tmp_path)
