#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  Lancement de Jarvis
#  Usage : ./run.sh
# ─────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"

# Activer le venv
if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
else
    echo "Erreur : venv introuvable ($VENV)"
    echo "Lance d'abord : python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Vérifications rapides
python3 -c "import vosk, sounddevice, llama_cpp" 2>/dev/null || {
    echo "Erreur : dépendances manquantes. Consulte INSTALL.md"
    exit 1
}

echo "Démarrage de Jarvis..."
cd "$SCRIPT_DIR"
exec python3 main.py "$@"
