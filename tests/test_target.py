from app_utils import find_windowless_python, validate_target


def test_validate_target_accepts_existing_file(tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("keep me", encoding="utf-8")

    normalized, error = validate_target(target)

    assert normalized == str(target.resolve())
    assert error is None


def test_validate_target_rejects_missing_and_directory(tmp_path):
    assert validate_target(None)[0] is None
    assert validate_target(tmp_path / "missing.txt")[0] is None
    assert validate_target(tmp_path)[0] is None


def test_find_windowless_python_prefers_pythonw(tmp_path):
    python = tmp_path / "python.exe"
    pythonw = tmp_path / "pythonw.exe"
    python.touch()
    pythonw.touch()

    assert find_windowless_python(python) == str(pythonw)


def test_find_windowless_python_falls_back_to_original(tmp_path):
    python = tmp_path / "python.exe"
    python.touch()

    assert find_windowless_python(python) == str(python)
