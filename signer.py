"""
╔══════════════════════════════════════════════════════════╗
║   🃏  C E R T  O F  C H A O S                           ║
║   Why so serious about certificates?                     ║
║   Random Cert · Batch Sign · Export · Verify             ║
╚══════════════════════════════════════════════════════════╝

Requirements:
    pip install cryptography

Signing tool (one of):
    Linux/macOS : sudo apt install osslsigncode  /  brew install osslsigncode
    Windows     : signtool  (Windows SDK / Visual Studio)
"""

import os, sys, json, shutil, random, string, subprocess
import threading, tempfile, platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12


# ══════════════════════════════════════════════════════════════════════════════
#  JOKER THEME  🃏
# ══════════════════════════════════════════════════════════════════════════════

C = dict(
    bg       = "#080810",   # near-black with purple tint
    panel    = "#0e0e1a",   # dark purple-black panel
    card     = "#12102a",   # deep violet card bg
    border   = "#3a1f6e",   # purple border
    accent   = "#39ff14",   # acid green  (Joker's chaos)
    accent2  = "#9d00ff",   # electric purple
    success  = "#39ff14",   # acid green success
    warning  = "#ffcc00",   # Joker gold
    error    = "#ff2052",   # hot red
    fg       = "#e8e0ff",   # lavender white
    fg_dim   = "#7060a0",   # muted purple
    entry_bg = "#0a0918",   # almost black
    btn_bg   = "#1c1040",   # dark purple btn
    btn_act  = "#2a1a5e",   # lighter purple on hover
)

FONT_BODY   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)


# ══════════════════════════════════════════════════════════════════════════════
#  RANDOM DATA
# ══════════════════════════════════════════════════════════════════════════════

PREFIXES  = ["Alpha","Beta","Nova","Apex","Prime","Core","Nexus","Vortex","Zenith",
             "Cipher","Vector","Titan","Orbit","Fusion","Sigma","Quartz","Helios",
             "Onyx","Cobalt","Pulsar","Stratus","Phantom","Eclipse","Axiom","Radix"]
SUFFIXES  = ["Systems","Technologies","Solutions","Software","Labs","Dynamics",
             "Networks","Innovations","Group","Corp","Enterprises","Digital",
             "Computing","Services","Works","Logic","Forge","Vault","Bridge"]
UNITS     = ["R&D","Engineering","Software Development","Platform Engineering",
             "Security","Infrastructure","DevOps","Core Systems","IT","Operations"]
COUNTRIES = {
    "US":["California","Texas","New York","Washington","Colorado","Nevada"],
    "GB":["England","Scotland","Wales","Northern Ireland"],
    "DE":["Bavaria","Berlin","Hamburg","Hesse","Saxony"],
    "FR":["Ile-de-France","Normandy","Brittany","Provence"],
    "CA":["Ontario","British Columbia","Quebec","Alberta"],
    "AU":["New South Wales","Victoria","Queensland","Western Australia"],
    "NL":["North Holland","South Holland","Utrecht"],
    "SE":["Stockholm County","Vastra Gotaland","Skane"],
    "CH":["Zurich","Geneva","Basel"],
    "JP":["Tokyo","Osaka","Kyoto","Kanagawa"],
    "SG":["Singapore"],
    "IE":["Dublin","Cork","Galway"],
    "FI":["Uusimaa","Pirkanmaa","Varsinais-Suomi"],
    "PL":["Masovian","Lesser Poland","Lower Silesian"],
}
CITIES    = ["Springfield","Riverside","Lakewood","Greenfield","Fairview",
             "Sunnyvale","Clearwater","Maplewood","Hillcrest","Brookside",
             "Stonebridge","Willowbrook","Harborview","Cedarville","Elmwood",
             "Ashford","Westgate","Northbrook","Southfield","Eastwood"]

TIMESTAMP_SERVERS = {
    "DigiCert (SHA-256)"  : "http://timestamp.digicert.com",
    "Sectigo RFC3161"     : "http://timestamp.sectigo.com",
    "GlobalSign"          : "http://timestamp.globalsign.com/scripts/timstamp.dll",
    "Comodo / Sectigo"    : "http://timestamp.comodoca.com",
    "Apple Timestamp"     : "http://timestamp.apple.com/ts01",
    "FreeTSA (RFC3161)"   : "https://freetsa.org/tsr",
    "None (no timestamp)" : "",
}

HASH_ALGOS = ["SHA256", "SHA384", "SHA512"]
KEY_SIZES  = [2048, 3072, 4096]

PRESETS_FILE = Path.home() / ".certofchaos_presets.json"

# Joker-flavoured log intro lines shown randomly on start
CHAOS_LINES = [
    "♠  Madness, as you know, is like gravity — all it takes is a little push.",
    "♣  Introduce a little anarchy. Upset the established order of certificate chains.",
    "♥  I'm not a monster. I'm just ahead of the CA curve.",
    "♦  You wanna know how I got these certs? I just made them up.",
    "🃏  Why so serious? It's just a self-signed certificate.",
    "♠  Some men just want to watch the trust store burn.",
    "♣  Chaos isn't a pit. Chaos is a ladder — and so is code signing.",
    "♥  The only sensible way to forge trust is to do it beautifully.",
]


