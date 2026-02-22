"""
MemoriaCoralApp v4.0 — Python
Sistema de Memoria Persistente Multi-IA — Pensamiento Coral / GCH
"""

import threading
import json
import os
import time
import sys
from datetime import datetime

# Ocultar consola en Windows cuando se ejecuta como .exe compilado
if sys.platform == "win32" and getattr(sys, 'frozen', False):
    import ctypes
    ctypes.windll.user32.ShowWindow(
        ctypes.windll.kernel32.GetConsoleWindow(), 0
    )

import requests
import customtkinter as ctk
from tkinter import messagebox, StringVar
import tkinter as tk

# ─────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkYnpqYXBzaG9tYXR3eWFzbWlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4ODAzNzMsImV4cCI6MjA3OTQ1NjM3M30.AmHDH1dmJ3qme8VYN1EU3zjf7zZAKESal5NXWhX-KMk"
BASE      = "https://jdbzjapshomatwyasmig.supabase.co"
URL_READ  = BASE + "/functions/v1/memory-read"
URL_WRITE = BASE + "/functions/v1/memory-write"
URL_RPC   = BASE + "/rest/v1/rpc"
HEADERS   = {
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
    "apikey": ANON_KEY
}

IA_FALLBACK  = ["user","claude","gpt4","copilot","gemini","kimi","grok","deepseek","mistral"]
ENTRY_TYPES  = ["fact","summary","entity","assertion","flag","conflict","context","instruction"]
KEYWORDS_ESTRATEGICAS = [
    "decisión","principio","fase","token","nodo","arquitectura",
    "protocolo","embedding","soberanía","causalidad","coral","tca","pip"
]

COLORS = {
    "bg":        "#0A0A14",
    "panel":     "#13141F",
    "surface":   "#1C1E2E",
    "accent1":   "#00D4B4",
    "accent2":   "#5B8CFF",
    "accent3":   "#C44E78",
    "accent4":   "#7B3DB5",
    "text":      "#DCE1EB",
    "muted":     "#636B80",
    "input":     "#1E2132",
    "ok":        "#00C88C",
    "error":     "#DC4B5F",
    "warning":   "#E8A838",
}

AUTHOR_COLORS = {
    "user":     "#00D4B4",
    "claude":   "#5B8CFF",
    "gpt4":     "#00C88C",
    "copilot":  "#C44E78",
    "gemini":   "#E8A838",
    "kimi":     "#7B3DB5",
    "grok":     "#DC4B5F",
    "deepseek": "#FF8C42",
    "mistral":  "#A0E878",
}

CONFIG_FILE = "config.json"
KEY_FILE    = "config.key"

# ─────────────────────────────────────────────────────────
# CONFIGURACIÓN — Cifrado de config.json
# ─────────────────────────────────────────────────────────
def get_cipher():
    from cryptography.fernet import Fernet
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    with open(KEY_FILE, "rb") as f:
        return Fernet(f.read())

