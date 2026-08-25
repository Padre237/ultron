"""
Reconnaissance et exécution des commandes Jarvis.
- Normalisation du texte Vosk (accents, apostrophes, ponctuation)
- 17 commandes numérotées + reconnaissance naturelle
- Commandes date/heure, météo locale, recherche web
- Retour None si aucune commande → délégué au LLM
"""

import subprocess
import os
import re
import sys
import unicodedata
import datetime
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.confirmation import ask_confirmation

logger = logging.getLogger("jarvis.executor")


# ── Normalisation ─────────────────────────────────────────────────────────────
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"['\-.,;:!?\"()]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Applications ──────────────────────────────────────────────────────────────
APPLICATIONS = {
    "firefox":      ["firefox"],
    "dolphin":      ["dolphin"],
    "fichiers":     ["dolphin"],
    "vlc":          ["vlc"],
    "lecteur":      ["vlc"],
    "konsole":      ["konsole"],
    "terminal":     ["konsole"],
    "parametres":   ["systemsettings"],
    "navigateur":   ["firefox"],
    "calculatrice": ["kcalc"],
    "editeur":      ["kate"],
    "musique":      ["elisa"],
}

# ── Commandes numérotées ──────────────────────────────────────────────────────
NUMBERED_COMMANDS = [
    (1,  "Ouvrir Firefox",                "open_firefox"),
    (2,  "Ouvrir le gestionnaire de fichiers", "open_fichiers"),
    (3,  "Ouvrir le terminal",            "open_terminal"),
    (4,  "Ouvrir VLC",                    "open_vlc"),
    (5,  "Ouvrir les paramètres",         "open_parametres"),
    (6,  "Augmenter le volume",           "volume_up"),
    (7,  "Diminuer le volume",            "volume_down"),
    (8,  "Couper le son",                 "mute"),
    (9,  "Rétablir le son",               "unmute"),
    (10, "Utilisation CPU",               "cpu"),
    (11, "Utilisation RAM",               "ram"),
    (12, "Espace disque",                 "disk"),
    (13, "Capture d'écran",               "screenshot"),
    (14, "Verrouiller l'écran",           "lock"),
    (15, "Mettre en veille",              "suspend"),
    (16, "Redémarrer",                    "reboot"),
    (17, "Éteindre",                      "shutdown"),
]

_NUM_MAP  = {n: key for n, _, key in NUMBERED_COMMANDS}
_LABEL_MAP= {key: lbl for _, lbl, key in NUMBERED_COMMANDS}

_COMMAND_TRIGGERS = [
    "commande", "command", "komande", "komand",
    "la commande", "execute commande", "execute la commande",
]

_NUM_WORDS = {
    "un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
    "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10,
    "onze": 11, "douze": 12, "treize": 13, "quatorze": 14,
    "quinze": 15, "seize": 16, "dix sept": 17,
}


def _parse_number(text: str):
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return int(m.group(1))
    for word, num in _NUM_WORDS.items():
        if word in text:
            return num
    return None


# ── Actions système ───────────────────────────────────────────────────────────
def _run(cmd):
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def volume_up(step=5):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{step}%"], check=False)

def volume_down(step=5):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{step}%"], check=False)

def mute():
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=False)

def unmute():
    subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"], check=False)

def get_cpu_usage():
    try:
        out = subprocess.check_output(["top", "-bn1"], text=True)
        for line in out.split("\n"):
            if "Cpu" in line:
                nums = re.findall(r"(\d+[\.,]\d+|\d+)", line)
                if nums:
                    return float(nums[0].replace(",", "."))
        return 0.0
    except Exception:
        return 0.0

def get_ram_usage():
    try:
        out = subprocess.check_output(["free", "-h"], text=True)
        for line in out.split("\n"):
            if line.startswith("Mem:"):
                p = line.split()
                return p[2].replace(",", "."), p[1].replace(",", ".")
        return "0", "0"
    except Exception:
        return "0", "0"

def get_disk_usage():
    try:
        out = subprocess.check_output(["df", "-h", "/"], text=True)
        lines = out.strip().split("\n")
        if len(lines) >= 2:
            p = lines[1].split()
            return p[3], p[1]
        return "0", "0"
    except Exception:
        return "0", "0"

