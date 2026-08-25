import vosk
import sounddevice as sd
import queue
import json
import sys

class WakeWordDetector:
    def __init__(self, model_or_path, wakeword="loulou"):
        """
        Détecte le mot-clé en utilisant Vosk avec un vocabulaire restreint.

        :param model_or_path: instance vosk.Model déjà chargée, ou chemin vers le modèle.
        :param wakeword: mot-clé à détecter (en minuscules).
        """
        if isinstance(model_or_path, vosk.Model):
            self.model = model_or_path
        else:
            print(f"Chargement du modèle Vosk depuis : {model_or_path}", flush=True)
            self.model = vosk.Model(model_or_path)

        self.samplerate = 16000
        self.wakeword = wakeword.lower()
        self.q = queue.Queue()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Erreur audio: {status}", file=sys.stderr)
        self.q.put(bytes(indata))

    def wait_for_wakeword(self):
        """
        Écoute en continu jusqu'à ce que le mot-clé soit reconnu.
        Retourne True quand le mot-clé est détecté.
        """
        print(f"En veille... Dites '{self.wakeword}' pour activer.", flush=True)

        # Vocabulaire limité pour une détection rapide et précise
        vocab = json.dumps([self.wakeword, f"hey {self.wakeword}", f"ok {self.wakeword}"])
        recognizer = vosk.KaldiRecognizer(self.model, self.samplerate, vocab)

        with sd.RawInputStream(samplerate=self.samplerate, blocksize=4000,
                               device=None, dtype="int16", channels=1,
                               callback=self._audio_callback):
            while True:
                data = self.q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").lower()
                    if self.wakeword in text:
                        print(f"Mot-clé détecté : '{text}'", flush=True)
                        return True


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config
    detector = WakeWordDetector(config.VOSK_MODEL_PATH, config.ASSISTANT_NAME)
    detector.wait_for_wakeword()
    print("Activé !")
