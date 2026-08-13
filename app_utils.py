import os
from pathlib import Path


def validate_target(target):
    if not target:
        return None, "没有指定目标文件。"
    try:
        normalized = os.path.abspath(os.fspath(target))
    except TypeError:
        return None, "目标文件路径无效。"
    if not os.path.isfile(normalized):
        return None, f"目标文件不存在或不是普通文件：\n{normalized}"
    return normalized, None


def find_windowless_python(executable):
    """Return a sibling pythonw executable when one is available on Windows."""
    executable = os.path.abspath(os.fspath(executable))
    path = Path(executable)
    name = path.name.lower()
    if name.startswith("pythonw"):
        return executable
    if name.startswith("python") and name.endswith(".exe"):
        candidates = [
            path.with_name("pythonw" + path.name[len("python"):]),
            path.with_name("pythonw.exe"),
        ]
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    return executable
