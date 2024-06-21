def test_import() -> None:
    import jobdb

    assert jobdb
    assert jobdb.version
