import os

# ── Chemins absolus ───────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VOSK_MODEL_PATH  = os.path.join(BASE_DIR, "models", "vosk", "vosk-model-small-fr-0.22")
PIPER_MODEL_PATH = os.path.join(BASE_DIR, "models", "piper", "fr_FR-gilles-low.onnx")
PIPER_CONFIG_PATH= os.path.join(BASE_DIR, "models", "piper", "fr_FR-gilles-low.onnx.json")
GGUF_MODEL_PATH  = os.path.join(BASE_DIR, "models", "gguf", "qwen2.5-0.5b-instruct-q4_k_m.gguf")
LOGS_DIR         = os.path.join(BASE_DIR, "logs")

# ── Audio ─────────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16000

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_N_CTX        = 2048   # Fenêtre de contexte
LLM_N_THREADS    = 4      # Threads CPU (adapter au nombre de cœurs)
LLM_MAX_TOKENS   = 150    # Tokens max par réponse
LLM_HISTORY_SIZE = 6      # Nombre de tours de conversation mémorisés

# ── STT ───────────────────────────────────────────────────────────────────────
STT_SILENCE_TIMEOUT_CMD  = 0.6   # secondes — mode commande (vocab restreint)
STT_SILENCE_TIMEOUT_FREE = 1.2   # secondes — mode conversation libre
STT_TOTAL_TIMEOUT        = 8     # secondes — timeout total écoute

# ── Assistant ─────────────────────────────────────────────────────────────────
ASSISTANT_NAME = "jarvis"

SYSTEM_PROMPT = (
    "Tu es Jarvis, un assistant personnel sobre, poli et concis. "
    "Tu réponds TOUJOURS en français. "
    "Tes réponses font au maximum deux phrases courtes. "
    "Tu ne dis jamais 'En tant qu'IA' ou 'Je suis un modèle de langage'."
)
