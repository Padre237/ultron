# Architecture technique — Jarvis

> Assistant vocal personnel 100% local, zéro cloud, haute performance

---

## Vision

**Jarvis** est un assistant vocal conversationnel qui tourne entièrement en local sur Linux. Il écoute en permanence, se réveille au mot-clé "Jarvis", comprend les commandes vocales en français, exécute des actions système, répond aux questions via un LLM local, et fournit un retour visuel temps réel via une interface orbe animée.

**Objectifs de performance** :
- Latence commande → action : **< 1 seconde**
- Latence question → première syllabe : **< 500ms**
- Zéro dépendance réseau — 100% offline
- Consommation RAM : **< 2 Go** (tous modèles chargés)
- CPU : compatible processeurs x86_64 modernes sans GPU requis

---

## Stack technique

### Backend — Python 3.12

| Composant | Technologie | Rôle | Performance |
|-----------|------------|------|-------------|
| **Wake word** | Vosk (vocabulaire restreint) | Détection passive "Jarvis" | ~15ms latence, 50 Mo RAM |
| **STT** | Vosk `small-fr-0.22` | Reconnaissance vocale française | ~200-300ms transcription |
| **STT (commandes)** | Vosk (vocab restreint 20 mots) | Reconnaissance précise des commandes | ~100-150ms, précision 95%+ |
| **LLM** | llama.cpp via llama-cpp-python | Conversation en français | Première token ~150ms |
| **TTS** | Piper (voix Gilles ONNX) | Synthèse vocale naturelle | ~800ms génération + lecture |
| **TTS (cache)** | Fichiers WAV pré-générés | Phrases fixes instantanées | ~50ms lecture depuis RAM |
| **Audio I/O** | sounddevice + aplay | Capture micro + lecture audio | Latence ~20ms |
| **Interface** | PyQt5 + QtWebEngine | Fenêtre native + canvas WebGL | 60 FPS animations |
| **Exécution** | subprocess + asyncio | Commandes système non-bloquantes | — |

---

## Frontend — Interface visuelle

### Fenêtre PyQt5 frameless

**Caractéristiques** :
- Sans bordure, transparente, toujours au premier plan
- Draggable à la souris
- Redimensionnable (par défaut 520×520px)
- Icône dans la barre système (tray icon) avec menu contextuel
- Fermeture → masquage au lieu de quitter

**Technologie** :
```
PyQt5 (5.15) + QtWebEngine → charge jarvis_orb.html
```

---

### Orbe animée — Canvas WebGL

**Fichier** : `interface/jarvis_orb.html`

#### Composants visuels

| Élément | Description | Animation |
|---------|-------------|-----------|
| **Noyau** | Sphère centrale blanche lumineuse | Pulse 0.5-1.0 échelle, 2s cycle |
| **Orbe principale** | Gradient radial (blanc → couleur état → noir) | Pulse + glow dynamique |
| **Glow externe** | Halo flou 4× rayon orbe | Pulse synchronisé, opacité 0.3-1.0 |
| **Anneau hexagonal** | Hexagone tournant lent | Rotation continue 30s/tour |
| **Anneau concentrique** | Cercle fin 1.4× rayon orbe | Pulse radius ±4px |
| **Particules orbitales** | 25 points lumineux en orbite 3D | Vitesse variable, trail effet |
| **Data streams** | 10 colonnes de binaire tombantes | Descente 1-3px/frame, fade out |
| **Barres vocales** | 7 barres verticales animées | Hauteur aléatoire synchronisée |
| **Grille de fond** | Grille 50×50px cyan translucide | Statique, opacité 0.03 |
| **Scan lines** | Lignes horizontales traversantes | Effet CRT, opacité 0.1 |
| **Lens flares** | 3 répliques décalées de l'orbe | Opacité décroissante 0.05-0.01 |

#### États visuels

| État | Couleur | RGB | Comportement |
|------|---------|-----|--------------|
| **rest** | Bleu cyan | `#00d4ff` (0,212,255) | Pulse lent 2s, particules lentes |
| **listening** | Orange | `#ffaa00` (255,170,0) | Pulse rapide 1s, barres vocales actives |
| **working** | Violet magenta | `#ff00ff` (255,0,255) | Pulse très rapide 0.5s, data streams accélérés |
| **speaking** | Vert émeraude | `#00ff88` (0,255,136) | Ondes sonores concentriques, barres max amplitude |

#### Overlay texte

**Label supérieur** : état actuel ("EN VEILLE", "ÉCOUTE", "TRAITEMENT", "PAROLE")
- Police : Courier New, monospace, 13px, letterspacing 6px
- Couleur : synchronisée avec l'état
- Animation : blink opacity 0.3-1.0, 3s cycle

**Transcription temps réel** (ajout futur) :
- Texte Vosk affiché en bas pendant l'écoute
- Réponse Jarvis affichée pendant speaking
- Fade in/out automatique

---

### Rendu performances

