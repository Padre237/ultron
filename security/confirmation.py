import sys
import os
import queue
import json
import time
import sounddevice as sd

# Ajouter le dossier racine au path pour importer config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ask_confirmation_vocal(message, vosk_model=None):
    """
    Pose une question de confirmation vocalement et écoute la réponse.
    Retourne True si l'utilisateur dit 'oui', False sinon.

    :param message: texte à prononcer pour demander confirmation.
    :param vosk_model: instance vosk.Model partagée (optionnelle).
    """
    # Import ici pour éviter les imports circulaires
    from tts.speak import speak

    speak(message)
    print(f"[Confirmation] {message}", flush=True)

    # Charger le modèle Vosk si non fourni
    import vosk as vosk_lib
    if vosk_model is None:
        import config
        vosk_model = vosk_lib.Model(config.VOSK_MODEL_PATH)

    samplerate = 16000
    audio_q = queue.Queue()

    def _callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_q.put(bytes(indata))

    # Vocabulaire limité à oui/non pour une détection rapide
    vocab = json.dumps(["oui", "non", "yes", "no", "ok", "annule", "annuler"])
    recognizer = vosk_lib.KaldiRecognizer(vosk_model, samplerate, vocab)

    start_time = time.time()
    timeout = 8  # secondes pour répondre

    with sd.RawInputStream(samplerate=samplerate, blocksize=4000,
                           device=None, dtype="int16", channels=1,
                           callback=_callback):
        print("En attente de votre réponse (oui / non)...", flush=True)
        while time.time() - start_time < timeout:
            try:
                data = audio_q.get(timeout=0.2)
            except queue.Empty:
                continue

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower().strip()
                print(f"[Confirmation] Entendu : '{text}'", flush=True)
                if text in ["oui", "yes", "ok"]:
                    speak("Confirmé.")
                    return True
                if text in ["non", "no", "annule", "annuler"]:
                    speak("Action annulée.")
                    return False

    # Timeout : annulation par défaut pour la sécurité
    speak("Pas de réponse. Action annulée par sécurité.")
    print("[Confirmation] Timeout — action annulée.", flush=True)
    return False


def ask_confirmation(message="Êtes-vous sûr ? (oui/non)", vosk_model=None):
    """
    Point d'entrée principal pour les confirmations.
    Utilise la confirmation vocale.
    """
    return ask_confirmation_vocal(message, vosk_model=vosk_model)


# Liste des actions nécessitant confirmation
DANGEROUS_ACTIONS = [
    "shutdown", "reboot", "halt", "poweroff",
    "suspend", "hibernate", "logout",
    "rm", "sudo", "dd", "mkfs"
]


def is_dangerous(command_text):
    """
    Vérifie si la commande texte contient une action dangereuse.
    """
    text_lower = command_text.lower()
    return any(action in text_lower for action in DANGEROUS_ACTIONS)
