<div align="center">

<!-- ORBE ANIMÉE -->
<p align="center">
<img src="docs/orb_preview.svg" width="180" alt="JARVIS Orb"/>
</p>

# J.A.R.V.I.S

### Assistant vocal personnel — 100% local, 100% français

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Vosk](https://img.shields.io/badge/STT-Vosk-00C7B7?style=for-the-badge)](https://alphacephei.com/vosk/)
[![Piper](https://img.shields.io/badge/TTS-Piper-FF6B35?style=for-the-badge)](https://github.com/rhasspy/piper)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?style=for-the-badge)](https://ollama.ai)
[![PyQt5](https://img.shields.io/badge/UI-PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)

> Dites **"Jarvis"** — il écoute, comprend, répond et agit. Sans internet, sans cloud, sans délai.

</div>

---

## Interface

<div align="center">
<img src="docs/orb_preview.svg" width="220" alt="JARVIS Orb — interface animée"/>
<br/>
<em>Fenêtre PyQt5 sans bordure · Transparente · Toujours au premier plan · Draggable</em>
</div>

| Couleur | État |
|---------|------|
| 🔵 Bleu `#00d4ff` | En veille |
| 🟠 Orange `#ffaa00` | Écoute active |
| 🟣 Violet `#ff00ff` | Traitement / LLM |
| 🟢 Vert `#00ff88` | Réponse vocale |

</div>

---

## Fonctionnalités

- **Wake word** — détection passive du mot "Jarvis" sans consommer de ressources
- **STT local** — reconnaissance vocale française via Vosk, zéro cloud
- **TTS local** — synthèse vocale naturelle via Piper (voix Gilles)
- **LLM local** — conversation via Ollama / qwen2.5, zéro internet requis
- **17 commandes système** — volume, apps, captures, infos système, veille...
- **Confirmation vocale** — les actions dangereuses demandent "oui / non" à voix haute
- **Commandes numérotées** — dites "commande 13" pour une reconnaissance fiable
- **Normalisation Vosk** — les variantes phonétiques sont toutes acceptées
- **Interface orbe** — canvas animé WebGL dans une fenêtre PyQt5 native

---

## Installation

### Prérequis système

```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine \
                 python3-pip portaudio19-dev alsa-utils pulseaudio
```

### Cloner et configurer

```bash
git clone https://github.com/VOTRE_USERNAME/jarvis.git
cd jarvis

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Exposer PyQt5 système dans le venv
echo "/usr/lib/python3/dist-packages" > venv/lib/python3.12/site-packages/system-pyqt5.pth

# Installer les dépendances Python
pip install vosk sounddevice requests
```

### Télécharger les modèles

```bash
# Modèle STT Vosk français
mkdir -p models/vosk
cd models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip
cd ../..

# Modèle TTS Piper (voix Gilles)
mkdir -p models/piper
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/gilles/low/fr_FR-gilles-low.onnx.json
cd ../..

# Installer Piper dans le venv
pip install piper-tts
```

### Installer et démarrer Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2.5:0.5b
```

### Lancer Jarvis

```bash
source venv/bin/activate
python3 main.py
```

---

## Commandes vocales

### Activation

Dites **"Jarvis"** — l'orbe passe en orange et Jarvis répond **"Oui."**

---

### Système numéroté

> Dites **"commande"** suivi du numéro. Variantes acceptées : *"command"*, *"komande"*, *"execute commande"*

| N° | Action | Description |
|----|--------|-------------|
| `commande 1` | Ouvrir Firefox | Lance le navigateur |
| `commande 2` | Ouvrir les fichiers | Lance Dolphin |
| `commande 3` | Ouvrir le terminal | Lance Konsole |
| `commande 4` | Ouvrir VLC | Lance le lecteur vidéo |
| `commande 5` | Ouvrir les paramètres | Paramètres système |
| `commande 6` | Augmenter le volume | +5% |
| `commande 7` | Diminuer le volume | -5% |
| `commande 8` | Couper le son | Mute toggle |
| `commande 9` | Rétablir le son | Unmute |
| `commande 10` | CPU | Affiche l'utilisation processeur |
| `commande 11` | RAM | Affiche la mémoire utilisée |
| `commande 12` | Disque | Affiche l'espace libre |
| `commande 13` | Capture d'écran | Enregistre dans ~/Images |
| `commande 14` | Verrouiller | Verrouille la session |
| `commande 15` | Veille | Suspend *(confirmation vocale)* |
| `commande 16` | Redémarrer | Reboot *(confirmation vocale)* |
| `commande 17` | Éteindre | Shutdown *(confirmation vocale)* |

---

### Commandes naturelles

#### Applications
```
"ouvre firefox"          → Lance Firefox
"lance le terminal"      → Lance Konsole
"ouvre les fichiers"     → Lance Dolphin
"lance vlc"              → Lance VLC
"ferme firefox"          → Ferme l'application
```

#### Volume
```
"augmente le volume" / "plus fort"    → +5%
"diminue le volume"  / "moins fort"   → -5%
"coupe le son"       / "silence"      → Mute
"rétablis le son"    / "remets le son" → Unmute
```

#### Système
```
"processeur" / "CPU"          → % utilisation CPU
"RAM" / "mémoire"             → RAM utilisée / totale
"espace disque" / "stockage"  → Espace libre sur /
```

#### Divers
```
"capture" / "screenshot"      → Capture d'écran → ~/Images
"recherche document.pdf"      → Recherche dans ~/
"verrouille"                  → Verrouille la session
```

#### Actions dangereuses *(confirmation vocale "oui / non" requise)*
```
"éteins" / "shutdown"         → Extinction
"redémarre" / "reboot"        → Redémarrage
"mets en veille" / "suspend"  → Suspension
```

#### Conversation libre
```
Toute autre phrase → envoyée au LLM Ollama pour réponse conversationnelle
```

---

## Structure du projet

```
jarvis/
├── main.py                      # Point d'entrée — boucle principale
├── config.py                    # Configuration centralisée
├── commandes.md                 # Référence des commandes (ce fichier)
│
├── brain/
│   └── llm.py                   # Client Ollama (LLM local)
│
├── commands/
│   └── executor.py              # Reconnaissance + exécution des commandes
│                                  (normalisation Vosk, système numéroté)
├── interface/
│   ├── jarvis_orb.html          # Orbe animée (canvas HTML5)
│   ├── orb_window.py            # Fenêtre PyQt5 frameless
│   └── server.py                # Serveur HTTP/SSE (mode navigateur)
│
├── models/
│   ├── piper/                   # Modèles TTS (.onnx + .onnx.json)
│   └── vosk/                    # Modèle STT français
│
├── security/
│   └── confirmation.py          # Confirmation vocale (actions dangereuses)
│
├── tts/
│   └── speak.py                 # Synthèse vocale Piper → aplay
│
└── voice/
    ├── stt.py                   # Reconnaissance vocale Vosk
    └── wakeword.py              # Détection mot-clé "Jarvis"
```

---

## Configuration

Fichier `config.py` — tous les paramètres au même endroit :

| Variable | Valeur par défaut | Description |
|----------|------------------|-------------|
| `ASSISTANT_NAME` | `jarvis` | Mot-clé d'activation |
| `VOSK_MODEL_PATH` | `models/vosk/vosk-model-small-fr-0.22` | Modèle STT |
| `PIPER_MODEL_PATH` | `models/piper/fr_FR-gilles-low.onnx` | Modèle TTS |
| `OLLAMA_URL` | `http://localhost:11434` | URL serveur Ollama |
| `OLLAMA_MODEL` | `qwen2.5:0.5b` | Modèle LLM |
| `SAMPLE_RATE` | `16000` | Fréquence audio |

---

## Stack technique

| Composant | Technologie | Rôle |
|-----------|------------|------|
| Wake word | Vosk (vocab restreint) | Détection passive de "Jarvis" |
| STT | Vosk `small-fr-0.22` | Transcription vocale française |
| LLM | Ollama + qwen2.5:0.5b | Réponses conversationnelles |
| TTS | Piper + voix Gilles | Synthèse vocale naturelle |
| UI | PyQt5 + WebEngine | Fenêtre orbe animée |
| Audio | sounddevice + aplay | Capture et lecture audio |

---

## Roadmap

- [ ] Remplacer Ollama par `llama-cpp-python` (latence réduite)
- [ ] Piper en pipe direct sans fichier temporaire
- [ ] Cache audio pour les phrases fixes
- [ ] Vocabulaire restreint STT pour les commandes
- [ ] Historique de conversation
- [ ] Whisper.cpp pour une meilleure précision STT
- [ ] Support multi-langue

---

<div align="center">

Fait avec Python · Tourne entièrement en local · Aucune donnée envoyée sur internet

</div>
