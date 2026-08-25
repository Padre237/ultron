"""
Synthèse vocale via Piper.
- Pipe direct stdout → aplay (sans fichier temporaire) → -1s de latence
- Cache audio RAM pour les phrases fixes → ~50ms au lieu de 800ms
- Pré-génération du cache au démarrage
"""

import subprocess
import os
import sys
import io
import threading
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger("jarvis.tts")

# ── Résolution du binaire Piper ───────────────────────────────────────────────
def _find_piper() -> str:
    venv_piper = os.path.join(os.path.dirname(sys.executable), "piper")
    if os.path.isfile(venv_piper):
        return venv_piper
    project_venv = os.path.join(config.BASE_DIR, "venv", "bin", "piper")
    if os.path.isfile(project_venv):
        return project_venv
    return "piper"

PIPER_BIN = _find_piper()

# ── Cache audio en RAM ────────────────────────────────────────────────────────
_CACHE_PHRASES = [
    "Oui.",
    "Je vous écoute.",
    "Je n'ai pas entendu.",
    "Commande non reconnue. Dites commande suivi d'un numéro.",
    "Jarvis est prêt. Dites Jarvis pour m'activer.",
    "Au revoir.",
    "Action annulée.",
    "Confirmé.",
    "Pas de réponse. Action annulée par sécurité.",
    "Désolé, je n'ai pas de réponse.",
]

_audio_cache: dict[str, bytes] = {}
_cache_lock = threading.Lock()


def _generate_wav_bytes(text: str) -> bytes | None:
    """Génère un WAV en mémoire via Piper (pas de fichier temp)."""
    if not os.path.exists(config.PIPER_MODEL_PATH):
        logger.error(f"Modèle Piper introuvable : {config.PIPER_MODEL_PATH}")
        return None

    try:
        proc = subprocess.run(
            [
                PIPER_BIN,
                "--model",       config.PIPER_MODEL_PATH,
                "--config",      config.PIPER_CONFIG_PATH,
                "--output-raw",  # sortie PCM brut sur stdout
            ],
            input=text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            logger.error(f"Piper erreur : {proc.stderr.decode()}")
            return None
        return proc.stdout  # PCM brut 16-bit 22050Hz mono
    except Exception as e:
        logger.error(f"Piper exception : {e}")
        return None


def _play_raw(pcm_bytes: bytes):
    """Joue des bytes PCM brut via aplay."""
    try:
        subprocess.run(
            ["aplay", "-q", "-r", "22050", "-f", "S16_LE", "-c", "1", "-"],
            input=pcm_bytes,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        logger.error(f"aplay erreur : {e}")


def build_cache():
    """
    Pré-génère les phrases fixes au démarrage et les stocke en RAM.
    Appelé dans un thread séparé pour ne pas bloquer le démarrage.
    """
    logger.info("Pré-génération du cache audio...")
    for phrase in _CACHE_PHRASES:
        pcm = _generate_wav_bytes(phrase)
        if pcm:
            with _cache_lock:
                _audio_cache[phrase] = pcm
    logger.info(f"Cache audio prêt — {len(_audio_cache)} phrases.")


def speak(text: str):
    """
    Synthétise et joue le texte.
    - Cache hit  → lecture immédiate (~50ms)
    - Cache miss → génération Piper pipe direct (~800ms)
    """
    if not text or not text.strip():
        return

    text = text.strip()
    logger.debug(f"speak: {text}")

    # Vérifier le cache
    with _cache_lock:
        cached = _audio_cache.get(text)

    if cached:
        _play_raw(cached)
        return

    # Génération à la volée (pipe direct, pas de fichier temp)
    pcm = _generate_wav_bytes(text)
    if pcm:
        _play_raw(pcm)
    else:
        logger.warning(f"Impossible de synthétiser : {text}")


if __name__ == "__main__":
    build_cache()
    speak("Bonjour, je suis Jarvis, votre assistant personnel.")