**Canvas 2D** (utilisé actuellement) :
- 60 FPS stable sur CPU intégré
- ~25 particules + 10 data streams + anneaux
- Pas de drop de frames sous 10% CPU

**Optimisations** :
- `requestAnimationFrame` natif
- Pas de calculs matriciels lourds
- Opérations de blend GPU-accélérées via compositing
- Trails limités à 5 frames par particule

---

## Pipeline vocal temps réel

### 1. Wake word detection (permanent, passif)

```
Micro → sounddevice (16kHz mono)
      → Vosk KaldiRecognizer (vocab: ["jarvis", "hey jarvis", "ok jarvis"])
      → Détection → set_ui_state("listening")
```

**Performance** : latence ~50ms, CPU ~2-3%

---

### 2. Écoute commande (timeout adaptatif)

```
Micro → sounddevice (16kHz mono)
      → Vosk KaldiRecognizer (mode commandes: vocab 20 mots)
      ├─ Match → exécution immédiate
      └─ No match → bascule vocab libre → LLM
```

**Timeouts** :
- `silence_timeout` : 0.5s (commandes), 1.2s (conversation)
- `total_timeout` : 8s max

**Performance** :
- Commande reconnue : ~100-150ms
- Fallback vocab libre : ~200-300ms

---

### 3. Exécution (commandes système ou LLM)

#### Commandes système
```
executor.py normalize(text)
         → pattern matching (17 commandes numérotées + ~40 variantes naturelles)
         → subprocess.Popen (non-bloquant)
         → réponse texte immédiate
```

**Exemples** :
- "commande 6" → volume +5% → ~10ms
- "capture écran" → spectacle → ~150ms
- "ouvre firefox" → subprocess → ~200ms

#### LLM conversationnel
```
llama-cpp-python Llama(model, stream=True)
    → génération token par token
    → buffer jusqu'à phrase complète (. ! ?)
    → speak(phrase) pendant génération suite
```

**Performance streaming** :
- Première token : ~150-200ms
- Tokens suivants : ~30-50ms/token
- Utilisateur entend la première phrase après ~500ms au lieu de 3s

---

### 4. Synthèse vocale (TTS)

#### Mode cache (phrases fixes)
```
Phrases pré-générées au démarrage :
  ["Oui.", "Je vous écoute.", "Je n'ai pas compris.", ...]
→ stockées en RAM (dict phrase → bytes WAV)
→ lecture directe via aplay
```

**Performance** : ~50ms lecture, zéro génération

#### Mode pipe direct (phrases dynamiques)
```
text → piper --output-raw stdout
     → pipe direct dans aplay stdin
     → pas de fichier temporaire
```

**Performance** : ~800ms génération+lecture (vs 1.5-2s avec fichier temp)

---

## Architecture modulaire

```
jarvis/
├── main.py                      # Boucle principale, orchestration
│
├── brain/
│   └── llm.py                   # LLM llama-cpp-python + streaming
│       ├── Llama(model_path)    # Chargement modèle GGUF
│       ├── ask_stream()         # Génération token par token
│       └── history[]            # Contexte N derniers échanges
│
├── commands/
│   └── executor.py              # Reconnaissance + exécution
│       ├── normalize()          # Suppression accents, apostrophes
│       ├── NUMBERED_COMMANDS[]  # 17 commandes numérotées
│       ├── APPLICATIONS{}       # Apps lancables
│       └── execute_command()    # Pattern matching + subprocess
│
├── interface/
│   ├── jarvis_orb.html          # Orbe canvas 2D animée
│   ├── orb_window.py            # Fenêtre PyQt5 frameless
│   │   ├── OrbWindow            # QMainWindow transparent
│   │   ├── change_state()       # Thread-safe state sync
│   │   └── SilentPage           # QWebEnginePage sans logs JS
│   └── server.py                # Serveur HTTP/SSE (mode navigateur, non utilisé)
│
├── models/
│   ├── gguf/                    # Modèle LLM llama.cpp
│   │   └── qwen2.5-0.5b-instruct-q4_k_m.gguf
│   ├── piper/                   # Modèle TTS ONNX
│   │   ├── fr_FR-gilles-low.onnx
│   │   └── fr_FR-gilles-low.onnx.json
│   └── vosk/                    # Modèle STT Kaldi
│       └── vosk-model-small-fr-0.22/
│
├── security/
│   └── confirmation.py          # Confirmation vocale actions dangereuses
│       ├── ask_confirmation_vocal()  # Vosk vocab oui/non
│       └── is_dangerous()            # Détection commandes à risque
│
├── tts/
│   └── speak.py                 # Synthèse vocale Piper
│       ├── AUDIO_CACHE{}        # Dict phrase → bytes WAV
│       ├── _generate_cache()    # Pré-génération au démarrage
│       └── speak()              # Cache hit ou pipe direct
│
├── voice/
│   ├── stt.py                   # Reconnaissance Vosk
│   │   ├── STT(model, vocab)    # Mode libre ou restreint
│   │   └── listen()             # Timeout adaptatif
│   └── wakeword.py              # Détection mot-clé
│       └── WakeWordDetector     # Vocab restreint "jarvis"
│
└── config.py                    # Configuration centralisée
    ├── BASE_DIR                 # Chemins absolus
    ├── VOSK_MODEL_PATH
    ├── PIPER_MODEL_PATH
    ├── GGUF_MODEL_PATH
    ├── OLLAMA_URL (legacy)
    └── ASSISTANT_NAME
```

