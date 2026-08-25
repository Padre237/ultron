import sounddevice as sd
import vosk
import queue
import sys

# Charger le modèle français
model = vosk.Model("models/vosk/vosk-model-small-fr-0.22")
samplerate = 16000

# Afficher le périphérique d'entrée
print("Périphérique d'entrée :", sd.query_devices(kind='input'))

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=None, dtype='int16', channels=1, callback=callback):
    print("Enregistrement 5 secondes... Parlez en français.")
    rec = vosk.KaldiRecognizer(model, samplerate)
    for _ in range(0, int(samplerate / 8000 * 5)):
        data = q.get()
        if rec.AcceptWaveform(data):
            pass
    print("Résultat partiel :", rec.PartialResult())
    print("Résultat final :", rec.FinalResult())