# ══════════════════════════════════════════════════════════════════════════════
#  CERTIFICATE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def rand_str(n=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def random_cert_details():
    company = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
    country = random.choice(list(COUNTRIES))
    state   = random.choice(COUNTRIES[country])
    domain  = company.replace(" ","").lower() + ".com"
    return dict(
        common_name  = company,
        organization = company,
        org_unit     = random.choice(UNITS),
        country      = country,
        state        = state,
        locality     = random.choice(CITIES),
        email        = f"certs-{rand_str(4)}@{domain}",
        valid_days   = random.randint(365, 1095),
    )

def build_certificate(details: dict, key_size: int = 2048, hash_algo: str = "SHA256"):
    key  = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    algo = {"SHA256": hashes.SHA256(), "SHA384": hashes.SHA384(),
            "SHA512": hashes.SHA512()}[hash_algo]

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME,             details["country"][:2].upper()),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,   details["state"]),
        x509.NameAttribute(NameOID.LOCALITY_NAME,            details["locality"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,        details["organization"]),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, details["org_unit"]),
        x509.NameAttribute(NameOID.COMMON_NAME,              details["common_name"]),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS,            details["email"]),
    ])
    now  = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject).issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=int(details["valid_days"])))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True, key_cert_sign=True, crl_sign=True,
            content_commitment=True, key_encipherment=False,
            data_encipherment=False, key_agreement=False,
            encipher_only=False, decipher_only=False), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([x509.ExtendedKeyUsageOID.CODE_SIGNING]),
            critical=False)
        .sign(key, algo)
    )
    cert_pem  = cert.public_bytes(serialization.Encoding.PEM)
    key_pem   = key.private_bytes(serialization.Encoding.PEM,
                                   serialization.PrivateFormat.TraditionalOpenSSL,
                                   serialization.NoEncryption())
    cer_bytes = cert.public_bytes(serialization.Encoding.DER)
    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=details["common_name"].encode(), key=key, cert=cert,
        cas=None, encryption_algorithm=serialization.NoEncryption())
    return cert_pem, key_pem, cer_bytes, pfx_bytes


# ══════════════════════════════════════════════════════════════════════════════
#  SIGNING / VERIFYING
# ══════════════════════════════════════════════════════════════════════════════

def sign_exe(exe_in, pfx_path, exe_out, timestamp_url, hash_algo, log):
    if sys.platform == "win32":
        cmd = ["signtool","sign","/f",pfx_path,"/fd",hash_algo.lower(),"/v",exe_in]
        if timestamp_url:
            cmd += ["/tr", timestamp_url, "/td", hash_algo.lower()]
        if exe_in != exe_out:
            shutil.copy2(exe_in, exe_out)
            cmd[-1] = exe_out
    else:
        cmd = ["osslsigncode","sign","-pkcs12",pfx_path,
               "-h", hash_algo.lower(), "-in", exe_in, "-out", exe_out]
        if timestamp_url:
            cmd += ["-ts", timestamp_url]

    log(f"  CMD: {' '.join(cmd)}\n")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: log(r.stdout)
        if r.stderr: log(f"[stderr] {r.stderr}", "warn")
        return r.returncode == 0
    except FileNotFoundError:
        tool = "signtool" if sys.platform == "win32" else "osslsigncode"
        log(f"  ERROR: '{tool}' not found — install it and add to PATH.\n", "error")
        return False

def verify_exe(exe_path, log, ca_file=None):
    if sys.platform == "win32":
        cmd = ["signtool","verify","/pa","/v",exe_path]
    else:
        cmd = ["osslsigncode","verify","-in",exe_path]
        if ca_file:
            cmd += ["-CAfile", ca_file]
    log(f"  Verifying: {exe_path}\n")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.stdout: log(r.stdout)
        if r.stderr: log(f"[stderr] {r.stderr}", "warn")
        return r.returncode == 0
    except FileNotFoundError:
        log("  Verify tool not found.\n", "warn")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION  🃏