def guardar_config(github_token, repo, rama):
    from cryptography.fernet import Fernet
    cipher = get_cipher()
    datos = {
        "repo": repo,
        "rama": rama,
        "token": cipher.encrypt(github_token.encode()).decode()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(datos, f)

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        cipher = get_cipher()
        with open(CONFIG_FILE, "r") as f:
            datos = json.load(f)
        datos["token"] = cipher.decrypt(datos["token"].encode()).decode()
        return datos
    except Exception:
        return None

# ─────────────────────────────────────────────────────────
# MODELO DE EMBEDDINGS — carga diferida en hilo
# ─────────────────────────────────────────────────────────
EMBEDDING_MODEL = None
_model_loading   = False
_model_ready     = threading.Event()

def _cargar_modelo():
    global EMBEDDING_MODEL, _model_loading
    _model_loading = True
    try:
        from sentence_transformers import SentenceTransformer
        import sys, os
        if getattr(sys, 'frozen', False):
            # Dentro del .exe: ruta explícita al snapshot empaquetado
            _model_path = os.path.join(
                sys._MEIPASS,
                "huggingface_cache",
                "models--sentence-transformers--all-MiniLM-L6-v2",
                "snapshots",
                "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
            )
        else:
            _model_path = 'all-MiniLM-L6-v2'
        EMBEDDING_MODEL = SentenceTransformer(_model_path)
    except Exception as e:
        print(f"[ERROR modelo] {e}")
    finally:
        _model_loading = False
        _model_ready.set()

def iniciar_carga_modelo():
    t = threading.Thread(target=_cargar_modelo, daemon=True)
    t.start()

def generar_embedding(field_key, entry_type, field_value, ia_author=""):
    """
    v4.1 — Concatenación semántica incluye ia_author:
    [{ia_author}] {field_key} | {entry_type} | {field_value}
    Permite detectar consenso multi-IA (vectores similares, autores distintos)
    y disenso (mismo field_key, vectores divergentes entre autores).
    """
    _model_ready.wait(timeout=300)
    if EMBEDDING_MODEL is None:
        return None
    prefix = f"[{ia_author}] " if ia_author else ""
    texto = f"{prefix}{field_key} | {entry_type} | {field_value}"
    return EMBEDDING_MODEL.encode(texto).tolist()

# ─────────────────────────────────────────────────────────
# API SUPABASE
# ─────────────────────────────────────────────────────────
def api_leer_memoria():
    try:
        r = requests.get(URL_READ, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except Exception as e:
        return None, str(e)

def api_escribir_entrada(payload):
    try:
        r = requests.post(URL_WRITE, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

def api_get_ias():
    try:
        r = requests.post(URL_RPC + "/get_ia_authors", headers=HEADERS, json={}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return [x.get("ia_author", x) if isinstance(x, dict) else x for x in data]
    except Exception:
        pass
    return IA_FALLBACK[:]

def api_add_ia(nombre):
    try:
        r = requests.post(URL_RPC + "/add_ia_author", headers=HEADERS, json={"p_ia_author": nombre}, timeout=10)
        if r.status_code in (200, 201):
            return True, None
        return False, r.text
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────────────────
# RECÁLCULO MASIVO DE EMBEDDINGS (v4.1)
# ─────────────────────────────────────────────────────────
def api_supersede_y_reescribir(entrada_original, nuevo_embedding):
    """
    Protocolo append-only: crea nueva entrada con embedding v4.1.
    Incluye supersedes_id para que la Edge Function marque la anterior
    como is_superseded=true si lo soporta, o simplemente añade la nueva.
    """
    payload = {
        "ia_author":        entrada_original.get("ia_author"),
        "entry_type":       entrada_original.get("entry_type"),
        "field_key":        entrada_original.get("field_key"),
        "field_value":      entrada_original.get("field_value"),
        "confidence_score": entrada_original.get("confidence_score", 0.8),
        "supersedes_id":    entrada_original.get("id"),
        "embedding":        nuevo_embedding,
    }
    return api_escribir_entrada(payload)

# ─────────────────────────────────────────────────────────
# API GITHUB
# ─────────────────────────────────────────────────────────
def github_probar_conexion(token, repo_nombre):
    try:
        from github import Github
        g = Github(token)
        repo = g.get_repo(repo_nombre)
        return True, repo.full_name
    except Exception as e:
        return False, str(e)

def github_subir_archivo(token, repo_nombre, rama, ruta, contenido, mensaje_commit):
    try:
        from github import Github
        g = Github(token)
        repo = g.get_repo(repo_nombre)
        try:
            archivo = repo.get_contents(ruta, ref=rama)
            repo.update_file(ruta, mensaje_commit, contenido, archivo.sha, branch=rama)
        except Exception:
            repo.create_file(ruta, mensaje_commit, contenido, branch=rama)
        return True, None
    except Exception as e:
        return False, str(e)

# ─────────────────────────────────────────────────────────
# CÁLCULO TCA
# ─────────────────────────────────────────────────────────
def calcular_score_sistema(texto, titulo, es_estrategica):
    score = 0.0
    if len(texto) > 500:   score += 0.2
    if len(texto) > 1500:  score += 0.1
    texto_lower = texto.lower()
    kw = sum(1 for k in KEYWORDS_ESTRATEGICAS if k in texto_lower)
    score += min(kw * 0.1, 0.4)
    if es_estrategica:     score += 0.3
    return min(score, 1.0)

def slug(titulo):
    import re
    s = titulo.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return s[:50]

def generar_markdown_tca(titulo, ia, score_u, score_s, score_f, texto, ts, es_estrategica):
    fecha = datetime.now().strftime("%Y-%m-%d")
    dec = "si" if es_estrategica else "no"
    return f"""---
fecha: {fecha}
titulo: {titulo}
ia_participante: {ia}
score_usuario: {score_u:.2f}
score_sistema: {score_s:.2f}
score_final: {score_f:.2f}
tca_usuario: tca_usuario_{ts}
tca_ia: tca_ia_{ts}
decision_estrategica: {dec}
---

# {titulo}

## Conversación

{texto}

---

## Tokens Causales Generados

| Token | Autor | Caducidad | Score |
|---|---|---|---|
| tca_usuario_{ts} | user | 3 años | {score_f:.2f} |
| tca_ia_{ts} | {ia} | 3 años | {score_f:.2f} |
"""

# ─────────────────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────────────────
def make_btn(parent, text, command, color=None, text_color=None, width=120):
    c = color or COLORS["accent1"]
    tc = text_color or COLORS["bg"]
    btn = ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=c, hover_color=_lighten(c),
        text_color=tc, corner_radius=10,
        font=("Segoe UI Variable", 9, "bold"),
        width=width, height=32
    )
    return btn

def _lighten(hex_color, factor=0.2):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    r = min(255, int(r + (255-r)*factor))
    g = min(255, int(g + (255-g)*factor))
    b = min(255, int(b + (255-b)*factor))
    return f"#{r:02x}{g:02x}{b:02x}"

def scrollable_text(parent, **kwargs):
    frame = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=8)
    txt = tk.Text(
        frame,
        bg=COLORS["surface"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        font=("Consolas", 9),
        wrap="word",
        **kwargs
    )
    sb = ctk.CTkScrollbar(frame, command=txt.yview, width=8, fg_color=COLORS["surface"],
                          button_color=COLORS["accent1"], button_hover_color=COLORS["accent2"])
    txt.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    txt.pack(side="left", fill="both", expand=True, padx=2, pady=2)
    return frame, txt

# ─────────────────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────────────────
class MemoriaCoralApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("MemoriaCoralApp v4.0")
        self.geometry("820x720")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        # Icono — ruta compatible con .exe y Python directo
        try:
            import sys, os
            if getattr(sys, 'frozen', False):
                _ico = os.path.join(sys._MEIPASS, "MemoriaCoral.ico")
            else:
                _ico = r"C:\Users\Oscar Fernandez\Desktop\Memoria Coral\Memoria Coral\MemoriaCoral.ico"
            if os.path.exists(_ico):
                self.iconbitmap(_ico)
        except Exception:
            pass

        self._centrar()
        self._build_ui()
        self._vista_actual = None
        self._ia_list = IA_FALLBACK[:]

        # Cargar modelo en background
        iniciar_carga_modelo()
        self._monitorear_modelo()

        # Mostrar vista inicial
        self.mostrar_vista("memoria")

    def _monitorear_modelo(self):
        """Actualiza la barra de estado mientras el modelo carga en background."""
        if _model_ready.is_set():
            if EMBEDDING_MODEL is not None:
                self.status("Modelo listo.", "ok")
            else:
                self.status("Error al cargar modelo de embeddings.", "error")
        else:
            self.status("⏳ Cargando modelo de embeddings...", "warning")
            self.after(2000, self._monitorear_modelo)

    def _centrar(self):
        self.update_idletasks()
        w, h = 820, 720
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["panel"], height=54, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🌊  MemoriaCoralApp",
            font=("Segoe UI Variable", 14, "bold"),
            text_color=COLORS["accent1"]
        ).pack(side="left", padx=18, pady=10)

        # Botón config GitHub
        ctk.CTkButton(
            header, text="⚙", width=36, height=32,
            fg_color=COLORS["surface"], hover_color=COLORS["accent4"],
            text_color=COLORS["text"], corner_radius=8,
            font=("Segoe UI Variable", 13),
            command=lambda: self.mostrar_vista("config")
        ).pack(side="right", padx=12, pady=10)

        # ── Barra de navegación ──────────────────────────────
        nav = ctk.CTkFrame(self, fg_color=COLORS["panel"], height=46, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        self._nav_btns = {}
        nav_items = [
            ("memoria",    "🧠 MEMORIA"),
            ("copiar",     "📋 COPIAR"),
            ("nueva",      "💾 NUEVA ENTRADA"),
            ("ias",        "⚙️ IAs"),
            ("excepcional","⭐ EXCEPCIONAL"),
            ("buscar",     "🔍 BUSCAR"),
            ("recalcular", "🔁 RECALCULAR"),
        ]
        for vista, label in nav_items:
            btn = ctk.CTkButton(
                nav, text=label,
                fg_color=COLORS["surface"],
                hover_color=COLORS["accent2"],
                text_color=COLORS["text"],
                corner_radius=10,
                font=("Segoe UI Variable", 9, "bold"),
                width=130, height=32,
                command=lambda v=vista: self.mostrar_vista(v)
            )
            btn.pack(side="left", padx=4, pady=7)
            self._nav_btns[vista] = btn

        # ── Área de contenido ────────────────────────────────
        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self._content.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Barra de estado ──────────────────────────────────
        self._status_var = StringVar(value="Listo.")
        self._status_color = COLORS["muted"]
        self._status_bar = ctk.CTkLabel(
            self, textvariable=self._status_var,
            fg_color=COLORS["panel"], text_color=COLORS["muted"],
            font=("Segoe UI Variable", 8), height=24, anchor="w"
        )
        self._status_bar.pack(fill="x", side="bottom")

    def status(self, msg, tipo="info"):
        color_map = {"ok": COLORS["ok"], "error": COLORS["error"],
                     "warning": COLORS["warning"], "info": COLORS["accent2"]}
        self._status_var.set(f"  {msg}")
        self._status_bar.configure(text_color=color_map.get(tipo, COLORS["muted"]))
        self.after(5000, lambda: self._status_var.set("  Listo."))

    def _limpiar_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    def _set_nav_active(self, vista):
        for k, btn in self._nav_btns.items():
            if k == vista:
                btn.configure(fg_color=COLORS["accent1"], text_color=COLORS["bg"])
            else:
                btn.configure(fg_color=COLORS["surface"], text_color=COLORS["text"])

    def mostrar_vista(self, nombre, datos=None):
        self._limpiar_content()
        self._set_nav_active(nombre)
        vistas = {
            "memoria":     self._vista_memoria,
            "copiar":      self._vista_copiar,
            "nueva":       self._vista_nueva_entrada,
            "ias":         self._vista_gestionar_ias,
            "excepcional": self._vista_excepcional_paso1,
            "config":      self._vista_config_github,
            "recalcular":  self._vista_recalcular_embeddings,
            "buscar":      self._vista_buscar_similitud,
        }
        fn = vistas.get(nombre)
        if fn:
            fn(datos) if datos is not None else fn()

    # ════════════════════════════════════════════════════════
    # VISTA 1 — MEMORIA
    # ════════════════════════════════════════════════════════
    def _vista_memoria(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        top = ctk.CTkFrame(frame, fg_color=COLORS["bg"])
        top.pack(fill="x", pady=(0,8))
        self._mem_header_lbl = ctk.CTkLabel(top, text="Cargando...",
            font=("Segoe UI Variable", 11, "bold"), text_color=COLORS["accent1"])
        self._mem_header_lbl.pack(side="left")
        make_btn(top, "🔄 Refrescar", self._refrescar_memoria,
                 color=COLORS["surface"], text_color=COLORS["accent1"], width=110).pack(side="right")

        sf, self._mem_text = scrollable_text(frame, state="disabled")
        sf.pack(fill="both", expand=True)

        self._refrescar_memoria()

    def _refrescar_memoria(self):
        self.status("Cargando memoria...", "info")
        def _fetch():
            data, err = api_leer_memoria()
            self.after(0, lambda: self._actualizar_mem_text(data, err))
        threading.Thread(target=_fetch, daemon=True).start()

    def _actualizar_mem_text(self, data, err):
        self._mem_text.configure(state="normal")
        self._mem_text.delete("1.0", "end")

        if err:
            self.status(f"Error: {err}", "error")
            self._mem_text.insert("end", f"[ERROR] {err}\n", "error")
            self._mem_text.tag_config("error", foreground=COLORS["error"])
        elif data:
            entradas = data if isinstance(data, list) else data.get("entries", [])
            activas = [e for e in entradas if not e.get("is_superseded", False)]
            self._mem_header_lbl.configure(text=f"🧠 MEMORIA  ·  {len(activas)} entradas activas")
            self.status(f"{len(activas)} entradas cargadas.", "ok")
            for e in activas:
                autor  = e.get("ia_author","?")
                fkey   = e.get("field_key","")
                fval   = e.get("field_value","")
                etype  = e.get("entry_type","")
                color  = AUTHOR_COLORS.get(autor, COLORS["accent2"])
                tag    = f"autor_{autor}"
                self._mem_text.tag_config(tag, foreground=color, font=("Consolas", 9, "bold"))
                self._mem_text.tag_config("key", foreground=COLORS["text"], font=("Consolas", 9, "bold"))
                self._mem_text.tag_config("val", foreground=COLORS["muted"], font=("Consolas", 9))
                self._mem_text.insert("end", f"[{autor.upper()}]  ", tag)
                self._mem_text.insert("end", f"{fkey}", "key")
                if etype:
                    self._mem_text.insert("end", f"  [{etype}]", "val")
                self._mem_text.insert("end", "\n")
                self._mem_text.insert("end", f"   {fval}\n\n", "val")
        else:
            self._mem_header_lbl.configure(text="🧠 MEMORIA  ·  Sin datos")
            self.status("Sin datos.", "warning")

        self._mem_text.configure(state="disabled")

    # ════════════════════════════════════════════════════════
    # VISTA 2 — COPIAR
    # ════════════════════════════════════════════════════════
    def _vista_copiar(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="📋  Copiar Memoria al Portapapeles",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent1"]).pack(anchor="w", pady=(0,12))

        info = ctk.CTkLabel(frame,
            text="Genera el contexto completo listo para pegar en cualquier IA.",
            font=("Segoe UI Variable", 9), text_color=COLORS["muted"])
        info.pack(anchor="w", pady=(0,8))

        make_btn(frame, "📋 Copiar al portapapeles", self._copiar_memoria,
                 color=COLORS["accent1"], width=220).pack(anchor="w")

        self._copy_result = ctk.CTkLabel(frame, text="", font=("Segoe UI Variable", 9),
                                          text_color=COLORS["ok"])
        self._copy_result.pack(anchor="w", pady=(8,0))

    def _copiar_memoria(self):
        self.status("Copiando...", "info")
        def _fetch():
            data, err = api_leer_memoria()
            self.after(0, lambda: self._do_copy(data, err))
        threading.Thread(target=_fetch, daemon=True).start()

    def _do_copy(self, data, err):
        if err:
            self.status(f"Error: {err}", "error")
            return
        entradas = data if isinstance(data, list) else data.get("entries", [])
        activas  = [e for e in entradas if not e.get("is_superseded", False)]
        lines    = ["=== MEMORIA DEL PROYECTO ==="]
        for e in activas:
            lines.append(f"[{e.get('ia_author','?').upper()}] {e.get('field_key','')}: {e.get('field_value','')}")
        lines.append("=== FIN DE MEMORIA ===")
        lines.append("Usa esta memoria como contexto. Si aprendes algo nuevo dime field_key, field_value, entry_type y confidence_score.")
        lines.append("No puedes hacer llamadas HTTP directamente. Yo guardaré lo que me indiques.")
        texto = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(texto)
        msg = f"✅ {len(activas)} entradas copiadas al portapapeles."
        self._copy_result.configure(text=msg)
        self.status(msg, "ok")

    # ════════════════════════════════════════════════════════
    # VISTA 3 — NUEVA ENTRADA
    # ════════════════════════════════════════════════════════
    def _vista_nueva_entrada(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="💾  Nueva Entrada de Memoria",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent1"]).pack(anchor="w", pady=(0,12))

        form = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=10)
        form.pack(fill="x", pady=(0,12))

        def lbl(parent, t):
            ctk.CTkLabel(parent, text=t, font=("Segoe UI Variable", 9, "bold"),
                         text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10,2))

        # ia_author
        lbl(form, "Autor IA")
        ia_list = self._ia_list
        self._ne_ia = StringVar(value=ia_list[0] if ia_list else "user")
        ctk.CTkComboBox(form, variable=self._ne_ia, values=ia_list,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"], width=200).pack(anchor="w", padx=14)

        # entry_type
        lbl(form, "Tipo de entrada")
        self._ne_type = StringVar(value=ENTRY_TYPES[0])
        ctk.CTkComboBox(form, variable=self._ne_type, values=ENTRY_TYPES,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"], width=200).pack(anchor="w", padx=14)

        # field_key
        lbl(form, "field_key (máx. 100 chars)")
        self._ne_key = ctk.CTkEntry(form, placeholder_text="clave_de_memoria",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=400)
        self._ne_key.pack(anchor="w", padx=14)

        # field_value
        lbl(form, "field_value (máx. 2000 chars)")
        self._ne_val_count = ctk.CTkLabel(form, text="0/2000",
            font=("Segoe UI Variable", 8), text_color=COLORS["muted"])
        self._ne_val_count.pack(anchor="e", padx=14)
        self._ne_val = tk.Text(form, bg=COLORS["input"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat", font=("Segoe UI Variable", 9),
            height=5, wrap="word")
        self._ne_val.pack(fill="x", padx=14, pady=(0,4))
        self._ne_val.bind("<KeyRelease>", self._update_val_count)

        # confidence_score
        lbl(form, "confidence_score (0.0 – 1.0)")
        self._ne_conf = ctk.CTkEntry(form, placeholder_text="0.8",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=120)
        self._ne_conf.pack(anchor="w", padx=14, pady=(0,14))

        # Botón
        self._ne_progress = ctk.CTkLabel(frame, text="", font=("Segoe UI Variable", 9),
                                          text_color=COLORS["warning"])
        self._ne_progress.pack(anchor="w", pady=(4,0))
        make_btn(frame, "💾 GUARDAR", self._guardar_entrada,
                 color=COLORS["accent1"], width=160).pack(anchor="w", pady=6)

    def _update_val_count(self, _=None):
        n = len(self._ne_val.get("1.0","end-1c"))
        self._ne_val_count.configure(text=f"{n}/2000")

    def _guardar_entrada(self):
        ia     = self._ne_ia.get().strip()
        etype  = self._ne_type.get().strip()
        key    = self._ne_key.get().strip()
        val    = self._ne_val.get("1.0","end-1c").strip()
        conf_s = self._ne_conf.get().strip()

        if not key:
            self.status("field_key es obligatorio.", "error"); return
        if len(key) > 100:
            self.status("field_key supera 100 chars.", "error"); return
        if not val:
            self.status("field_value es obligatorio.", "error"); return
        if len(val) > 2000:
            self.status("field_value supera 2000 chars.", "error"); return
        try:
            conf = float(conf_s)
            if not (0.0 <= conf <= 1.0):
                raise ValueError
        except ValueError:
            self.status("confidence_score debe ser un float entre 0.0 y 1.0.", "error")
            return

        self._ne_progress.configure(text="⏳ Generando embedding...")
        self.status("Generando embedding...", "info")

        payload_base = {"ia_author": ia, "entry_type": etype,
                        "field_key": key, "field_value": val, "confidence_score": conf}

        def _worker():
            emb = generar_embedding(key, etype, val, ia_author=ia)
            payload = {**payload_base, "embedding": emb}
            ok, err = api_escribir_entrada(payload)
            self.after(0, lambda: self._post_guardar(ok, err))

        threading.Thread(target=_worker, daemon=True).start()

    def _post_guardar(self, ok, err):
        self._ne_progress.configure(text="")
        if ok:
            self.status("Entrada guardada correctamente.", "ok")
            self.mostrar_vista("memoria")
        else:
            self.status(f"Error al guardar: {err}", "error")

    # ════════════════════════════════════════════════════════
    # VISTA 4 — GESTIONAR IAs
    # ════════════════════════════════════════════════════════
    def _vista_gestionar_ias(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="⚙️  Gestionar IAs",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent1"]).pack(anchor="w", pady=(0,10))

        top = ctk.CTkFrame(frame, fg_color=COLORS["bg"])
        top.pack(fill="x", pady=(0,8))
        make_btn(top, "🔄 Refrescar", self._refrescar_ias,
                 color=COLORS["surface"], text_color=COLORS["accent1"], width=110).pack(side="left")

        panel = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=10)
        panel.pack(fill="both", expand=True)

        sf, self._ia_text = scrollable_text(panel, state="disabled", height=10)
        sf.pack(fill="both", expand=True, padx=10, pady=10)

        add_frame = ctk.CTkFrame(panel, fg_color=COLORS["panel"])
        add_frame.pack(fill="x", padx=10, pady=(0,10))
        ctk.CTkLabel(add_frame, text="Nueva IA:", font=("Segoe UI Variable", 9, "bold"),
                     text_color=COLORS["text"]).pack(side="left", padx=(0,6))
        self._ia_nuevo = ctk.CTkEntry(add_frame, placeholder_text="nombre_ia",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=180)
        self._ia_nuevo.pack(side="left", padx=(0,8))
        make_btn(add_frame, "➕ AÑADIR", self._anadir_ia,
                 color=COLORS["accent2"], width=100).pack(side="left")

        self._refrescar_ias()

    def _refrescar_ias(self):
        self.status("Cargando IAs...", "info")
        def _fetch():
            ias = api_get_ias()
            self._ia_list = ias
            self.after(0, lambda: self._mostrar_ias(ias))
        threading.Thread(target=_fetch, daemon=True).start()

    def _mostrar_ias(self, ias):
        self._ia_text.configure(state="normal")
        self._ia_text.delete("1.0","end")
        for ia in ias:
            color = AUTHOR_COLORS.get(ia, COLORS["accent2"])
            tag = f"ia_{ia}"
            self._ia_text.tag_config(tag, foreground=color, font=("Consolas", 9, "bold"))
            self._ia_text.insert("end", f"  ● {ia}\n", tag)
        self._ia_text.configure(state="disabled")
        self.status(f"{len(ias)} IAs cargadas.", "ok")

    def _anadir_ia(self):
        import re
        nombre = self._ia_nuevo.get().strip()
        if not re.match(r'^[a-z0-9_]+$', nombre):
            self.status("Solo letras minúsculas, números y guion bajo.", "error")
            return
        if nombre in self._ia_list:
            self.status(f"La IA '{nombre}' ya existe.", "warning")
            return
        ok, err = api_add_ia(nombre)
        if ok:
            self.status(f"IA '{nombre}' añadida.", "ok")
            self._ia_nuevo.delete(0,"end")
            self._refrescar_ias()
        else:
            self.status(f"Error: {err}", "error")

    # ════════════════════════════════════════════════════════
    # VISTA 5 — CONVERSACIONES EXCEPCIONALES
    # ════════════════════════════════════════════════════════
    def _vista_excepcional_paso1(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="⭐  Conversación Excepcional — Paso 1: Registro",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent3"]).pack(anchor="w", pady=(0,10))

        form = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=10)
        form.pack(fill="both", expand=True)

        def lbl(t):
            ctk.CTkLabel(form, text=t, font=("Segoe UI Variable", 9, "bold"),
                         text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10,2))

        lbl("Título (máx. 100 chars)")
        self._exc_titulo = ctk.CTkEntry(form, placeholder_text="Título de la conversación",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=500)
        self._exc_titulo.pack(anchor="w", padx=14)

        lbl("IA participante")
        ia_list = self._ia_list
        self._exc_ia = StringVar(value=ia_list[1] if len(ia_list) > 1 else ia_list[0])
        ctk.CTkComboBox(form, variable=self._exc_ia, values=ia_list,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"], width=200).pack(anchor="w", padx=14)

        lbl("Texto completo de la conversación")
        self._exc_texto = tk.Text(form, bg=COLORS["input"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat", font=("Segoe UI Variable", 9),
            height=10, wrap="word")
        self._exc_texto.pack(fill="x", padx=14, pady=(0,4))

        self._exc_estrategica = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(form, text="¿Contiene decisiones estratégicas?",
            variable=self._exc_estrategica,
            fg_color=COLORS["accent3"], hover_color=COLORS["accent4"],
            text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(4,14))

        make_btn(form, "SIGUIENTE →", self._exc_siguiente_p1,
                 color=COLORS["accent3"], text_color="white", width=160).pack(anchor="e", padx=14, pady=(0,14))

    def _exc_siguiente_p1(self):
        titulo     = self._exc_titulo.get().strip()
        ia         = self._exc_ia.get().strip()
        texto      = self._exc_texto.get("1.0","end-1c").strip()
        estrategica= self._exc_estrategica.get()

        if not titulo:
            self.status("El título es obligatorio.", "error"); return
        if len(titulo) > 100:
            self.status("Título supera 100 chars.", "error"); return
        if not texto:
            self.status("El texto de la conversación es obligatorio.", "error"); return

        datos = {"titulo": titulo, "ia": ia, "texto": texto, "estrategica": estrategica}
        self._limpiar_content()
        self._vista_excepcional_paso2(datos)

    def _vista_excepcional_paso2(self, datos):
        titulo     = datos["titulo"]
        ia         = datos["ia"]
        texto      = datos["texto"]
        estrategica= datos["estrategica"]

        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="⭐  Conversación Excepcional — Paso 2: Validación mutua",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent3"]).pack(anchor="w", pady=(0,10))

        panel = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=10)
        panel.pack(fill="x", pady=(0,10))

        # Score sistema
        score_s = calcular_score_sistema(texto, titulo, estrategica)

        # Criterios
        crit_frame = ctk.CTkFrame(panel, fg_color=COLORS["panel"])
        crit_frame.pack(fill="x", padx=14, pady=(12,4))

        ctk.CTkLabel(crit_frame, text="Criterios del sistema:",
            font=("Segoe UI Variable", 9, "bold"), text_color=COLORS["text"]).pack(anchor="w")

        def crit_row(ok, label):
            sym   = "✓" if ok else "✗"
            color = COLORS["ok"] if ok else COLORS["error"]
            ctk.CTkLabel(crit_frame, text=f"  {sym}  {label}",
                font=("Consolas", 9), text_color=color).pack(anchor="w")

        crit_row(len(texto) > 500, f"Longitud suficiente (>500 chars) — actual: {len(texto)}")
        kws = [k for k in KEYWORDS_ESTRATEGICAS if k in texto.lower()]
        crit_row(bool(kws), f"Palabras clave estratégicas: {', '.join(kws) if kws else 'ninguna'}")
        crit_row(estrategica, "Marcada como decisión estratégica")

        ctk.CTkLabel(panel, text=f"Score del sistema:  {score_s:.2f}",
            font=("Consolas", 10), text_color=COLORS["accent2"]).pack(anchor="w", padx=14, pady=(8,2))

        # Slider usuario
        ctk.CTkLabel(panel, text="Score del usuario:",
            font=("Segoe UI Variable", 9, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(8,2))

        self._exc_score_u = ctk.DoubleVar(value=0.7)
        slider = ctk.CTkSlider(panel, from_=0.0, to=1.0, variable=self._exc_score_u,
            progress_color=COLORS["accent3"], button_color=COLORS["accent3"],
            fg_color=COLORS["surface"])
        slider.pack(fill="x", padx=14, pady=(0,4))

        score_lbl = ctk.CTkLabel(panel, text=f"Score usuario: 0.70  |  Score final: {(0.70+score_s)/2:.2f}",
            font=("Consolas", 9), text_color=COLORS["text"])
        score_lbl.pack(anchor="w", padx=14, pady=(0,12))

        def update_labels(_=None):
            su = self._exc_score_u.get()
            sf = (su + score_s) / 2
            color = COLORS["ok"] if sf >= 0.7 else COLORS["warning"]
            score_lbl.configure(
                text=f"Score usuario: {su:.2f}  |  Score final: {sf:.2f}",
                text_color=color
            )

        slider.configure(command=update_labels)

        # Advertencia
        self._exc_warn = ctk.CTkLabel(panel, text="", font=("Segoe UI Variable", 9),
                                       text_color=COLORS["warning"])
        self._exc_warn.pack(anchor="w", padx=14, pady=(0,4))

        btn_row = ctk.CTkFrame(panel, fg_color=COLORS["panel"])
        btn_row.pack(fill="x", padx=14, pady=(0,14))

        make_btn(btn_row, "← Atrás", lambda: self.mostrar_vista("excepcional"),
                 color=COLORS["surface"], text_color=COLORS["text"], width=90).pack(side="left", padx=(0,8))
        make_btn(btn_row, "✅ CONFIRMAR", lambda: self._exc_confirmar(datos, score_s),
                 color=COLORS["accent3"], text_color="white", width=140).pack(side="left")
        make_btn(btn_row, "⚠ Forzar", lambda: self._exc_forzar(datos, score_s),
                 color=COLORS["warning"], text_color=COLORS["bg"], width=100).pack(side="left", padx=8)

    def _exc_confirmar(self, datos, score_s):
        su = self._exc_score_u.get()
        sf = (su + score_s) / 2
        if sf < 0.7:
            self._exc_warn.configure(
                text=f"⚠ Score final {sf:.2f} < 0.7 — usa 'Forzar' para continuar de todas formas.")
            return
        self._exc_paso3(datos, su, score_s, sf)

    def _exc_forzar(self, datos, score_s):
        su = self._exc_score_u.get()
        sf = (su + score_s) / 2
        self._exc_paso3(datos, su, score_s, sf)

    def _exc_paso3(self, datos, score_u, score_s, score_f):
        self._limpiar_content()
        self._vista_excepcional_paso3(datos, score_u, score_s, score_f)

    def _vista_excepcional_paso3(self, datos, score_u, score_s, score_f):
        titulo     = datos["titulo"]
        ia         = datos["ia"]
        texto      = datos["texto"]
        estrategica= datos["estrategica"]

        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="⭐  Paso 3: Generando Tokens Causales y subiendo a GitHub...",
            font=("Segoe UI Variable", 11, "bold"),
            text_color=COLORS["accent3"]).pack(anchor="w", pady=(0,10))

        self._exc_log = tk.Text(frame, bg=COLORS["surface"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat", font=("Consolas", 9),
            height=16, wrap="word", state="disabled")
        self._exc_log.pack(fill="both", expand=True)

        def log(msg, color=None):
            self._exc_log.configure(state="normal")
            tag = f"tag_{id(msg)}"
            self._exc_log.tag_config(tag, foreground=color or COLORS["text"])
            self._exc_log.insert("end", msg + "\n", tag)
            self._exc_log.see("end")
            self._exc_log.configure(state="disabled")
            self._exc_log.update()

        def _worker():
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.after(0, lambda: log(f"[{datetime.now().strftime('%H:%M:%S')}] Generando embeddings...", COLORS["accent2"]))

            val_u = (f"TCA generado por conversación excepcional '{titulo}'. "
                     f"Tipo: conocimiento/investigación. Caducidad: 3 años. "
                     f"Score: {score_f:.2f}. IA participante: {ia}.")
            val_ia = (f"TCA generado por conversación excepcional '{titulo}'. "
                      f"Tipo: conocimiento/investigación. Caducidad: 3 años. "
                      f"Score: {score_f:.2f}. Validado por: user.")

            emb_u  = generar_embedding(f"tca_usuario_{ts}", "fact", val_u, ia_author="user")
            emb_ia = generar_embedding(f"tca_ia_{ts}", "fact", val_ia, ia_author=ia)

            self.after(0, lambda: log("  ✓ Embeddings generados", COLORS["ok"]))

            # TCA usuario
            self.after(0, lambda: log("[.] Guardando TCA usuario...", COLORS["accent1"]))
            ok, err = api_escribir_entrada({
                "ia_author": "user", "entry_type": "fact",
                "field_key": f"tca_usuario_{ts}", "field_value": val_u,
                "confidence_score": score_f, "embedding": emb_u
            })
            if ok:
                self.after(0, lambda: log(f"  ✓ tca_usuario_{ts} guardado", COLORS["ok"]))
            else:
                self.after(0, lambda: log(f"  ✗ Error TCA usuario: {err}", COLORS["error"]))

            # TCA ia
            self.after(0, lambda: log(f"[.] Guardando TCA {ia}...", COLORS["accent1"]))
            ok2, err2 = api_escribir_entrada({
                "ia_author": ia, "entry_type": "fact",
                "field_key": f"tca_ia_{ts}", "field_value": val_ia,
                "confidence_score": score_f, "embedding": emb_ia
            })
            if ok2:
                self.after(0, lambda: log(f"  ✓ tca_ia_{ts} guardado", COLORS["ok"]))
            else:
                self.after(0, lambda: log(f"  ✗ Error TCA IA: {err2}", COLORS["error"]))

            # GitHub
            config = cargar_config()
            if config:
                self.after(0, lambda: log("[.] Subiendo a GitHub...", COLORS["accent2"]))
                fecha_str = datetime.now().strftime("%Y-%m-%d")
                ruta = f"conversaciones/{fecha_str}_{slug(titulo)}.md"
                contenido = generar_markdown_tca(
                    titulo, ia, score_u, score_s, score_f, texto, ts, estrategica)
                ok3, err3 = github_subir_archivo(
                    config["token"], config["repo"], config["rama"],
                    ruta, contenido,
                    f"TCA: {titulo} [{ts}]"
                )
                if ok3:
                    self.after(0, lambda: log(f"  ✓ Subido a GitHub: {ruta}", COLORS["ok"]))
                else:
                    self.after(0, lambda: log(f"  ✗ Error GitHub: {err3}", COLORS["error"]))
            else:
                self.after(0, lambda: log("  ⚠ GitHub no configurado — omitiendo subida.", COLORS["warning"]))

            self.after(0, lambda: log("\n✅ Proceso completado.", COLORS["ok"]))
            self.after(0, lambda: self.status("Conversación excepcional procesada.", "ok"))

        threading.Thread(target=_worker, daemon=True).start()

    # ════════════════════════════════════════════════════════
    # VISTA CONFIGURACIÓN GITHUB
    # ════════════════════════════════════════════════════════
    def _vista_config_github(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="⚙  Configuración GitHub",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent4"]).pack(anchor="w", pady=(0,10))

        panel = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=10)
        panel.pack(fill="x")

        def lbl(t):
            ctk.CTkLabel(panel, text=t, font=("Segoe UI Variable", 9, "bold"),
                         text_color=COLORS["text"]).pack(anchor="w", padx=14, pady=(10,2))

        lbl("GitHub Personal Access Token (scope: repo)")
        self._cfg_token = ctk.CTkEntry(panel, placeholder_text="ghp_...",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=500, show="*")
        self._cfg_token.pack(anchor="w", padx=14)

        lbl("Repositorio (usuario/nombre-repo)")
        self._cfg_repo = ctk.CTkEntry(panel, placeholder_text="usuario/mi-repo",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=300)
        self._cfg_repo.pack(anchor="w", padx=14)

        lbl("Rama")
        self._cfg_rama = ctk.CTkEntry(panel, placeholder_text="main",
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            text_color=COLORS["text"], width=150)
        self._cfg_rama.pack(anchor="w", padx=14)

        # Cargar config existente
        config = cargar_config()
        if config:
            self._cfg_token.insert(0, config.get("token", ""))
            self._cfg_repo.insert(0, config.get("repo", ""))
            self._cfg_rama.insert(0, config.get("rama", "main"))
        else:
            self._cfg_rama.insert(0, "main")

        btn_row = ctk.CTkFrame(panel, fg_color=COLORS["panel"])
        btn_row.pack(fill="x", padx=14, pady=(12,14))

        make_btn(btn_row, "💾 GUARDAR", self._guardar_config_github,
                 color=COLORS["accent4"], text_color="white", width=120).pack(side="left", padx=(0,8))
        make_btn(btn_row, "🔗 Probar conexión", self._probar_github,
                 color=COLORS["surface"], text_color=COLORS["accent1"], width=160).pack(side="left")

        self._cfg_result = ctk.CTkLabel(panel, text="", font=("Segoe UI Variable", 9),
                                         text_color=COLORS["ok"])
        self._cfg_result.pack(anchor="w", padx=14, pady=(0,8))

    def _guardar_config_github(self):
        token = self._cfg_token.get().strip()
        repo  = self._cfg_repo.get().strip()
        rama  = self._cfg_rama.get().strip() or "main"
        if not token or not repo:
            self.status("Token y repositorio son obligatorios.", "error"); return
        guardar_config(token, repo, rama)
        self.status("Configuración GitHub guardada.", "ok")
        self._cfg_result.configure(text="✅ Configuración guardada.", text_color=COLORS["ok"])

    def _probar_github(self):
        token = self._cfg_token.get().strip()
        repo  = self._cfg_repo.get().strip()
        if not token or not repo:
            self.status("Introduce token y repositorio primero.", "error"); return
        self.status("Probando conexión...", "info")
        def _test():
            ok, msg = github_probar_conexion(token, repo)
            self.after(0, lambda: self._cfg_result.configure(
                text=f"✅ Conectado: {msg}" if ok else f"✗ Error: {msg}",
                text_color=COLORS["ok"] if ok else COLORS["error"]
            ))
            self.after(0, lambda: self.status(
                f"GitHub: {msg}" if ok else f"Error GitHub: {msg}",
                "ok" if ok else "error"
            ))
        threading.Thread(target=_test, daemon=True).start()


    # ════════════════════════════════════════════════════════
    # VISTA 6 — RECALCULAR EMBEDDINGS v4.1
    # ════════════════════════════════════════════════════════
    def _vista_recalcular_embeddings(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="🔁  Recalcular Embeddings — Migración a v4.1",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["warning"]).pack(anchor="w", pady=(0,6))

        info = ctk.CTkLabel(frame,
            text=(
                "Recalcula todos los embeddings existentes usando la nueva concatenación v4.1:\n"
                "  [{ia_author}] {field_key} | {entry_type} | {field_value}\n\n"
                "Por cada entrada activa se crea una nueva entrada con el embedding corregido\n"
                "y la anterior queda marcada como superseded (protocolo append-only).\n"
                "⚠  Requiere que el modelo esté cargado. Puede tardar varios minutos."
            ),
            font=("Segoe UI Variable", 9), text_color=COLORS["muted"],
            justify="left")
        info.pack(anchor="w", pady=(0,10))

        # Barra de progreso
        self._recalc_progress_var = ctk.DoubleVar(value=0)
        self._recalc_progress_bar = ctk.CTkProgressBar(frame,
            variable=self._recalc_progress_var,
            progress_color=COLORS["warning"], fg_color=COLORS["surface"],
            height=12, corner_radius=6)
        self._recalc_progress_bar.pack(fill="x", pady=(0,4))

        self._recalc_count_lbl = ctk.CTkLabel(frame, text="",
            font=("Consolas", 9), text_color=COLORS["muted"])
        self._recalc_count_lbl.pack(anchor="w", pady=(0,6))

        # Log
        sf, self._recalc_log = scrollable_text(frame)
        sf.pack(fill="both", expand=True, pady=(0,8))

        btn_row = ctk.CTkFrame(frame, fg_color=COLORS["bg"])
        btn_row.pack(fill="x")

        self._recalc_btn = make_btn(btn_row, "🔁 INICIAR RECÁLCULO", self._iniciar_recalculo,
                 color=COLORS["warning"], text_color=COLORS["bg"], width=200)
        self._recalc_btn.pack(side="left")

        ctk.CTkLabel(btn_row,
            text="  Solo entradas activas (is_superseded=false)",
            font=("Segoe UI Variable", 8), text_color=COLORS["muted"]).pack(side="left", padx=8)

    def _log_recalc(self, msg, color=None):
        self._recalc_log.configure(state="normal")
        tag = f"t{id(msg)}"
        self._recalc_log.tag_config(tag, foreground=color or COLORS["text"])
        self._recalc_log.insert("end", msg + "\n", tag)
        self._recalc_log.see("end")
        self._recalc_log.configure(state="disabled")
        self._recalc_log.update()

    def _iniciar_recalculo(self):
        if not _model_ready.is_set() or EMBEDDING_MODEL is None:
            self.status("Modelo no cargado aún. Espera unos segundos.", "warning")
            return

        self._recalc_btn.configure(state="disabled", text="⏳ Procesando...")
        self.status("Recálculo en curso...", "warning")

        def _worker():
            self.after(0, lambda: self._log_recalc("Cargando entradas activas desde Supabase...", COLORS["accent2"]))
            data, err = api_leer_memoria()
            if err:
                self.after(0, lambda: self._log_recalc(f"✗ Error al leer memoria: {err}", COLORS["error"]))
                self.after(0, lambda: self._recalc_btn.configure(state="normal", text="🔁 INICIAR RECÁLCULO"))
                return

            entradas = data if isinstance(data, list) else data.get("entries", [])
            activas  = [e for e in entradas if not e.get("is_superseded", False)]
            total    = len(activas)

            self.after(0, lambda: self._log_recalc(
                f"  {total} entradas activas encontradas. Iniciando recálculo v4.1...\n",
                COLORS["text"]))

            ok_count  = 0
            err_count = 0

            for i, entrada in enumerate(activas):
                ia    = entrada.get("ia_author", "")
                key   = entrada.get("field_key", "")
                etype = entrada.get("entry_type", "")
                val   = entrada.get("field_value", "")

                # Generar nuevo embedding v4.1
                nuevo_emb = generar_embedding(key, etype, val, ia_author=ia)

                if nuevo_emb is None:
                    msg = f"  [{i+1}/{total}] ✗ SKIP (modelo no disponible): {key}"
                    self.after(0, lambda m=msg: self._log_recalc(m, COLORS["error"]))
                    err_count += 1
                else:
                    ok, err_w = api_supersede_y_reescribir(entrada, nuevo_emb)
                    if ok:
                        msg = f"  [{i+1}/{total}] ✓ {ia} | {key}"
                        self.after(0, lambda m=msg: self._log_recalc(m, COLORS["ok"]))
                        ok_count += 1
                    else:
                        msg = f"  [{i+1}/{total}] ✗ ERROR: {key} — {err_w}"
                        self.after(0, lambda m=msg: self._log_recalc(m, COLORS["error"]))
                        err_count += 1

                # Actualizar barra de progreso
                progreso = (i + 1) / total if total > 0 else 1
                count_txt = f"Procesadas: {i+1}/{total}  ·  ✓ {ok_count}  ·  ✗ {err_count}"
                self.after(0, lambda p=progreso: self._recalc_progress_var.set(p))
                self.after(0, lambda t=count_txt: self._recalc_count_lbl.configure(text=t))

                # Pequeña pausa para no saturar la API
                time.sleep(0.15)

            resumen = (
                f"\n{'─'*50}\n"
                f"✅ Recálculo completado.\n"
                f"   Entradas procesadas: {total}\n"
                f"   Exitosas: {ok_count}\n"
                f"   Errores:  {err_count}\n"
                f"   Concatenación aplicada: [ia_author] field_key | entry_type | field_value\n"
                f"{'─'*50}"
            )
            self.after(0, lambda: self._log_recalc(resumen, COLORS["accent1"]))
            self.after(0, lambda: self.status(
                f"Recálculo completado: {ok_count} OK, {err_count} errores.", "ok"))
            self.after(0, lambda: self._recalc_btn.configure(
                state="normal", text="🔁 INICIAR RECÁLCULO"))

        threading.Thread(target=_worker, daemon=True).start()


    # ════════════════════════════════════════════════════════
    # VISTA 7 — BÚSQUEDA POR SIMILITUD COSENO (v4.1)
    # ════════════════════════════════════════════════════════
    def _vista_buscar_similitud(self, _=None):
        frame = ctk.CTkFrame(self._content, fg_color=COLORS["bg"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(frame, text="🔍  Búsqueda por Similitud Semántica",
            font=("Segoe UI Variable", 12, "bold"),
            text_color=COLORS["accent2"]).pack(anchor="w", pady=(0,6))

        # ── Umbrales de referencia ───────────────────────────
        umb_frame = ctk.CTkFrame(frame, fg_color=COLORS["panel"], corner_radius=8)
        umb_frame.pack(fill="x", pady=(0,10))
        umb_inner = ctk.CTkFrame(umb_frame, fg_color=COLORS["panel"])
        umb_inner.pack(fill="x", padx=14, pady=8)
        for color, label in [
            (COLORS["ok"],      "■  ≥ 0.88   Equivalente"),
            (COLORS["accent2"], "■  0.20–0.87  Compatible"),
            (COLORS["error"],   "■  < 0.20   Conflicto crítico"),
        ]:
            ctk.CTkLabel(umb_inner, text=label,
                font=("Consolas", 9), text_color=color).pack(side="left", padx=14)

        # ── Formulario de búsqueda ───────────────────────────
        search_row = ctk.CTkFrame(frame, fg_color=COLORS["bg"])
        search_row.pack(fill="x", pady=(0,6))

        self._buscar_query = ctk.CTkEntry(
            search_row,
            placeholder_text="Escribe tu consulta semántica... (ej: soberanía humana en decisiones estratégicas)",
            fg_color=COLORS["input"], border_color=COLORS["accent2"],
            text_color=COLORS["text"], width=560, height=36,
            font=("Segoe UI Variable", 10)
        )
        self._buscar_query.pack(side="left", padx=(0,8))
        self._buscar_query.bind("<Return>", lambda e: self._ejecutar_busqueda())

        make_btn(search_row, "🔍 BUSCAR", self._ejecutar_busqueda,
                 color=COLORS["accent2"], text_color="white", width=100).pack(side="left")

        # ── Filtros ──────────────────────────────────────────
        filtros_row = ctk.CTkFrame(frame, fg_color=COLORS["bg"])
        filtros_row.pack(fill="x", pady=(0,8))

        ctk.CTkLabel(filtros_row, text="Filtrar por IA:",
            font=("Segoe UI Variable", 9), text_color=COLORS["muted"]).pack(side="left", padx=(0,6))

        self._buscar_filtro_ia = StringVar(value="todas")
        ia_opts = ["todas"] + self._ia_list
        ctk.CTkComboBox(filtros_row, variable=self._buscar_filtro_ia,
            values=ia_opts, width=140,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"]).pack(side="left", padx=(0,16))

        ctk.CTkLabel(filtros_row, text="Tipo:",
            font=("Segoe UI Variable", 9), text_color=COLORS["muted"]).pack(side="left", padx=(0,6))

        self._buscar_filtro_tipo = StringVar(value="todos")
        tipo_opts = ["todos"] + ENTRY_TYPES
        ctk.CTkComboBox(filtros_row, variable=self._buscar_filtro_tipo,
            values=tipo_opts, width=130,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"]).pack(side="left", padx=(0,16))

        ctk.CTkLabel(filtros_row, text="Máx. resultados:",
            font=("Segoe UI Variable", 9), text_color=COLORS["muted"]).pack(side="left", padx=(0,6))

        self._buscar_top_k = StringVar(value="10")
        ctk.CTkComboBox(filtros_row, variable=self._buscar_top_k,
            values=["5","10","20","50","todas"], width=80,
            fg_color=COLORS["input"], border_color=COLORS["surface"],
            button_color=COLORS["accent2"], dropdown_fg_color=COLORS["panel"],
            text_color=COLORS["text"]).pack(side="left")

        # ── Resultados ───────────────────────────────────────
        self._buscar_header = ctk.CTkLabel(frame, text="",
            font=("Segoe UI Variable", 9, "bold"), text_color=COLORS["muted"])
        self._buscar_header.pack(anchor="w", pady=(2,4))

        sf, self._buscar_result_text = scrollable_text(frame)
        sf.pack(fill="both", expand=True)

    def _ejecutar_busqueda(self):
        query = self._buscar_query.get().strip()
        if not query:
            self.status("Escribe una consulta antes de buscar.", "warning")
            return
        if not _model_ready.is_set() or EMBEDDING_MODEL is None:
            self.status("Modelo no cargado aún. Espera unos segundos.", "warning")
            return

        self.status("Buscando...", "info")
        self._buscar_header.configure(text="⏳ Generando embedding de la consulta...")

        filtro_ia   = self._buscar_filtro_ia.get()
        filtro_tipo = self._buscar_filtro_tipo.get()
        top_k_str   = self._buscar_top_k.get()

        def _worker():
            import numpy as np

            # Embedding de la consulta (sin ia_author: consulta neutral)
            vec_query = EMBEDDING_MODEL.encode(query)

            # Cargar todas las entradas
            data, err = api_leer_memoria()
            if err:
                self.after(0, lambda: self.status(f"Error: {err}", "error"))
                return

            entradas = data if isinstance(data, list) else data.get("entries", [])
            activas  = [e for e in entradas if not e.get("is_superseded", False)]

            # Aplicar filtros
            if filtro_ia != "todas":
                activas = [e for e in activas if e.get("ia_author") == filtro_ia]
            if filtro_tipo != "todos":
                activas = [e for e in activas if e.get("entry_type") == filtro_tipo]

            # Calcular similitud coseno para entradas con embedding
            resultados = []
            sin_embedding = 0

            for e in activas:
                emb_raw = e.get("embedding")
                if not emb_raw:
                    sin_embedding += 1
                    continue
                try:
                    # El embedding puede venir como lista o como string "[x,y,z]"
                    if isinstance(emb_raw, str):
                        vec = np.array(json.loads(emb_raw), dtype=np.float32)
                    else:
                        vec = np.array(emb_raw, dtype=np.float32)

                    # Similitud coseno
                    norm_q = np.linalg.norm(vec_query)
                    norm_v = np.linalg.norm(vec)
                    if norm_q == 0 or norm_v == 0:
                        continue
                    score = float(np.dot(vec_query, vec) / (norm_q * norm_v))
                    resultados.append((score, e))
                except Exception:
                    sin_embedding += 1
                    continue

            # Ordenar por similitud descendente
            resultados.sort(key=lambda x: x[0], reverse=True)

            # Aplicar top_k
            if top_k_str != "todas":
                try:
                    resultados = resultados[:int(top_k_str)]
                except ValueError:
                    pass

            self.after(0, lambda: self._mostrar_resultados_busqueda(
                resultados, query, sin_embedding, len(activas)))

        threading.Thread(target=_worker, daemon=True).start()

    def _clasificar_similitud(self, score):
        if score >= 0.88:
            return "EQUIVALENTE", COLORS["ok"]
        elif score >= 0.20:
            return "compatible",  COLORS["accent2"]
        else:
            return "conflicto",   COLORS["error"]

    def _mostrar_resultados_busqueda(self, resultados, query, sin_embedding, total_filtrado):
        txt = self._buscar_result_text
        txt.configure(state="normal")
        txt.delete("1.0", "end")

        n = len(resultados)
        header_txt = (f"Consulta: \"{query}\"  ·  {n} resultados  "
                      f"·  {sin_embedding} sin embedding  ·  {total_filtrado} entradas analizadas")
        self._buscar_header.configure(text=header_txt)
        self.status(f"{n} resultados encontrados.", "ok")

        if not resultados:
            txt.insert("end", "\nNo se encontraron entradas con embedding para esta consulta.\n",
                      "muted")
            txt.tag_config("muted", foreground=COLORS["muted"], font=("Consolas", 9))
            txt.configure(state="disabled")
            return

        # Tags fijos
        txt.tag_config("sep",   foreground=COLORS["surface"],   font=("Consolas", 8))
        txt.tag_config("score_ok",  foreground=COLORS["ok"],    font=("Consolas", 10, "bold"))
        txt.tag_config("score_compat", foreground=COLORS["accent2"], font=("Consolas", 10, "bold"))
        txt.tag_config("score_conflict", foreground=COLORS["error"],  font=("Consolas", 10, "bold"))
        txt.tag_config("label_ok",     foreground=COLORS["ok"],    font=("Consolas", 8))
        txt.tag_config("label_compat", foreground=COLORS["accent2"], font=("Consolas", 8))
        txt.tag_config("label_conflict", foreground=COLORS["error"], font=("Consolas", 8))
        txt.tag_config("meta",  foreground=COLORS["muted"],     font=("Consolas", 9))
        txt.tag_config("key",   foreground=COLORS["text"],      font=("Consolas", 9, "bold"))
        txt.tag_config("val",   foreground=COLORS["muted"],     font=("Consolas", 9))

        for i, (score, e) in enumerate(resultados):
            etiqueta, color = self._clasificar_similitud(score)
            autor  = e.get("ia_author", "?")
            key    = e.get("field_key", "")
            val    = e.get("field_value", "")
            etype  = e.get("entry_type", "")
            conf   = e.get("confidence_score", "?")

            # Color dinámico por autor
            autor_color = AUTHOR_COLORS.get(autor, COLORS["accent2"])
            autor_tag   = f"autor_{autor}_{i}"
            txt.tag_config(autor_tag, foreground=autor_color, font=("Consolas", 9, "bold"))

            score_tag = f"score_{'ok' if score >= 0.88 else 'compat' if score >= 0.20 else 'conflict'}"
            label_tag = f"label_{'ok' if score >= 0.88 else 'compat' if score >= 0.20 else 'conflict'}"

            # Línea de resultado
            txt.insert("end", f"  {score:.4f}  ", score_tag)
            txt.insert("end", f"[{etiqueta}]  ", label_tag)
            txt.insert("end", f"[{autor.upper()}]  ", autor_tag)
            txt.insert("end", f"{key}", "key")
            txt.insert("end", f"  [{etype}]  conf:{conf}\n", "meta")
            # Fragmento del valor (máx 120 chars)
            resumen_val = val[:120] + ("..." if len(val) > 120 else "")
            txt.insert("end", f"     {resumen_val}\n", "val")
            txt.insert("end", "  " + "─"*90 + "\n", "sep")

        txt.configure(state="disabled")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MemoriaCoralApp()
    app.mainloop()
