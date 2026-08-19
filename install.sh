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
install -m 755 "$SCRIPT_DIR/convert" "$DEST_DIR/numconvert"

printf 'convert installé dans %s/convert\n' "$DEST_DIR"
printf 'Alias sans conflit : %s/numconvert\n' "$DEST_DIR"

resolved_convert="$(type -P convert 2>/dev/null || true)"
if [[ "$resolved_convert" != "$DEST_DIR/convert" ]]; then
    printf 'Attention : convert est résolu vers %s.\n' "${resolved_convert:-une commande inconnue}"
    printf 'Utilisez numconvert ou %s/convert.\n' "$DEST_DIR"
    printf 'Dans Bash, `hash -r` peut être nécessaire après l’installation.\n'
fi

printf 'Test : numconvert --version\n'
