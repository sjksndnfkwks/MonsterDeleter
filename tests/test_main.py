import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt6")
from PyQt6.QtWidgets import QApplication

import main


def test_failed_spritesheet_load_clears_old_frames():
    app = QApplication.instance() or QApplication([])
    animator = main.SpriteAnimator()
    source = os.path.join(main.SPRITE_DIR, "走路动效_spritesheet.png")
    assert animator.load_spritesheet(source)
    assert animator.frames

    assert not animator.load_spritesheet(os.path.join(main.SPRITE_DIR, "missing.png"))
    assert animator.frames == []
    animator.close()
    app.processEvents()
