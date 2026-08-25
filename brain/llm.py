"""
LLM local via llama-cpp-python.
- Chargement direct du modèle GGUF (zéro overhead réseau)
- Génération en streaming token par token
- Historique de conversation configurable
- Callback par phrase complète pour couplage TTS
"""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logger = logging.getLogger("jarvis.llm")


class LLM:
    def __init__(self,
                 model_path: str = None,
                 n_ctx: int = None,
                 n_threads: int = None,
                 history_size: int = None):

        self.model_path   = model_path   or config.GGUF_MODEL_PATH
        self.n_ctx        = n_ctx        or config.LLM_N_CTX
        self.n_threads    = n_threads    or config.LLM_N_THREADS
        self.history_size = history_size or config.LLM_HISTORY_SIZE
        self.history      = []   # [(role, content), ...]
        self._llm         = None

    def load(self):
        """Charge le modèle GGUF en mémoire."""
        from llama_cpp import Llama
        logger.info(f"Chargement du modèle LLM : {self.model_path}")
        self._llm = Llama(
            model_path  = self.model_path,
            n_ctx       = self.n_ctx,
            n_threads   = self.n_threads,
            verbose     = False,
        )
        logger.info("Modèle LLM chargé.")

    def _build_prompt(self, user_input: str) -> str:
        """Construit le prompt avec historique au format ChatML."""
        lines = [f"<|im_start|>system\n{config.SYSTEM_PROMPT}<|im_end|>"]
        for role, content in self.history[-self.history_size:]:
            lines.append(f"<|im_start|>{role}\n{content}<|im_end|>")
        lines.append(f"<|im_start|>user\n{user_input}<|im_end|>")
        lines.append("<|im_start|>assistant\n")
        return "\n".join(lines)

    def _update_history(self, user_input: str, response: str):
        """Ajoute l'échange à l'historique, tronque si nécessaire."""
        self.history.append(("user",      user_input))
        self.history.append(("assistant", response))
        # Garder uniquement les N derniers tours
        max_entries = self.history_size * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]

    def ask(self, user_input: str) -> str:
        """
        Génère une réponse complète (non streaming).
        Retourne le texte complet.
        """
        if not self._llm:
            self.load()

        prompt = self._build_prompt(user_input)
        result = self._llm(
            prompt,
            max_tokens  = config.LLM_MAX_TOKENS,
            stop        = ["<|im_end|>", "<|im_start|>"],
            echo        = False,
        )
        response = result["choices"][0]["text"].strip()
        self._update_history(user_input, response)
        return response

    def ask_stream(self, user_input: str, on_sentence):
        """
        Génère en streaming et appelle on_sentence(texte) dès qu'une
        phrase complète est prête. Permet de parler pendant la génération.

        :param user_input: question de l'utilisateur
        :param on_sentence: callable(str) appelé pour chaque phrase
        """
        if not self._llm:
            self.load()

        prompt   = self._build_prompt(user_input)
        buffer   = ""
        full_response = ""

        for chunk in self._llm(
            prompt,
            max_tokens  = config.LLM_MAX_TOKENS,
            stop        = ["<|im_end|>", "<|im_start|>"],
            echo        = False,
            stream      = True,
        ):
            token = chunk["choices"][0]["text"]
            buffer        += token
            full_response += token

            # Déclencher dès qu'une phrase est complète
            if any(buffer.rstrip().endswith(p) for p in (".", "!", "?", "…")):
                sentence = buffer.strip()
                if sentence:
                    logger.debug(f"Phrase prête : {sentence}")
                    on_sentence(sentence)
                buffer = ""

        # Résidu éventuel sans ponctuation finale
        if buffer.strip():
            on_sentence(buffer.strip())

        self._update_history(user_input, full_response.strip())

    def clear_history(self):
        """Efface l'historique de conversation."""
        self.history.clear()
        logger.info("Historique effacé.")