# ══════════════════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🃏 CertOfChaos")
        self.configure(bg=C["bg"])
        self.minsize(880, 740)
        self._presets = self._load_presets()
        self._build_styles()
        self._build_ui()
        self._randomize()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ──────────────────────────────────────────────────────────── STYLES ──
    def _build_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".",             background=C["bg"],   foreground=C["fg"],
                                     font=FONT_BODY,       borderwidth=0)
        s.configure("TFrame",        background=C["bg"])
        s.configure("TLabel",        background=C["bg"],   foreground=C["fg"])
        s.configure("Card.TLabel",   background=C["card"], foreground=C["fg"])
        s.configure("Dim.TLabel",    background=C["card"], foreground=C["fg_dim"])
        s.configure("TNotebook",     background=C["bg"],   tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab", background=C["panel"],foreground=C["fg_dim"],
                                     padding=[16,8], font=FONT_BOLD)
        s.map("TNotebook.Tab",
              background=[("selected", C["card"])],
              foreground=[("selected", C["accent"])])      # acid green active tab
        s.configure("TEntry",        fieldbackground=C["entry_bg"], foreground=C["fg"],
                                     insertcolor=C["accent"], relief="flat", borderwidth=1)
        s.configure("TCombobox",     fieldbackground=C["entry_bg"], foreground=C["fg"],
                                     selectbackground=C["border"], relief="flat")
        s.configure("TCheckbutton",  background=C["card"], foreground=C["fg"])
        s.configure("TScrollbar",    background=C["border"], troughcolor=C["panel"],
                                     relief="flat", arrowcolor=C["fg_dim"])

        # Button styles — Joker palette
        for name, bg, fg, abg in [
            ("Accent",  C["accent2"],  "white",       "#7a00cc"),   # electric purple
            ("Cyan",    C["accent"],   C["bg"],        "#28cc0f"),   # acid green
            ("Dim",     C["btn_bg"],   C["fg_dim"],    C["btn_act"]),
            ("Success", C["accent"],   C["bg"],        "#28cc0f"),
            ("Danger",  C["error"],    "white",        "#cc0033"),
        ]:
            s.configure(f"{name}.TButton", background=bg, foreground=fg,
                        font=FONT_BOLD, borderwidth=0, relief="flat", padding=[10,6])
            s.map(f"{name}.TButton",
                  background=[("active", abg), ("disabled", C["border"])],
                  foreground=[("disabled", C["fg_dim"])])

        s.configure("TProgressbar", troughcolor=C["border"], background=C["accent"],
                    thickness=5, relief="flat", borderwidth=0)
        s.configure("TSeparator",   background=C["border"])
        s.configure("Treeview",     background=C["entry_bg"], foreground=C["fg"],
                    fieldbackground=C["entry_bg"], rowheight=22, font=FONT_SMALL)
        s.configure("Treeview.Heading", background=C["border"],
                    foreground=C["accent"], font=FONT_SMALL)
        s.map("Treeview", background=[("selected", C["accent2"])])

    # ───────────────────────────────────────────────────────────── UI ──────
    def _build_ui(self):
        # ── Header  🃏
        hdr = tk.Frame(self, bg=C["panel"], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Left: suit decorations + title
        left = tk.Frame(hdr, bg=C["panel"])
        left.pack(side="left", padx=16, pady=8)
        tk.Label(left, text="♠ ♣", font=("Segoe UI", 11),
                 bg=C["panel"], fg=C["fg_dim"]).pack(side="left", padx=(0,8))
        tk.Label(left, text="🃏  CertOfChaos", font=("Segoe UI", 15, "bold"),
                 bg=C["panel"], fg=C["accent"]).pack(side="left")
        tk.Label(left, text="  ♥ ♦", font=("Segoe UI", 11),
                 bg=C["panel"], fg=C["error"]).pack(side="left", padx=(8,0))

        # Tagline
        tk.Label(hdr, text="Why so serious about certificates?",
                 font=("Segoe UI", 9, "italic"),
                 bg=C["panel"], fg=C["fg_dim"]).pack(side="left", pady=18)

        ttk.Button(hdr, text="About", style="Dim.TButton",
                   command=self._show_about).pack(side="right", padx=10, pady=12)

        # Thin accent border under header
        tk.Frame(self, bg=C["accent"], height=2).pack(fill="x")

        # ── Notebook
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=12, pady=(8,0))

        self._tab_single = ttk.Frame(self._nb)
        self._tab_batch  = ttk.Frame(self._nb)
        self._tab_cert   = ttk.Frame(self._nb)
        self._tab_config = ttk.Frame(self._nb)

        self._nb.add(self._tab_single, text="  ✍  Single Sign  ")
        self._nb.add(self._tab_batch,  text="  📦  Batch Sign  ")
        self._nb.add(self._tab_cert,   text="  🃏  Certificate  ")
        self._nb.add(self._tab_config, text="  ⚙  Settings  ")

        self._build_single_tab()
        self._build_batch_tab()
        self._build_cert_tab()
        self._build_config_tab()

        # ── Progress bar
        self._progress = tk.DoubleVar(value=0)
        ttk.Progressbar(self, variable=self._progress, maximum=100).pack(
            fill="x", padx=12, pady=(6,0))

        # ── Log area
        log_frame = tk.Frame(self, bg=C["panel"])
        log_frame.pack(fill="both", expand=True, padx=12, pady=8)

        log_hdr = tk.Frame(log_frame, bg=C["panel"])
        log_hdr.pack(fill="x")
        tk.Label(log_hdr, text="  ♠  Chaos Log", font=FONT_BOLD,
                 bg=C["panel"], fg=C["accent"]).pack(side="left", pady=4)
        for (lbl, cmd) in [("Copy All", self._copy_log), ("Clear", self._clear_log)]:
            tk.Button(log_hdr, text=lbl, font=FONT_SMALL, relief="flat",
                      bg=C["btn_bg"], fg=C["fg_dim"], cursor="hand2",
                      command=cmd, bd=0, padx=8).pack(side="right", pady=2, padx=4)

        self._log_w = scrolledtext.ScrolledText(
            log_frame, height=8, font=FONT_MONO, state="disabled",
            bg=C["bg"], fg=C["fg"], relief="flat", bd=0,
            insertbackground=C["accent"])
        self._log_w.pack(fill="both", expand=True, padx=2, pady=(0,4))

        for tag, color in [
            ("info",    C["fg"]),
            ("success", C["accent"]),    # acid green
            ("error",   C["error"]),
            ("warn",    C["warning"]),
            ("accent",  C["accent"]),
            ("dim",     C["fg_dim"]),
            ("header",  C["accent2"]),   # purple
            ("joker",   C["warning"]),   # gold for chaos quotes
        ]:
            self._log_w.tag_config(tag, foreground=color)

        # ── Status bar
        self._status = tk.StringVar(value="🃏  Ready to deal some chaos...")
        tk.Label(self, textvariable=self._status, font=FONT_SMALL,
                 bg=C["panel"], fg=C["fg_dim"], anchor="w", padx=10).pack(
            fill="x", side="bottom")

    # ──────────────────────────────── TAB 1 · SINGLE SIGN ────────────────
    def _build_single_tab(self):
        card = tk.Frame(self._tab_single, bg=C["card"])
        card.pack(fill="both", expand=True, padx=16, pady=14)

        for row_idx, (label, attr, browse_fn) in enumerate([
            ("Input EXE",  "_s_exe", "_browse_exe_single"),
            ("Output EXE", "_s_out", "_browse_out_single"),
        ]):
            setattr(self, attr, tk.StringVar())
            tk.Label(card, text=label, font=FONT_SMALL, bg=C["card"],
                     fg=C["fg_dim"]).grid(row=row_idx, column=0, sticky="w",
                                          padx=(14,6), pady=6)
            ttk.Entry(card, textvariable=getattr(self, attr), width=52).grid(
                row=row_idx, column=1, sticky="ew", padx=(0,6), pady=6)
            ttk.Button(card, text="Browse…", style="Dim.TButton",
                       command=getattr(self, browse_fn)).grid(
                row=row_idx, column=2, padx=(0,14))
        card.columnconfigure(1, weight=1)

        tk.Label(card, text="♦  Tip: type the path directly or use Browse.",
                 font=FONT_SMALL, bg=C["card"], fg=C["fg_dim"]).grid(
            row=2, column=0, columnspan=3, sticky="w", padx=14, pady=(0,6))

        tk.Frame(card, bg=C["border"], height=1).grid(
            row=3, column=0, columnspan=3, sticky="ew", padx=12, pady=4)

        opts = tk.Frame(card, bg=C["card"])
        opts.grid(row=4, column=0, columnspan=3, sticky="w", padx=14, pady=4)
        self._s_verify = tk.BooleanVar(value=True)
        self._s_export = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts, text="Verify after signing",
                        variable=self._s_verify).pack(side="left", padx=(0,20))
        ttk.Checkbutton(opts, text="Export certificate files",
                        variable=self._s_export).pack(side="left")

        btns = tk.Frame(card, bg=C["card"])
        btns.grid(row=5, column=0, columnspan=3, pady=(12,14), padx=14, sticky="w")
        ttk.Button(btns, text="  🃏  Deal the Cert  ", style="Accent.TButton",
                   command=self._run_single).pack(side="left", padx=(0,10), ipadx=6, ipady=2)
        ttk.Button(btns, text="🔀 New Cert", style="Dim.TButton",
                   command=self._randomize).pack(side="left", padx=(0,8))
        ttk.Button(btns, text="🔍 Verify Only", style="Dim.TButton",
                   command=self._run_verify_only).pack(side="left")

    # ──────────────────────────────── TAB 2 · BATCH SIGN ─────────────────
    def _build_batch_tab(self):
        card = tk.Frame(self._tab_batch, bg=C["card"])
        card.pack(fill="both", expand=True, padx=16, pady=14)

        tb = tk.Frame(card, bg=C["card"])
        tb.pack(fill="x", padx=10, pady=(10,4))
        ttk.Button(tb, text="+ Add EXEs",       style="Dim.TButton",
                   command=self._batch_add).pack(side="left", padx=(0,6))
        ttk.Button(tb, text="Remove Selected",  style="Dim.TButton",
                   command=self._batch_remove).pack(side="left", padx=(0,6))
        ttk.Button(tb, text="Clear All",        style="Dim.TButton",
                   command=self._batch_clear).pack(side="left", padx=(0,20))

        self._batch_out_dir = tk.StringVar()
        tk.Label(tb, text="Output dir:", font=FONT_SMALL,
                 bg=C["card"], fg=C["fg_dim"]).pack(side="left")
        ttk.Entry(tb, textvariable=self._batch_out_dir, width=26).pack(side="left", padx=4)
        ttk.Button(tb, text="…", style="Dim.TButton", width=3,
                   command=self._batch_browse_out).pack(side="left")

        self._batch_suffix = tk.StringVar(value="_signed")
        tk.Label(tb, text="  Suffix:", font=FONT_SMALL,
                 bg=C["card"], fg=C["fg_dim"]).pack(side="left")
        ttk.Entry(tb, textvariable=self._batch_suffix, width=10).pack(side="left", padx=4)

        tree_frame = tk.Frame(card, bg=C["card"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(4,0))

        self._batch_tree = ttk.Treeview(tree_frame, columns=("file","status"),
                                         show="headings", selectmode="extended", height=8)
        self._batch_tree.heading("file",   text="♠  EXE File")
        self._batch_tree.heading("status", text="♣  Status")
        self._batch_tree.column("file",   width=500)
        self._batch_tree.column("status", width=140, anchor="center")
        self._batch_tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._batch_tree.yview)
        vsb.pack(side="right", fill="y")
        self._batch_tree.configure(yscrollcommand=vsb.set)

        opts = tk.Frame(card, bg=C["card"])
        opts.pack(fill="x", padx=10, pady=6)
        self._b_new_cert = tk.BooleanVar(value=True)
        self._b_verify   = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="New random cert per file",
                        variable=self._b_new_cert).pack(side="left", padx=(0,20))
        ttk.Checkbutton(opts, text="Verify after each sign",
                        variable=self._b_verify).pack(side="left")

        btns = tk.Frame(card, bg=C["card"])
        btns.pack(fill="x", padx=10, pady=(0,12))
        ttk.Button(btns, text="  📦  Release the Chaos  ", style="Accent.TButton",
                   command=self._run_batch).pack(side="left", ipadx=6, ipady=2)
        self._batch_count = tk.StringVar(value="0 files")
        tk.Label(btns, textvariable=self._batch_count, font=FONT_SMALL,
                 bg=C["card"], fg=C["fg_dim"]).pack(side="left", padx=14)

    # ──────────────────────────────── TAB 3 · CERTIFICATE ────────────────
    def _build_cert_tab(self):
        card = tk.Frame(self._tab_cert, bg=C["card"])
        card.pack(fill="both", expand=True, padx=16, pady=14)

        # Preset bar
        pb = tk.Frame(card, bg=C["card"])
        pb.pack(fill="x", padx=12, pady=(10,6))
        tk.Label(pb, text="Preset:", font=FONT_SMALL,
                 bg=C["card"], fg=C["fg_dim"]).pack(side="left")
        self._preset_var = tk.StringVar()
        self._preset_cb  = ttk.Combobox(pb, textvariable=self._preset_var,
                                         width=26, values=list(self._presets.keys()))
        self._preset_cb.pack(side="left", padx=6)
        for (lbl, sty, fn) in [
            ("Load",   "Dim.TButton",    self._load_preset),
            ("Save",   "Cyan.TButton",   self._save_preset),
            ("Delete", "Dim.TButton",    self._del_preset),
        ]:
            ttk.Button(pb, text=lbl, style=sty, command=fn).pack(side="left", padx=2)
        ttk.Button(pb, text="🃏 Randomize", style="Accent.TButton",
                   command=self._randomize).pack(side="right")

        tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=12, pady=(4,8))

        # Fields
        ff = tk.Frame(card, bg=C["card"])
        ff.pack(fill="both", padx=12)

        FIELDS = [
            ("Common Name",    "cn",       0, 0, 32),
            ("Organization",   "org",      1, 0, 32),
            ("Org Unit",       "ou",       2, 0, 32),
            ("Email",          "email",    3, 0, 32),
            ("Country (2-ch)", "country",  0, 2, 8),
            ("State",          "state",    1, 2, 20),
            ("City",           "locality", 2, 2, 20),
            ("Valid Days",     "days",     3, 2, 8),
        ]
        self._cert_vars = {}
        for (lbl, key, row, col, w) in FIELDS:
            bc = col * 2
            tk.Label(ff, text=lbl, font=FONT_SMALL, bg=C["card"],
                     fg=C["fg_dim"]).grid(row=row, column=bc,
                                          sticky="w", padx=(0,6), pady=5)
            var = tk.StringVar()
            self._cert_vars[key] = var
            ttk.Entry(ff, textvariable=var, width=w).grid(
                row=row, column=bc+1, sticky="ew", padx=(0,18), pady=5)
        ff.columnconfigure(1, weight=2)
        ff.columnconfigure(3, weight=1)

        tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=12, pady=8)

        # Export row
        exp = tk.Frame(card, bg=C["card"])
        exp.pack(fill="x", padx=12, pady=(0,10))
        self._exp_dir = tk.StringVar()
        tk.Label(exp, text="Export dir:", font=FONT_SMALL,
                 bg=C["card"], fg=C["fg_dim"]).pack(side="left")
        ttk.Entry(exp, textvariable=self._exp_dir, width=34).pack(side="left", padx=6)
        ttk.Button(exp, text="…", style="Dim.TButton", width=3,
                   command=lambda: self._exp_dir.set(
                       filedialog.askdirectory(title="Export cert to…") or self._exp_dir.get())
                   ).pack(side="left")
        ttk.Button(exp, text="💾 Export Cert Files", style="Cyan.TButton",
                   command=self._export_cert).pack(side="left", padx=10)
        ttk.Button(exp, text="📋 Copy Info", style="Dim.TButton",
                   command=self._copy_cert_info).pack(side="left")

    # ──────────────────────────────── TAB 4 · SETTINGS ───────────────────
    def _build_config_tab(self):
        card = tk.Frame(self._tab_config, bg=C["card"])
        card.pack(fill="both", expand=True, padx=16, pady=14)

        def section(text):
            tk.Label(card, text=text, font=FONT_BOLD, bg=C["card"],
                     fg=C["accent"]).pack(anchor="w", padx=14, pady=(14,2))
            tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=14, pady=(0,6))

        def opt_row(label, widget_fn):
            r = tk.Frame(card, bg=C["card"])
            r.pack(fill="x", padx=14, pady=4)
            tk.Label(r, text=label, width=26, anchor="w", font=FONT_SMALL,
                     bg=C["card"], fg=C["fg_dim"]).pack(side="left")
            widget_fn(r)

        section("♠  Signing Options")
        self._cfg_ts    = tk.StringVar(value="DigiCert (SHA-256)")
        self._cfg_hash  = tk.StringVar(value="SHA256")
        self._cfg_ksize = tk.StringVar(value="2048")

        opt_row("Timestamp Server",
                lambda r: ttk.Combobox(r, textvariable=self._cfg_ts,
                    values=list(TIMESTAMP_SERVERS.keys()),
                    width=34, state="readonly").pack(side="left"))
        opt_row("Hash Algorithm",
                lambda r: ttk.Combobox(r, textvariable=self._cfg_hash,
                    values=HASH_ALGOS, width=12, state="readonly").pack(side="left"))
        opt_row("RSA Key Size",
                lambda r: ttk.Combobox(r, textvariable=self._cfg_ksize,
                    values=[str(k) for k in KEY_SIZES],
                    width=10, state="readonly").pack(side="left"))

        section("♣  Behavior")
        self._cfg_open_out = tk.BooleanVar(value=True)
        self._cfg_verbose  = tk.BooleanVar(value=False)
        opt_row("Open output folder after sign",
                lambda r: ttk.Checkbutton(r, variable=self._cfg_open_out).pack(side="left"))
        opt_row("Verbose log output",
                lambda r: ttk.Checkbutton(r, variable=self._cfg_verbose).pack(side="left"))

        section("♦  Environment")
        tool = "signtool" if sys.platform == "win32" else "osslsigncode"
        found = shutil.which(tool) is not None
        tk.Label(card,
                 text=f"{'✅' if found else '❌'}  {tool}  {'found in PATH' if found else 'NOT found — install it, clown'}",
                 font=FONT_SMALL, bg=C["card"],
                 fg=C["accent"] if found else C["error"]).pack(anchor="w", padx=14, pady=4)
        tk.Label(card,
                 text=f"🃏  Python {platform.python_version()}  ·  "
                      f"{platform.system()} {platform.release()}",
                 font=FONT_SMALL, bg=C["card"], fg=C["fg_dim"]).pack(anchor="w", padx=14)

    # ══════════════════════════════════════════════════════════════════════
    #  LOG HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _log(self, msg, tag="info"):
        def _do():
            self._log_w.configure(state="normal")
            self._log_w.insert("end", msg, tag)
            self._log_w.see("end")
            self._log_w.configure(state="disabled")
        self.after(0, _do)

    def _log_sep(self):
        self._log("─" * 64 + "\n", "dim")

    def _clear_log(self):
        self._log_w.configure(state="normal")
        self._log_w.delete("1.0","end")
        self._log_w.configure(state="disabled")

    def _copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self._log_w.get("1.0","end"))

    def _set_status(self, msg):
        self.after(0, lambda: self._status.set(msg))

    def _set_progress(self, val):
        self.after(0, lambda: self._progress.set(val))

    # ══════════════════════════════════════════════════════════════════════
    #  BROWSE HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _browse_exe_single(self):
        p = filedialog.askopenfilename(title="Select EXE to sign",
              filetypes=[("Executable","*.exe"),("All files","*.*")])
        if p:
            self._s_exe.set(p)
            if not self._s_out.get():
                base, ext = os.path.splitext(p)
                self._s_out.set(base + "_signed" + ext)

    def _browse_out_single(self):
        p = filedialog.asksaveasfilename(title="Save signed EXE as",
              defaultextension=".exe", filetypes=[("Executable","*.exe")])
        if p:
            self._s_out.set(p)

    def _batch_add(self):
        files = filedialog.askopenfilenames(title="Add EXE files",
                   filetypes=[("Executable","*.exe"),("All","*.*")])
        existing = {self._batch_tree.item(i)["values"][0]
                    for i in self._batch_tree.get_children()}
        for f in files:
            if f not in existing:
                self._batch_tree.insert("", "end", values=(f, "⏳ Pending"))
        self._batch_count.set(f"{len(self._batch_tree.get_children())} file(s)")

    def _batch_remove(self):
        for sel in self._batch_tree.selection():
            self._batch_tree.delete(sel)
        self._batch_count.set(f"{len(self._batch_tree.get_children())} file(s)")

    def _batch_clear(self):
        for i in self._batch_tree.get_children():
            self._batch_tree.delete(i)
        self._batch_count.set("0 files")

    def _batch_browse_out(self):
        p = filedialog.askdirectory(title="Output directory for batch")
        if p:
            self._batch_out_dir.set(p)

    # ══════════════════════════════════════════════════════════════════════
    #  CERT HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _randomize(self):
        d = random_cert_details()
        mapping = {"cn":"common_name","org":"organization","ou":"org_unit",
                   "country":"country","state":"state","locality":"locality",
                   "email":"email","days":"valid_days"}
        for k, dk in mapping.items():
            self._cert_vars[k].set(str(d[dk]))
        self._log(f"[🃏 CERT] {d['common_name']} | {d['country']} | "
                  f"{d['valid_days']} days\n", "accent")
        self._log(f"  {random.choice(CHAOS_LINES)}\n", "joker")

    def _collect_details(self):
        mapping = {"cn": "common_name", "org": "organization", "ou": "org_unit",
                   "country": "country", "state": "state", "locality": "locality",
                   "email": "email", "days": "valid_days"}
        return {mapping[k]: v.get().strip() for k, v in self._cert_vars.items()}

    def _get_settings(self):
        return dict(
            timestamp_url = TIMESTAMP_SERVERS.get(self._cfg_ts.get(), ""),
            hash_algo     = self._cfg_hash.get(),
            key_size      = int(self._cfg_ksize.get()),
        )

    def _export_cert(self):
        d = self._exp_dir.get().strip()
        if not d or not os.path.isdir(d):
            messagebox.showerror("CertOfChaos","Choose a valid export directory."); return
        details = self._collect_details()
        cfg = self._get_settings()
        try:
            c, k, cer, pfx = build_certificate(details, cfg["key_size"], cfg["hash_algo"])
            self._do_export_cert(c, k, cer, pfx, details, d)
            messagebox.showinfo("🃏 Chaos Exported", f"Certificate files saved to:\n{d}")
        except Exception as e:
            messagebox.showerror("CertOfChaos", str(e))

    def _do_export_cert(self, cert_pem, key_pem, cer_bytes, pfx_bytes, details, out_dir):
        slug = details["common_name"].replace(" ","_")[:24]
        os.makedirs(out_dir, exist_ok=True)
        for fname, data in [
            (f"{slug}.pfx",      pfx_bytes),
            (f"{slug}_cert.pem", cert_pem),
            (f"{slug}_key.pem",  key_pem),
            (f"{slug}.cer",      cer_bytes),
        ]:
            with open(os.path.join(out_dir, fname), "wb") as fh:
                fh.write(data)
        self._log(f"  💾 Cert exported → {out_dir}\n", "success")

    def _copy_cert_info(self):
        d = self._collect_details()
        info = "\n".join(f"{k}: {v}" for k, v in d.items())
        self.clipboard_clear()
        self.clipboard_append(info)
        self._set_status("🃏  Cert info copied to clipboard")

    # ══════════════════════════════════════════════════════════════════════
    #  PRESET MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════

    def _load_presets(self):
        if PRESETS_FILE.exists():
            try:
                return json.loads(PRESETS_FILE.read_text())
            except Exception:
                pass
        return {}

    def _save_presets_file(self):
        PRESETS_FILE.write_text(json.dumps(self._presets, indent=2))

    def _save_preset(self):
        name = self._preset_var.get().strip() or self._cert_vars["cn"].get().strip() or "preset"
        self._presets[name] = {k: v.get() for k, v in self._cert_vars.items()}
        self._save_presets_file()
        self._preset_cb.configure(values=list(self._presets.keys()))
        self._set_status(f"🃏  Preset '{name}' saved")

    def _load_preset(self):
        name = self._preset_var.get().strip()
        if name in self._presets:
            for k, v in self._presets[name].items():
                if k in self._cert_vars:
                    self._cert_vars[k].set(v)
            self._set_status(f"🃏  Preset '{name}' loaded")

    def _del_preset(self):
        name = self._preset_var.get().strip()
        if name in self._presets:
            del self._presets[name]
            self._save_presets_file()
            self._preset_cb.configure(values=list(self._presets.keys()))
            self._preset_var.set("")
            self._set_status(f"🃏  Preset '{name}' deleted")

    # ══════════════════════════════════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════════════════════════════════

    def _run_single(self):
        exe = self._s_exe.get().strip()
        out = self._s_out.get().strip()
        if not exe or not os.path.isfile(exe):
            messagebox.showerror("CertOfChaos","Select a valid input EXE."); return
        if not out:
            messagebox.showerror("CertOfChaos","Specify an output path."); return
        threading.Thread(target=self._sign_worker,
                         args=([exe],[out],self._s_verify.get(),self._s_export.get()),
                         daemon=True).start()

    def _run_verify_only(self):
        path = self._s_out.get().strip() or self._s_exe.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showerror("CertOfChaos","No file to verify."); return
        threading.Thread(target=self._verify_worker, args=(path,), daemon=True).start()

    def _verify_worker(self, path):
        self._log_sep()
        self._log(f"[VERIFY] {path}\n","accent")
        ok = verify_exe(path, self._log)
        if ok is True:
            self._log("  ✅ Signature valid\n","success")
        elif ok is False:
            self._log("  ❌ Signature invalid or not signed\n","error")
        else:
            self._log("  ⚠️  Could not verify (tool missing?)\n","warn")

    def _run_batch(self):
        items = self._batch_tree.get_children()
        if not items:
            messagebox.showinfo("CertOfChaos","Add some EXE files first."); return
        out_dir = self._batch_out_dir.get().strip()
        if not out_dir or not os.path.isdir(out_dir):
            messagebox.showerror("CertOfChaos","Choose a valid output directory."); return

        ins, outs = [], []
        suffix = self._batch_suffix.get() or "_signed"
        for iid in items:
            src = self._batch_tree.item(iid)["values"][0]
            base, ext = os.path.splitext(os.path.basename(src))
            dst = os.path.join(out_dir, base + suffix + ext)
            ins.append(src); outs.append(dst)
            self._batch_tree.item(iid, values=(src, "⏳ Queued"))

        threading.Thread(target=self._sign_worker,
                         args=(ins, outs, self._b_verify.get(), False),
                         daemon=True).start()

    def _sign_worker(self, in_files, out_files, do_verify, do_export):
        total = len(in_files)
        cfg   = self._get_settings()
        self._log_sep()
        self._log(f"[START] {total} file(s)  hash={cfg['hash_algo']}"
                  f"  key={cfg['key_size']}  ts={'yes' if cfg['timestamp_url'] else 'no'}\n","header")

        success_count = 0
        for idx, (exe_in, exe_out) in enumerate(zip(in_files, out_files)):
            self._set_status(f"🃏  Dealing cert {idx+1}/{total}: {os.path.basename(exe_in)}")
            self._set_progress((idx / total) * 90)

            if total > 1 and self._b_new_cert.get():
                self._randomize()

            details = self._collect_details()
            self._log(f"\n[{idx+1}/{total}] {os.path.basename(exe_in)}\n","accent")
            self._log(f"  Cert: {details['common_name']} | {details['country']}\n","dim")

            try:
                cert_pem, key_pem, cer_bytes, pfx_bytes = build_certificate(
                    details, cfg["key_size"], cfg["hash_algo"])
            except Exception as e:
                self._log(f"  ✗ Cert error: {e}\n","error")
                self._update_tree_row(exe_in, "❌ Cert error")
                continue

            with tempfile.TemporaryDirectory() as tmp:
                pfx_path = os.path.join(tmp, "cert.pfx")
                ca_path  = os.path.join(tmp, "cert.pem")
                with open(pfx_path, "wb") as fh: fh.write(pfx_bytes)
                with open(ca_path,  "wb") as fh: fh.write(cert_pem)

                ok = sign_exe(exe_in, pfx_path, exe_out,
                              cfg["timestamp_url"], cfg["hash_algo"], self._log)

                if ok and do_export:
                    exp_dir = self._exp_dir.get().strip() or os.path.dirname(exe_out)
                    self._do_export_cert(cert_pem, key_pem, cer_bytes,
                                         pfx_bytes, details, exp_dir)

                if ok and do_verify:
                    v = verify_exe(exe_out, self._log, ca_path)
                    status = "✅ Signed+Verified" if v else "⚠️ Signed/unverified"
                elif ok:
                    status = "✅ Signed"
                else:
                    status = "❌ Failed"

            self._update_tree_row(exe_in, status)
            if ok: success_count += 1
            self._log(f"  → {status}\n","success" if ok else "error")

        self._set_progress(100)
        self._log_sep()
        self._log(f"[DONE] {success_count}/{total} chaos cert(s) deployed.\n",
                  "success" if success_count == total else "warn")
        self._set_status(f"🃏  Done — {success_count}/{total} succeeded")

        if self._cfg_open_out.get() and out_files:
            out_dir = os.path.dirname(out_files[0])
            if os.path.isdir(out_dir):
                try:
                    if sys.platform == "win32":    os.startfile(out_dir)
                    elif sys.platform == "darwin":  subprocess.Popen(["open",   out_dir])
                    else:                           subprocess.Popen(["xdg-open", out_dir])
                except Exception:
                    pass

        self.after(2500, lambda: self._set_progress(0))

    def _update_tree_row(self, path, status):
        def _do():
            for iid in self._batch_tree.get_children():
                if self._batch_tree.item(iid)["values"][0] == path:
                    self._batch_tree.item(iid, values=(path, status))
        self.after(0, _do)

    # ══════════════════════════════════════════════════════════════════════
    #  ABOUT  🃏
    # ══════════════════════════════════════════════════════════════════════

    def _show_about(self):
        w = tk.Toplevel(self)
        w.title("About CertOfChaos")
        w.configure(bg=C["card"])
        w.resizable(False, False)
        w.geometry("400x360")

        # Header
        tk.Label(w, text="🃏  CertOfChaos", font=("Segoe UI", 16, "bold"),
                 bg=C["card"], fg=C["accent"]).pack(pady=(20,2))
        tk.Label(w, text="v2.0  ·  Why so serious about certificates?",
                 font=("Segoe UI", 9, "italic"), bg=C["card"], fg=C["fg_dim"]).pack()
        tk.Label(w, text="♠  ♣  ♥  ♦",
                 font=("Segoe UI", 13), bg=C["card"],
                 fg=C["warning"]).pack(pady=(4,0))

        tk.Frame(w, bg=C["border"], height=1).pack(fill="x", padx=20, pady=10)

        features = [
            "🃏  Random certificate generation (every run)",
            "♠  Single & batch EXE signing",
            "♣  SHA-256 / SHA-384 / SHA-512 support",
            "♥  RSA 2048 / 3072 / 4096 key sizes",
            "♦  Timestamp server selection (6 servers)",
            "🃏  Export .pfx  .pem  .cer  files",
            "♠  Cert preset save / load / delete",
            "♣  Self-signed cert verify (CA-aware)",
            "♥  Color-coded chaos log with copy/clear",
        ]
        for line in features:
            tk.Label(w, text=line, font=FONT_SMALL,
                     bg=C["card"], fg=C["fg"]).pack(anchor="w", padx=28, pady=1)

        tk.Frame(w, bg=C["border"], height=1).pack(fill="x", padx=20, pady=8)
        tk.Label(w, text=random.choice(CHAOS_LINES),
                 font=("Segoe UI", 8, "italic"), bg=C["card"],
                 fg=C["warning"], wraplength=340).pack(padx=20)

        ttk.Button(w, text="Close", style="Dim.TButton",
                   command=w.destroy).pack(pady=10)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        import cryptography  # noqa
    except ImportError:
        print("ERROR: Missing dependency.\nRun: pip install cryptography")
        sys.exit(1)

    app = App()
    app.mainloop()