# Installation complète — Jarvis

Exécute les blocs dans l'ordre. Chaque bloc est indépendant.

---

## Étape 0 — Prérequis système

```bash
sudo apt update
sudo apt install -y \
    python3-pip python3-venv \
    python3-pyqt5 python3-pyqt5.qtwebengine \
    portaudio19-dev alsa-utils pulseaudio \
    wget unzip git curl \
    cmake build-essential pkg-config \
    libopenblas-dev liblapack-dev \
    scrot
```

---

## Étape 1 — Environnement Python

```bash
cd /home/student/jarvis

# Créer le venv s'il n'existe pas
python3 -m venv venv
source venv/bin/activate

# Exposer PyQt5 système dans le venv
echo "/usr/lib/python3/dist-packages" > venv/lib/python3.12/site-packages/system-pyqt5.pth

# Dépendances de base
pip install --upgrade pip
pip install vosk sounddevice requests
```

---

## Étape 2 — llama-cpp-python (LLM local)

```bash
source venv/bin/activate

# Installer avec support CPU optimisé (OpenBLAS)
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
pip install llama-cpp-python --no-cache-dir
```

> Si ça échoue ou dure trop longtemps, version sans optimisation :
> ```bash
> pip install llama-cpp-python --no-cache-dir
> ```

---

## Étape 3 — Modèle GGUF (Qwen2.5 0.5B)

```bash
source venv/bin/activate
pip install huggingface-hub

mkdir -p /home/student/jarvis/models/gguf

huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct-GGUF \
    qwen2.5-0.5b-instruct-q4_k_m.gguf \
    --local-dir /home/student/jarvis/models/gguf/
```

> Taille : ~400 Mo. Vérifie avec :
> ```bash
> ls -lh /home/student/jarvis/models/gguf/
> ```

---

## Étape 4 — Modèle STT Vosk (si pas encore fait)

```bash
mkdir -p /home/student/jarvis/models/vosk
cd /home/student/jarvis/models/vosk

wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
rm vosk-model-small-fr-0.22.zip

cd /home/student/jarvis
```

---

## Étape 5 — Modèle TTS Piper (si pas encore fait)

```bash
source venv/bin/activate

# Installer Piper
pip install piper-tts

# Télécharger la voix Gilles
mkdir -p /home/student/jarvis/models/piper
cd /home/student/jarvis/models/piper

wget -q "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx"
wget -q "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json"

cd /home/student/jarvis
```

---

## Étape 6 — Vérification complète

```bash
cd /home/student/jarvis
source venv/bin/activate

python3 -c "
import vosk;          print('✓ vosk')
import sounddevice;   print('✓ sounddevice')
import requests;      print('✓ requests')
import llama_cpp;     print('✓ llama-cpp-python')
from PyQt5.QtWidgets import QApplication; print('✓ PyQt5')
from PyQt5.QtWebEngineWidgets import QWebEngineView; print('✓ WebEngine')
import os, sys
sys.path.insert(0,'.')
import config
assert os.path.exists(config.VOSK_MODEL_PATH),  '✗ modèle Vosk manquant'
assert os.path.exists(config.PIPER_MODEL_PATH), '✗ modèle Piper manquant'
gguf = 'models/gguf/qwen2.5-0.5b-instruct-q4_k_m.gguf'
assert os.path.exists(gguf), f'✗ modèle GGUF manquant : {gguf}'
print('✓ tous les modèles présents')
print()
print('TOUT EST PRÊT — lance : python3 main.py')
"
```

---

## Résumé — ce qui doit être installé

| Composant | Commande de vérif |
|-----------|------------------|
| vosk | `python3 -c "import vosk"` |
| sounddevice | `python3 -c "import sounddevice"` |
| requests | `python3 -c "import requests"` |
| llama-cpp-python | `python3 -c "import llama_cpp"` |
| PyQt5 | `python3 -c "from PyQt5.QtWidgets import QApplication"` |
| PyQtWebEngine | `python3 -c "from PyQt5.QtWebEngineWidgets import QWebEngineView"` |
| Piper (binaire) | `ls venv/bin/piper` |
| Modèle Vosk | `ls models/vosk/vosk-model-small-fr-0.22/` |
| Modèle Piper | `ls models/piper/fr_FR-gilles-low.onnx` |
| Modèle GGUF | `ls models/gguf/qwen2.5-0.5b-instruct-q4_k_m.gguf` |

---

## Une fois tout installé

Dis-le moi — je prends la main pour implémenter :
- `brain/llm.py` avec llama-cpp-python + streaming
- `tts/speak.py` Piper pipe direct + cache audio
- `voice/stt.py` vocab restreint + timeout adaptatif
- Historique conversation, commandes date/heure, logs, run.sh, .desktop