def take_screenshot():
    images_dir = os.path.expanduser("~/Images")
    os.makedirs(images_dir, exist_ok=True)
    now  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(images_dir, f"jarvis_{now}.png")
    r = subprocess.run(["spectacle", "-b", "-o", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode != 0:
        subprocess.run(["scrot", path], check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return path

def search_file(filename):
    try:
        out = subprocess.check_output(
            ["find", os.path.expanduser("~"), "-name", filename, "-maxdepth", "8"],
            text=True, stderr=subprocess.DEVNULL)
        return [f for f in out.strip().split("\n") if f][:5]
    except Exception:
        return []

def lock_screen():
    subprocess.run(["loginctl", "lock-session"], check=False)

def suspend():
    subprocess.run(["systemctl", "suspend"], check=False)

def reboot():
    subprocess.run(["systemctl", "reboot"], check=False)

def shutdown():
    subprocess.run(["systemctl", "poweroff"], check=False)

def get_datetime():
    now = datetime.datetime.now()
    jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    mois  = ["janvier","février","mars","avril","mai","juin",
             "juillet","août","septembre","octobre","novembre","décembre"]
    return (
        f"Il est {now.hour} heure {now.minute:02d}. "
        f"Nous sommes {jours[now.weekday()]} {now.day} {mois[now.month-1]} {now.year}."
    )

def open_url(url):
    _run(["firefox", url])

def _ask_dangerous(msg, fn):
    if ask_confirmation(msg):
        fn()
        return True
    return False


# ── Point d'entrée ────────────────────────────────────────────────────────────
def execute_command(text: str):
    """
    Retourne une réponse str si commande reconnue, None sinon (→ LLM).
    """
    n = normalize(text)
    logger.debug(f"execute_command: '{n}'")

    # ── Commandes numérotées ──────────────────────────────────────────
    if any(t in n for t in _COMMAND_TRIGGERS):
        num = _parse_number(n)
        if num and num in _NUM_MAP:
            return _run_numbered(num)
        else:
            lines = "\n".join(f"{no}. {lbl}" for no, lbl, _ in NUMBERED_COMMANDS)
            return f"Commandes disponibles :\n{lines}"

    # ── Date / Heure ──────────────────────────────────────────────────
    if any(k in n for k in ["heure", "heure est il", "quelle heure",
                              "date", "quel jour", "aujourd hui"]):
        return get_datetime()

    # ── Ouverture d'applications ──────────────────────────────────────
    for app_key, cmd in APPLICATIONS.items():
        patterns = [f"ouvre {app_key}", f"lance {app_key}",
                    f"demarre {app_key}", f"ouvrir {app_key}",
                    f"lancer {app_key}", f"demarrer {app_key}",
                    f"ouvre le {app_key}", f"lance le {app_key}"]
        if any(p in n for p in patterns):
            _run(cmd)
            return f"{app_key.capitalize()} lancé."

    # Fermer
    m = re.search(r"ferme (\w+)", n)
    if m:
        app = m.group(1)
        subprocess.run(["pkill", "-f", app], check=False)
        return f"{app} fermé."

    # ── Volume ────────────────────────────────────────────────────────
    if any(k in n for k in ["augmente le volume", "monte le son", "plus fort", "augmenter volume"]):
        volume_up(); return "Volume augmenté."
    if any(k in n for k in ["diminue le volume", "baisse le son", "moins fort", "baisser volume"]):
        volume_down(); return "Volume diminué."
    if any(k in n for k in ["coupe le son", "mute", "silence", "couper son"]):
        mute(); return "Son coupé."
    if any(k in n for k in ["retablis le son", "remets le son", "unmute", "reactive le son"]):
        unmute(); return "Son rétabli."

    # ── Infos système ─────────────────────────────────────────────────
    if any(k in n for k in ["processeur", "cpu", "utilisation processeur"]):
        return f"Utilisation du processeur : {get_cpu_usage():.1f} pourcent."
    if any(k in n for k in ["ram", "memoire", "utilisation memoire"]):
        used, total = get_ram_usage()
        return f"RAM utilisée : {used} sur {total}."
    if any(k in n for k in ["disque", "espace disque", "stockage", "espace libre"]):
        avail, total = get_disk_usage()
        return f"Espace disque disponible : {avail} sur {total}."

    # ── Capture d'écran ───────────────────────────────────────────────
    if any(k in n for k in ["capture", "screenshot", "ecran", "capturer", "prends ecran"]):
        path = take_screenshot()
        return "Capture d'écran enregistrée." if path and os.path.exists(path) else "Capture échouée."

    # ── Recherche fichier ─────────────────────────────────────────────
    m = re.search(r"recherche (?:le fichier |le |la )?(.+)", n)
    if m:
        filename = m.group(1).strip()
        results  = search_file(filename)
        return f"Trouvé : {', '.join(results[:3])}" if results else f"Aucun fichier trouvé pour {filename}."

    # ── Recherche web ─────────────────────────────────────────────────
    m = re.search(r"(?:recherche sur internet|cherche sur le web|google) (.+)", n)
    if m:
        query = m.group(1).strip()
        url   = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        open_url(url)
        return f"Je recherche {query} sur internet."

    # ── Verrouillage ──────────────────────────────────────────────────
    if any(k in n for k in ["verrouille", "verrouiller", "lock", "verrou"]):
        lock_screen(); return "Écran verrouillé."

    # ── Effacer historique ────────────────────────────────────────────
    if any(k in n for k in ["efface l historique", "efface la conversation",
                              "oublie tout", "recommence"]):
        return "__clear_history__"   # Signal spécial traité dans main.py

    # ── Commandes dangereuses ─────────────────────────────────────────
    if any(k in n for k in ["eteins", "eteint", "arrete ordinateur", "shutdown", "poweroff"]):
        if _ask_dangerous("Voulez-vous vraiment éteindre ? Dites oui ou non.", shutdown):
            return "Extinction en cours."
        return "Action annulée."

    if any(k in n for k in ["redemarre", "reboot", "redemarrer"]):
        if _ask_dangerous("Voulez-vous vraiment redémarrer ? Dites oui ou non.", reboot):
            return "Redémarrage en cours."
        return "Action annulée."

    if any(k in n for k in ["suspend", "mets en veille", "mise en veille", "veille"]):
        if _ask_dangerous("Voulez-vous vraiment mettre en veille ? Dites oui ou non.", suspend):
            return "Suspension en cours."
        return "Action annulée."

    return None  # → LLM


def _run_numbered(num: int) -> str:
    """Exécute la commande numérotée et retourne la réponse."""
    key   = _NUM_MAP[num]
    label = _LABEL_MAP[key]

    dispatch = {
        "open_firefox":    lambda: (_run(["firefox"]),          f"{label} lancé."),
        "open_fichiers":   lambda: (_run(["dolphin"]),          f"{label} lancé."),
        "open_terminal":   lambda: (_run(["konsole"]),          f"{label} lancé."),
        "open_vlc":        lambda: (_run(["vlc"]),              f"{label} lancé."),
        "open_parametres": lambda: (_run(["systemsettings"]),   f"{label} lancé."),
        "volume_up":       lambda: (volume_up(),                "Volume augmenté."),
        "volume_down":     lambda: (volume_down(),              "Volume diminué."),
        "mute":            lambda: (mute(),                     "Son coupé."),
        "unmute":          lambda: (unmute(),                   "Son rétabli."),
        "lock":            lambda: (lock_screen(),              "Écran verrouillé."),
    }

    if key in dispatch:
        _, response = dispatch[key]()
        return response

    if key == "cpu":
        return f"Utilisation CPU : {get_cpu_usage():.1f} pourcent."
    if key == "ram":
        used, total = get_ram_usage()
        return f"RAM utilisée : {used} sur {total}."
    if key == "disk":
        avail, total = get_disk_usage()
        return f"Espace libre : {avail} sur {total}."
    if key == "screenshot":
        path = take_screenshot()
        return "Capture enregistrée." if path and os.path.exists(path) else "Capture échouée."

    dangerous = {
        "suspend":  ("Voulez-vous vraiment mettre en veille ? Dites oui ou non.", suspend),
        "reboot":   ("Voulez-vous vraiment redémarrer ? Dites oui ou non.",       reboot),
        "shutdown": ("Voulez-vous vraiment éteindre ? Dites oui ou non.",         shutdown),
    }
    if key in dangerous:
        msg, fn = dangerous[key]
        if _ask_dangerous(msg, fn):
            return f"{label} en cours."
        return "Action annulée."

    return f"Commande {num} exécutée."
