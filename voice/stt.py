"""
Reconnaissance vocale Vosk avec deux modes :
- Mode commandes (vocab restreint) : rapide, précis, ~100ms
- Mode libre                       : vocab complet, ~200-300ms
Timeout adaptatif selon le mode.
"""

import sounddevice as sd
import vosk
import queue
import sys
import os
import json
import time
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger("jarvis.stt")

# ── Vocabulaire restreint commandes ───────────────────────────────────────────
# Tous les mots que Jarvis doit reconnaître en mode commande
_COMMAND_VOCAB = json.dumps([
    # Déclencheurs commande numérotée
    "commande", "command", "komande",
    # Nombres 1-17
    "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit",
    "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze",
    "seize", "dix sept",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17",
    # Applications
    "firefox", "fichiers", "terminal", "vlc", "parametres",
    "navigateur", "lecteur", "konsole", "dolphin",
    # Volume
    "volume", "son", "plus fort", "moins fort", "mute", "silence",
    "augmente", "diminue", "coupe", "retablis",
    # Système
    "cpu", "ram", "memoire", "processeur", "disque", "stockage",
    # Actions
    "capture", "screenshot", "verrouille", "recherche",
    "ouvre", "lance", "ferme", "demarre",
    # Sécurité
    "eteins", "redemarre", "veille", "reboot", "shutdown",
    # Confirmation
    "oui", "non", "ok", "annule",
    # Date/heure
    "heure", "date", "jour",
])


class STT:
    def __init__(self, model_or_path):
        if isinstance(model_or_path, vosk.Model):
            self.model = model_or_path
        else:
            logger.info(f"Chargement Vosk : {model_or_path}")
            self.model = vosk.Model(model_or_path)

        self.samplerate = config.SAMPLE_RATE
        self.q = queue.Queue()

    def _callback(self, indata, frames, time_info, status):
        if status:
            logger.warning(f"Audio status : {status}")
        self.q.put(bytes(indata))

    def _flush_queue(self):
        """Vide la queue des données résiduelles du wakeword."""
        while not self.q.empty():
            try:
                self.q.get_nowait()
            except Exception:
                break

    def listen(self, mode: str = "command") -> str:
        """
        Écoute et retourne le texte reconnu.

        :param mode: "command" (vocab restreint, rapide)
                     "free"    (vocab complet, conversation)
        """
        self._flush_queue()

        silence_timeout = (
            config.STT_SILENCE_TIMEOUT_CMD  if mode == "command"
            else config.STT_SILENCE_TIMEOUT_FREE
        )
        total_timeout = config.STT_TOTAL_TIMEOUT

        # Choisir le recognizer selon le mode
        if mode == "command":
            recognizer = vosk.KaldiRecognizer(self.model, self.samplerate, _COMMAND_VOCAB)
        else:
            recognizer = vosk.KaldiRecognizer(self.model, self.samplerate)
        recognizer.SetWords(False)

        final_text     = ""
        last_speech_t  = time.time()
        start_t        = time.time()

        with sd.RawInputStream(samplerate=self.samplerate, blocksize=4000,
                               device=None, dtype="int16", channels=1,
                               callback=self._callback):
            logger.debug(f"Écoute mode={mode}, silence={silence_timeout}s")
            while True:
                elapsed = time.time() - start_t
                if elapsed > total_timeout:
                    break

                try:
                    data = self.q.get(timeout=0.1)
                except queue.Empty:
                    if time.time() - last_speech_t > silence_timeout:
                        break
                    continue

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        final_text    += " " + text
                        last_speech_t  = time.time()
                else:
                    partial = json.loads(recognizer.PartialResult())
                    if partial.get("partial", "").strip():
                        last_speech_t = time.time()

            # Résidu final
            final_result = json.loads(recognizer.FinalResult())
            remaining = final_result.get("text", "").strip()
            if remaining:
                final_text += " " + remaining

        return final_text.strip()
