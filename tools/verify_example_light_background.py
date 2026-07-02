import argparse
import os
import sys
from pathlib import Path


def _repo_root():
    return Path(__file__).resolve().parents[1]


def _ensure_import_path():
    root = _repo_root()
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "LqRibbon" / "example"))


def _color_text(color):
    return f"{color.name()} lightness={color.lightness()}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", default="")
    args = parser.parse_args()

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    _ensure_import_path()

    from PySide6.QtWidgets import QApplication

    from LqRibbon import LqStyle
    from LqRibbon.example.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(1200, 700)
    window.show()
    app.processEvents()

    pixmap = window.grab()
    if args.preview:
        pixmap.save(args.preview)

    image = pixmap.toImage()
    ribbon = window.ribbon_bar
    ribbon_rect = ribbon.geometry()
    sample_points = [
        (
            ribbon_rect.right() - 80,
            ribbon_rect.top() + LqStyle.TAB_BAR_HEIGHT + 12,
        ),
        (
            ribbon_rect.right() - 80,
            ribbon_rect.bottom() - 12,
        ),
    ]

    failures = []
    for point in sample_points:
        color = image.pixelColor(*point)
        print(f"{point}: {_color_text(color)}")
        if color.lightness() <= 180:
            failures.append((point, color))

    window.close()
    if failures:
        details = ", ".join(
            f"{point}={_color_text(color)}" for point, color in failures
        )
        raise AssertionError(f"Ribbon empty background is too dark: {details}")

    print("PASS example ribbon empty background remains light")


if __name__ == "__main__":
    main()
