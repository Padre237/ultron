# JARVIS — Assistant vocal personnel

## Lancement

```bash
cd /home/student/jarvis
source venv/bin/activate
python3 main.py
```

---

## Commandes vocales

### Activation
Dites **"Jarvis"** pour activer l'assistant, puis énoncez votre commande.

---

### Système numéroté — dites "commande + numéro"

> Exemples : *"commande 1"*, *"commande 13"*, *"kommande six"*

| N° | Commande             | Description                        |
|----|---------------------|------------------------------------|
| 1  | Ouvrir Firefox      | Lance le navigateur Firefox        |
| 2  | Ouvrir les fichiers | Lance le gestionnaire Dolphin      |
| 3  | Ouvrir le terminal  | Lance Konsole                      |
| 4  | Ouvrir VLC          | Lance le lecteur VLC               |
| 5  | Ouvrir les paramètres | Lance les paramètres système     |
| 6  | Augmenter le volume | Monte le volume de 5%              |
| 7  | Diminuer le volume  | Baisse le volume de 5%             |
| 8  | Couper le son       | Mute / Unmute (toggle)             |
| 9  | Rétablir le son     | Réactive le son                    |
| 10 | Utilisation CPU     | Affiche le % d'utilisation CPU     |
| 11 | Utilisation RAM     | Affiche la RAM utilisée / totale   |
| 12 | Espace disque       | Affiche l'espace libre sur /       |
| 13 | Capture d'écran     | Enregistre une capture dans ~/Images |
| 14 | Verrouiller l'écran | Verrouille la session              |
| 15 | Mettre en veille    | Suspend l'ordinateur (confirmation vocale) |
| 16 | Redémarrer          | Redémarre le système (confirmation vocale) |
| 17 | Éteindre            | Éteint l'ordinateur (confirmation vocale)  |

---

### Commandes naturelles (reconnaissance flexible)

#### Applications
| Ce que vous dites              | Action                        |
|-------------------------------|-------------------------------|
| "ouvre firefox"               | Lance Firefox                 |
| "lance le terminal"           | Lance Konsole                 |
| "ouvre les fichiers"          | Lance Dolphin                 |
| "lance vlc"                   | Lance VLC                     |
| "ouvre les paramètres"        | Lance les paramètres système  |
| "ferme firefox"               | Ferme l'application           |

#### Volume
| Ce que vous dites                      | Action            |
|---------------------------------------|-------------------|
| "augmente le volume" / "plus fort"    | Volume +5%        |
| "diminue le volume" / "moins fort"    | Volume -5%        |
| "coupe le son" / "silence"            | Mute              |
| "rétablis le son" / "remets le son"   | Unmute            |

#### Informations système
| Ce que vous dites                     | Action                      |
|--------------------------------------|-----------------------------|
| "processeur" / "CPU"                 | Affiche le % CPU            |
| "RAM" / "mémoire"                    | Affiche la RAM              |
| "espace disque" / "stockage"         | Affiche l'espace libre      |

#### Capture d'écran
| Ce que vous dites                          | Action                       |
|-------------------------------------------|------------------------------|
| "capture" / "screenshot" / "capture écran"| Capture dans ~/Images        |

#### Recherche de fichier
| Ce que vous dites              | Action                            |
|-------------------------------|-----------------------------------|
| "recherche document.pdf"       | Cherche le fichier dans ~/        |

#### Sécurité (confirmation vocale requise)
| Ce que vous dites              | Action (confirmation oui/non)     |
|-------------------------------|-----------------------------------|
| "éteins" / "shutdown"         | Éteint l'ordinateur               |
| "redémarre" / "reboot"        | Redémarre                         |
| "mets en veille" / "suspend"  | Suspend                           |
| "verrouille"                  | Verrouille la session (immédiat)  |

---

### Conversation libre
Toute phrase non reconnue comme commande est envoyée au LLM **Ollama** (`qwen2.5:0.5b`) pour une réponse conversationnelle.

---

## Structure du projet

```
jarvis/
├── main.py                  # Point d'entrée principal
├── config.py                # Configuration (chemins, modèles, URL Ollama)
├── brain/
│   └── llm.py               # Client Ollama
├── commands/
│   └── executor.py          # Reconnaissance et exécution des commandes
├── interface/
│   ├── jarvis_orb.html      # Animation de l'orbe (canvas WebGL)
│   ├── orb_window.py        # Fenêtre PyQt5 frameless
│   └── server.py            # Serveur HTTP / SSE (non utilisé en mode PyQt5)
├── models/
│   ├── piper/               # Modèles TTS Piper
│   └── vosk/                # Modèle STT Vosk français
├── security/
│   └── confirmation.py      # Confirmation vocale pour actions dangereuses
├── tts/
│   └── speak.py             # Synthèse vocale via Piper + aplay
└── voice/
    ├── stt.py               # Reconnaissance vocale (Vosk)
    └── wakeword.py          # Détection du mot-clé "Jarvis"
```

---

## Configuration (`config.py`)

| Variable          | Valeur par défaut                              | Description              |
|-------------------|------------------------------------------------|--------------------------|
| `VOSK_MODEL_PATH` | `models/vosk/vosk-model-small-fr-0.22`         | Modèle STT français      |
| `PIPER_MODEL_PATH`| `models/piper/fr_FR-gilles-low.onnx`           | Modèle TTS voix Gilles   |
| `OLLAMA_URL`      | `http://localhost:11434`                       | URL du serveur Ollama    |
| `OLLAMA_MODEL`    | `qwen2.5:0.5b`                                 | Modèle LLM local         |
| `ASSISTANT_NAME`  | `jarvis`                                       | Mot-clé d'activation     |

---

## Dépendances

```
vosk
sounddevice
requests
PyQt5
PyQtWebEngine
piper (binaire dans venv/bin/)
aplay (système)
pactl (système, PulseAudio)
```