---

## Communication inter-threads

```
Thread principal (Qt)
    ├─ OrbWindow.change_state(state)  # Thread-safe via pyqtSignal
    └─ QApplication.exec_()            # Boucle événements Qt

Thread daemon (Jarvis core)
    ├─ WakeWordDetector.wait()         # Bloquant, détection passive
    ├─ STT.listen()                    # Bloquant, timeout
    ├─ LLM.ask_stream(on_sentence=)    # Callback speak() par phrase
    └─ set_ui_state() → orb_window.change_state()
```

**Mécanisme** : `pyqtSignal` pour passer du thread Python au thread Qt de manière thread-safe.

---

## Optimisations clés

### 1. Modèle Vosk partagé
Un seul `vosk.Model` chargé en RAM, passé par référence à `WakeWordDetector` et `STT` → économise 300 Mo RAM.

### 2. Vocabulaire restreint commandes
Vosk avec vocab de 20 mots (commandes + nombres) → précision +15%, latence -40%.

### 3. Cache audio TTS
10 phrases fixes pré-générées (150 Ko RAM) → latence divisée par 15.

### 4. Streaming LLM + TTS couplés
Jarvis commence à parler après 500ms au lieu de 3s — impression de fluidité.

### 5. Piper pipe direct
Suppression du fichier WAV temporaire → -1s par réponse.

### 6. Normalisation Vosk agressive
Suppression accents, apostrophes, doublons → taux de reconnaissance +20%.

### 7. PyQt5 avec système packages
Pas de recompilation de Qt dans le venv → installation 10× plus rapide.

---

## Roadmap optimisation avancée

### Phase 2 — Whisper.cpp
Remplacer Vosk par Whisper.cpp `tiny` ou `base` français.

**Gains attendus** :
- Précision : 75% → 92%
- Latence : identique (~200ms)
- Robustesse : meilleure gestion du bruit ambiant

### Phase 3 — TTS Kokoro
Remplacer Piper par Kokoro-82M (modèle léger, streaming natif).

**Gains attendus** :
- Qualité voix : +30%
- Latence : ~150ms (vs 800ms Piper)
- Streaming : génération chunk par chunk

### Phase 4 — LLM quantizé Q3/Q2
Tester Qwen2.5-1.5B en quantization Q3_K_M.

**Gains attendus** :
- Qualité réponses : +40%
- RAM : +500 Mo (acceptable)
- Latence : +50ms (négligeable avec streaming)

### Phase 5 — VAD (Voice Activity Detection)
Ajouter Silero VAD avant Vosk pour détecter la fin de phrase plus tôt.

**Gains attendus** :
- Latence perçue : -200ms
- Précision découpage : meilleure

---

## Métriques de performance cibles

| Métrique | Valeur actuelle | Cible optimale |
|----------|----------------|----------------|
| Wake word → "Oui" | ~300ms | < 200ms |
| Commande → action | ~800ms | < 500ms |
| Question → 1ère syllabe | ~1.5s | < 500ms |
| Phrase complète TTS | ~2s | < 1.2s |
| RAM totale | ~1.2 Go | < 2 Go |
| CPU idle | ~8% | < 5% |
| CPU écoute | ~15% | < 10% |
| CPU génération LLM | ~80% | 60-80% (acceptable) |

---

## Dépendances Python

```
vosk==0.3.45
sounddevice==0.4.6
requests==2.31.0
llama-cpp-python==0.3.35
piper-tts==1.2.0
PyQt5==5.15.10 (système)
PyQtWebEngine==5.15.6 (système)
huggingface-hub==0.20.0
```

---

## Modèles requis

| Modèle | Taille | Source | Usage |
|--------|--------|--------|-------|
| vosk-model-small-fr-0.22 | 41 Mo | alphacephei.com/vosk | STT français |
| fr_FR-gilles-low.onnx | 18 Mo | Hugging Face rhasspy/piper-voices | TTS voix masculine |
| qwen2.5-0.5b-instruct-q4_k_m.gguf | 400 Mo | Hugging Face Qwen/Qwen2.5-0.5B-Instruct-GGUF | LLM conversationnel |

**Total disque** : ~460 Mo

---

## Compatibilité

- **OS** : Linux (testé Ubuntu 24.04, Debian 12, Arch)
- **Architecture** : x86_64 (Intel/AMD)
- **Python** : 3.10, 3.11, 3.12
- **Desktop** : KDE Plasma, GNOME, XFCE (tout environnement avec PulseAudio)
- **GPU** : non requis (CPU pur, OpenBLAS pour accélération matricielle)

---

Fait avec Python · 100% local · Zéro cloud · Zéro tracking
