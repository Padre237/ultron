"""
Jarvis — Point d'entrée principal.
- Interface PyQt5 dans le thread principal
- Boucle vocale dans un thread daemon
- LLM llama-cpp-python avec streaming
- TTS Piper pipe direct + cache audio
- STT Vosk avec vocab restreint pour les commandes
- Logs structurés dans logs/jarvis.log
"""

import sys
import os
import threading
import logging
import logging.handlers

# ── Chemin racine ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

# ── Logs ──────────────────────────────────────────────────────────────────────
os.makedirs(config.LOGS_DIR, exist_ok=True)

_log_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)

# Console
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(_log_formatter)

# Fichier avec rotation (5 Mo × 3 fichiers)
_file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(config.LOGS_DIR, "jarvis.log"),
    maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_log_formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[_console_handler, _file_handler])
logger = logging.getLogger("jarvis.main")

# ── Imports après config des logs ─────────────────────────────────────────────
from interface.orb_window import start_orb, run_event_loop
import vosk
from voice.wakeword import WakeWordDetector
from voice.stt import STT
from brain.llm import LLM
from tts.speak import speak, build_cache
from commands.executor import execute_command

# ── Référence globale à la fenêtre orbe ──────────────────────────────────────
_orb = None

def set_ui(state: str, text: str = ""):
    """Change l'état de l'orbe (thread-safe)."""
    if _orb:
        _orb.change_state(state, text)


# ── Boucle Jarvis (thread daemon) ─────────────────────────────────────────────
def jarvis_loop():
    logger.info("Démarrage de la boucle Jarvis")

    # ── Pré-générer le cache audio (en tâche de fond) ─────────────────
    cache_thread = threading.Thread(target=build_cache, daemon=True, name="tts-cache")
    cache_thread.start()

    # ── Charger Vosk ──────────────────────────────────────────────────
    logger.info(f"Chargement Vosk : {config.VOSK_MODEL_PATH}")
    vosk_model = vosk.Model(config.VOSK_MODEL_PATH)
    detector   = WakeWordDetector(vosk_model, wakeword=config.ASSISTANT_NAME)
    stt        = STT(vosk_model)

    # ── Charger LLM ───────────────────────────────────────────────────
    llm = LLM()
    llm.load()

    set_ui("rest")
    speak("Jarvis est prêt. Dites Jarvis pour m'activer.")
    logger.info("Jarvis prêt.")

    while True:
        try:
            # ── Veille ────────────────────────────────────────────────
            set_ui("rest")
            detector.wait_for_wakeword()

            # ── Écoute commande ───────────────────────────────────────
            set_ui("listening")
            speak("Oui.")

            # Essai 1 : vocab restreint (rapide)
            command_text = stt.listen(mode="command")
            logger.info(f"STT (command): '{command_text}'")

            if not command_text:
                speak("Je n'ai pas entendu.")
                continue

            # ── Traitement ────────────────────────────────────────────
            set_ui("working", command_text)
            response = execute_command(command_text)

            # Signal spécial : effacer l'historique LLM
            if response == "__clear_history__":
                llm.clear_history()
                response = "Historique effacé."

            if response is None:
                # Pas une commande → écouter en mode libre si besoin
                # (le texte command peut être incomplet en vocab restreint)
                logger.info("Commande non reconnue → mode libre")
                set_ui("listening", "Mode conversation...")
                command_text_free = stt.listen(mode="free")
                if command_text_free:
                    command_text = command_text_free
                    logger.info(f"STT (free): '{command_text}'")
                    response = execute_command(command_text)

            if response is None:
                # Toujours rien → LLM
                logger.info("→ LLM streaming")
                set_ui("working", command_text)

                def _speak_sentence(sentence):
                    set_ui("speaking", sentence)
                    speak(sentence)

                llm.ask_stream(command_text, on_sentence=_speak_sentence)
                set_ui("rest")
            else:
                # Commande reconnue
                set_ui("speaking", response)
                logger.info(f"Réponse: {response}")
                speak(response)
                set_ui("rest")

        except Exception as e:
            logger.error(f"Erreur boucle : {e}", exc_info=True)
            set_ui("rest")
            # Watchdog : on continue sans crash
            import time; time.sleep(1)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global _orb

    logger.info("=" * 50)
    logger.info("JARVIS démarrage")
    logger.info("=" * 50)

    print("Démarrage de Jarvis — fenêtre graphique en cours...\n")

    # Fenêtre PyQt5 dans le thread principal
    _orb = start_orb()

    # Boucle vocale dans un thread daemon
    t = threading.Thread(target=jarvis_loop, daemon=True, name="jarvis-core")
    t.start()

    # Boucle Qt — bloque jusqu'à fermeture
    try:
        run_event_loop()
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur.")
        speak("Au revoir.")


if __name__ == "__main__":
    main()
