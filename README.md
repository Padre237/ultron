<div align="center">
<img src="docs/orb_preview.svg" width="280" alt="JARVIS Orb"/>

# J · A · R · V · I · S

**Assistant vocal personnel — 100% local · 100% français · Zéro cloud**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vosk](https://img.shields.io/badge/STT-Vosk-00C7B7?style=flat-square)](https://alphacephei.com/vosk/)
[![Piper](https://img.shields.io/badge/TTS-Piper-FF6B35?style=flat-square)](https://github.com/rhasspy/piper)
[![llama.cpp](https://img.shields.io/badge/LLM-llama--cpp-8A2BE2?style=flat-square)](https://github.com/ggerganov/llama.cpp)
[![PyQt5](https://img.shields.io/badge/UI-PyQt5-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Linux](https://img.shields.io/badge/Linux-Ubuntu_24.04-E95420?style=flat-square&logo=ubuntu&logoColor=white)](https://ubuntu.com)
[![License](https://img.shields.io/badge/licence-MIT-blue?style=flat-square)](LICENSE)

</div>

---

<div align="center">

```
  Dites  ❝ Jarvis ❞  →  il écoute  →  comprend  →  répond  →  agit
```

</div>

---

## Ce que fait Jarvis

| Capacité | Détail |
|----------|--------|
| 🎙️ **Wake word** | Détection passive de "Jarvis" en continu, ~2% CPU |
| 🧠 **Compréhension** | Vosk STT français, vocab restreint pour les commandes |
| ⚡ **LLM local** | llama-cpp-python + Qwen2.5-0.5B GGUF, streaming token/token |
| 🔊 **Voix naturelle** | Piper TTS, voix Gilles, pipe direct sans fichier temporaire |
| 🖥️ **17 commandes système** | Volume, apps, captures, infos système, veille, reboot... |
| 🔒 **Confirmation vocale** | Actions dangereuses protégées par "oui / non" vocal |
| 💬 **Mémoire** | Historique des 6 derniers échanges en contexte |
| 🎨 **Interface orbe** | Fenêtre PyQt5 frameless, transparente, toujours au premier plan |

---

## Interface

<div align="center">

| État | Couleur | Comportement |
|------|---------|-------------|
| 🔵 En veille | `#00d4ff` | Pulse lent, particules lentes |
| 🟠 Écoute | `#ffaa00` | Pulse rapide, barres vocales actives |
| 🟣 Traitement | `#ff00ff` | Pulse intense, data streams |
| 🟢 Parole | `#00ff88` | Ondes sonores, barres à fond |

</div>

---

## Installation rapide

<details>
<summary><b>Étape 1 — Prérequis système</b></summary>

```bash
sudo apt update && sudo apt install -y \
    python3-pip python3-venv \
    python3-pyqt5 python3-pyqt5.qtwebengine \
    portaudio19-dev alsa-utils pulseaudio \
    cmake build-essential libopenblas-dev liblapack-dev \
    wget unzip scrot
```

</details>

<details>
<summary><b>Étape 2 — Environnement Python</b></summary>

```bash
git clone https://github.com/Padre237/ultron.git
cd ultron

python3 -m venv venv
source venv/bin/activate

# Exposer PyQt5 système
echo "/usr/lib/python3/dist-packages" > venv/lib/python3.12/site-packages/system-pyqt5.pth

pip install vosk sounddevice requests piper-tts huggingface-hub

# LLM local (compilation ~5-15 min)
CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
pip install llama-cpp-python --no-cache-dir
```

</details>

<details>
<summary><b>Étape 3 — Télécharger les modèles</b></summary>

```bash
# Modèle STT Vosk français (~41 Mo)
mkdir -p models/vosk && cd models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip && cd ../..

# Modèle TTS Piper — voix Gilles (~61 Mo)
mkdir -p models/piper && cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json
cd ../..

# Modèle LLM GGUF Qwen2.5-0.5B (~491 Mo)
mkdir -p models/gguf
hf download Qwen/Qwen2.5-0.5B-Instruct-GGUF \
    qwen2.5-0.5b-instruct-q4_k_m.gguf \
    --local-dir models/gguf/
```

</details>

<details>
<summary><b>Étape 4 — Vérification</b></summary>

```bash
source venv/bin/activate
python3 -c "
import vosk, sounddevice, llama_cpp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os, sys; sys.path.insert(0,'.')
import config
assert os.path.exists(config.VOSK_MODEL_PATH),  'Vosk manquant'
assert os.path.exists(config.PIPER_MODEL_PATH), 'Piper manquant'
assert os.path.exists(config.GGUF_MODEL_PATH),  'GGUF manquant'
print('✓ Tout est prêt — lancez : ./run.sh')
"
```

</details>

---

## Lancement

```bash
./run.sh
```

> La fenêtre orbe s'ouvre. Dites **"Jarvis"** pour l'activer.

---

## Commandes vocales

### Système numéroté — dites `commande` + numéro

> Vosk reconnaît fiablement les chiffres. Variantes acceptées : *"command 3"*, *"komande six"*

| N° | Action | N° | Action |
|----|--------|----|--------|
| `commande 1` | Ouvrir Firefox | `commande 10` | Utilisation CPU |
| `commande 2` | Gestionnaire de fichiers | `commande 11` | Utilisation RAM |
| `commande 3` | Terminal | `commande 12` | Espace disque |
| `commande 4` | VLC | `commande 13` | Capture d'écran |
| `commande 5` | Paramètres système | `commande 14` | Verrouiller l'écran |
| `commande 6` | Volume + | `commande 15` | Veille ⚠️ |
| `commande 7` | Volume - | `commande 16` | Redémarrer ⚠️ |
| `commande 8` | Mute | `commande 17` | Éteindre ⚠️ |
| `commande 9` | Unmute | | |

> ⚠️ Confirmation vocale requise — dites **"oui"** ou **"non"**

### Commandes naturelles

<details>
<summary><b>Voir toutes les commandes naturelles</b></summary>

**Applications**
```
"ouvre firefox"            → Lance Firefox
"lance le terminal"        → Lance Konsole
"ouvre les fichiers"       → Lance Dolphin
"ferme vlc"                → Ferme l'application
```

**Volume**
```
"augmente le volume"       → +5%
"baisse le son"            → -5%
"coupe le son"             → Mute
"rétablis le son"          → Unmute
```

**Système**
```
"processeur"               → % CPU
"mémoire"                  → RAM utilisée
"espace disque"            → Espace libre
"quelle heure est-il"      → Heure et date
"capture d'écran"          → Screenshot → ~/Images
"recherche fichier.txt"    → Cherche dans ~/
"cherche sur internet ..."  → Ouvre Firefox + Google
"oublie tout"              → Efface l'historique LLM
```

</details>

### Conversation libre
Toute phrase non reconnue comme commande est envoyée au **LLM Qwen2.5** avec streaming — Jarvis commence à parler avant d'avoir fini de générer.

---

## Architecture

```
jarvis/
├── main.py              # Orchestration — thread Qt + thread vocal
├── config.py            # Configuration centralisée
├── brain/
│   └── llm.py           # llama-cpp-python + streaming + historique
├── commands/
│   └── executor.py      # Pattern matching normalisé (accents, apostrophes)
├── interface/
│   ├── jarvis_orb.html  # Orbe canvas 2D animée (WebGL)
│   └── orb_window.py    # Fenêtre PyQt5 frameless + overlay texte
├── tts/
│   └── speak.py         # Piper pipe direct + cache RAM phrases fixes
├── voice/
│   ├── stt.py           # Vosk vocab restreint + timeout adaptatif
│   └── wakeword.py      # Détection "Jarvis" passive
└── security/
    └── confirmation.py  # Confirmation vocale oui/non
```

---

## Stack technique

| Composant | Technologie | Latence |
|-----------|------------|---------|
| Wake word | Vosk (vocab 3 mots) | ~50ms |
| STT commandes | Vosk (vocab 50 mots) | ~100ms |
| STT conversation | Vosk (vocab libre) | ~250ms |
| LLM | llama-cpp-python Qwen2.5-0.5B Q4 | ~150ms premier token |
| TTS (cache) | Piper pré-généré RAM | ~50ms |
| TTS (dynamique) | Piper pipe direct → aplay | ~800ms |
| UI | PyQt5 + QtWebEngine canvas 2D | 60 FPS |

---

## Optimisations

- **Vosk partagé** — un seul modèle en RAM pour wakeword + STT (-300 Mo)
- **Cache audio** — 10 phrases fixes pré-générées au démarrage (-1.5s/réponse)
- **Piper sans fichier temp** — stdout pipé directement dans aplay (-1s)
- **Streaming LLM+TTS** — parle phrase par phrase pendant la génération (-2s perçu)
- **Normalisation Vosk** — suppression accents/apostrophes (+20% reconnaissance)
- **Vocab restreint** — Vosk précision +15%, latence -40% sur les commandes

---

## Roadmap

- [ ] Whisper.cpp `tiny-fr` — précision STT 75% → 92%
- [ ] Kokoro TTS — latence 800ms → 150ms
- [ ] Qwen2.5-1.5B Q3 — meilleure qualité LLM
- [ ] VAD Silero — détection fin de phrase plus précise
- [ ] Démarrage automatique au login

---

<div align="center">

**100% local · Zéro cloud · Zéro tracking · Zéro internet requis**

*Fait avec Python sur Linux*

</div>
