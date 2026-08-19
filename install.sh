#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PREFIX="${PREFIX:-/usr/local}"
DEST_DIR="$PREFIX/bin"

if [[ ! -f "$SCRIPT_DIR/numconvert" || ! -f "$SCRIPT_DIR/numconvert.py" ]]; then
    printf 'Erreur : numconvert et numconvert.py doivent être dans le même dossier.\n' >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    printf 'Erreur : python3 est requis mais introuvable.\n' >&2
    exit 1
fi

# Elevate only for the default system-wide installation.
if [[ "$PREFIX" == "/usr/local" && "$EUID" -ne 0 ]]; then
    if ! command -v sudo >/dev/null 2>&1; then
        printf 'Erreur : sudo est requis pour installer dans %s.\n' "$DEST_DIR" >&2
        printf 'Alternative : PREFIX="$HOME/.local" ./install.sh\n' >&2
        exit 1
    fi
    exec sudo -- "$0" "$@"
fi

install -d "$DEST_DIR"
# Remove files created by older versions without touching an unrelated
# ImageMagick or system command named convert.
legacy_launcher="$DEST_DIR/convert"
if [[ -f "$legacy_launcher" ]] && grep -Fq 'exec python3 "$SCRIPT_DIR/convert.py" "$@"' "$legacy_launcher"; then
    rm -f "$legacy_launcher"
fi
legacy_implementation="$DEST_DIR/convert.py"
if [[ -f "$legacy_implementation" ]] \
    && grep -Fq 'A small, dependency-free command for common numeric conversions.' "$legacy_implementation" \
    && grep -Fq 'class ConversionError' "$legacy_implementation"; then
    rm -f "$legacy_implementation"
fi

install -m 755 "$SCRIPT_DIR/numconvert.py" "$DEST_DIR/numconvert.py"
install -m 755 "$SCRIPT_DIR/numconvert" "$DEST_DIR/numconvert"

printf 'numconvert installé dans %s/numconvert\n' "$DEST_DIR"
printf 'Test : numconvert --version\n'
