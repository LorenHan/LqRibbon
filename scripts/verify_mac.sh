#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
PREVIEW_PATH="${PREVIEW_PATH:-/tmp/lqribbon_mac_preview.png}"
CPP_BUILD_DIR="${CPP_BUILD_DIR:-/tmp/lqribbon_cpp_mac_build}"

echo "== macOS verification for LqRibbon =="
echo "Repository: $ROOT_DIR"
echo "Python: $($PYTHON_BIN --version)"

echo
echo "== Python dependency check =="
$PYTHON_BIN - <<'PY'
import PySide6
print(f"PySide6: {PySide6.__version__}")
PY

echo
echo "== Python import check =="
$PYTHON_BIN - <<'PY'
from LqRibbon import RibbonMainWindow, RibbonStyle
print("LqRibbon import: ok")
print(f"Default style enum: {RibbonStyle.Office2016Blue}")
print(f"Main window class: {RibbonMainWindow.__name__}")
PY

echo
echo "== Python compile check =="
$PYTHON_BIN -m compileall LqRibbon LqRibbonPy tests

echo
echo "== Python tests =="
QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}" $PYTHON_BIN -m pytest tests

echo
echo "== Python demo preview =="
rm -f "$PREVIEW_PATH"
QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}" \
  $PYTHON_BIN LqRibbonPy/example/main.py --grab-preview "$PREVIEW_PATH"
test -s "$PREVIEW_PATH"
echo "Preview written: $PREVIEW_PATH"

echo
echo "== C++/Qt qmake build =="
QMAKE_BIN="${QMAKE_BIN:-}"
if [[ -z "$QMAKE_BIN" ]]; then
  for candidate in \
    qmake6 \
    qmake \
    "$HOME/Qt/6.11.0/macos/bin/qmake6" \
    "$HOME/Qt/6.11.0/macos/bin/qmake"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      QMAKE_BIN="$(command -v "$candidate")"
      break
    fi
    if [[ -x "$candidate" ]]; then
      QMAKE_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$QMAKE_BIN" ]]; then
  echo "qmake not found; skipping C++/Qt build."
else
  echo "qmake: $QMAKE_BIN"
  rm -rf "$CPP_BUILD_DIR"
  mkdir -p "$CPP_BUILD_DIR"
  qmake_args=("$ROOT_DIR/LqRibbonCPP/Example/LqRibbonExample.pro")
  if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    qmake_args+=("QMAKE_CXXFLAGS+=-include arm_acle.h")
  fi
  (
    cd "$CPP_BUILD_DIR"
    "$QMAKE_BIN" "${qmake_args[@]}"
    make -j"$(sysctl -n hw.ncpu)"
  )
  echo "C++ build directory: $CPP_BUILD_DIR"
fi

echo
echo "macOS verification completed."
