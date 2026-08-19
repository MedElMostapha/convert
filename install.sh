#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PREFIX="${PREFIX:-/usr/local}"
DEST_DIR="$PREFIX/bin"

if [[ ! -f "$SCRIPT_DIR/convert" || ! -f "$SCRIPT_DIR/convert.py" ]]; then
    printf 'Erreur : convert et convert.py doivent être dans le même dossier.\n' >&2
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
install -m 755 "$SCRIPT_DIR/convert.py" "$DEST_DIR/convert.py"
install -m 755 "$SCRIPT_DIR/convert" "$DEST_DIR/convert"

printf 'convert installé dans %s/convert\n' "$DEST_DIR"
printf 'Test : convert --version\n'
