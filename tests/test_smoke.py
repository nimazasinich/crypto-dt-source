def test_import_main_app():
    # Smoke-test: ensure the FastAPI app can be imported.
    from main import app  # noqa: F401

    assert app is not None
