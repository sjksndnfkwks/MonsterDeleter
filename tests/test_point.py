import sys

try:
    import uiautomation as auto
except ImportError:
    if __name__ == "__main__":
        raise SystemExit("uiautomation is not installed; run: pip install -r requirements-dev.txt")
    import pytest
    pytest.skip("uiautomation is not installed", allow_module_level=True)


def inspect_point(x, y):
    control = auto.ControlFromPoint(x, y)
    print(f"Control under {x}, {y}: {control.Name} ({control.ClassName})")
    
if __name__ == "__main__":
    if len(sys.argv) > 2:
        inspect_point(int(sys.argv[1]), int(sys.argv[2]))
