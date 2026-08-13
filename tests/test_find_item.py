try:
    import uiautomation as auto
except ImportError:
    if __name__ == "__main__":
        raise SystemExit("uiautomation is not installed; run: pip install -r requirements-dev.txt")
    import pytest
    pytest.skip("uiautomation is not installed", allow_module_level=True)


def inspect_first_item():
    auto.SetGlobalSearchTimeout(3.0)
    # Search for anything on the desktop
    desktop = auto.GetRootControl()
    
    # Let's just find the first ListItemControl and print its name
    for item, depth in auto.WalkTree(desktop, getChildren=lambda c: c.GetChildren(), maxDepth=5):
        if isinstance(item, auto.ListItemControl):
            print(f"Found item: {item.Name}, Rect: {item.BoundingRectangle}")
            break

if __name__ == "__main__":
    inspect_first_item()
