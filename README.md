```
 ██████╗███████╗██████╗ ████████╗ ██████╗ ███████╗ ██████╗██╗  ██╗ █████╗  ██████╗ ███████╗
██╔════╝██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔════╝██║  ██║██╔══██╗██╔═══██╗██╔════╝
██║     █████╗  ██████╔╝   ██║   ██║   ██║█████╗  ██║     ███████║███████║██║   ██║███████╗
██║     ██╔══╝  ██╔══██╗   ██║   ██║   ██║██╔══╝  ██║     ██╔══██║██╔══██║██║   ██║╚════██║
╚██████╗███████╗██║  ██║   ██║   ╚██████╔╝██║     ╚██████╗██║  ██║██║  ██║╚██████╔╝███████║
 ╚═════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

<div align="center">

**`[ SELF-SIGNED CERTIFICATE GENERATION & PE SIGNING UTILITY ]`**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Use](https://img.shields.io/badge/Use-Authorized%20Research%20Only-red?style=for-the-badge)

```
╔─────────────────────────────────────────────────────────────────╗
│  ⚠  FOR AUTHORIZED SECURITY RESEARCH AND LAB USE ONLY  ⚠      │
╚─────────────────────────────────────────────────────────────────╝
```

</div>

---

## ◈ OVERVIEW

**CertOfChaos** is a GUI-based toolkit for generating self-signed code-signing certificates and applying them to PE (`.exe`) binaries. Designed for security researchers, red teamers, and penetration testers who need to study Authenticode validation, test EDR behavior in isolated lab environments, or quickly generate internal test certificates without spinning up a full PKI.

---

## ◈ DISCLAIMER

> This software is intended **exclusively for authorized security research, red team lab operations, CTF environments, and legitimate development pipeline testing.**

- Use only on systems and executables **you own or have explicit written authorization to test**
- Certificates produced by this tool are **self-signed** — they carry no CA trust chain and will not pass Windows SmartScreen or standard OS certificate validation
- Applying signatures to binaries **without authorization**, using them to **impersonate legitimate publishers**, or deploying them to **evade security controls on systems you do not own** is illegal under the CFAA (US), Computer Misuse Act (UK), and equivalent statutes globally
- The maintainers of this repository **accept no liability** for unauthorized or malicious use

---

## ◈ FEATURE MATRIX

| Module | Capability |
|---|---|
| 🃏 **Cert Generator** | Random or custom-built self-signed X.509 certificates |
| ✍ **Single Sign** | Sign one PE binary; optional post-sign verification |
| 📦 **Batch Sign** | Sign entire queues; optional unique cert per file |
| 💾 **Export** | Dump `.pfx` · `.pem` · `.cer` to any directory |
| 🔍 **Verify** | Inspect Authenticode signatures on signed binaries |
| ⚙ **Settings** | Hash algorithm · RSA key size · Timestamp server |
| 📋 **Presets** | Save, load, and delete named certificate profiles |

---

## ◈ SYSTEM REQUIREMENTS

**Python dependency**
```bash
pip install cryptography
```

**Signing backend**

| OS | Tool | Install Command |
|---|---|---|
| Linux | `osslsigncode` | `sudo apt install osslsigncode` |
| macOS | `osslsigncode` | `brew install osslsigncode` |
| Windows | `signtool` | Windows SDK / Visual Studio |

---

## ◈ QUICKSTART

```bash
git clone https://github.com/YOUR_USERNAME/CertOfChaos.git
cd CertOfChaos
pip install cryptography
python signer.py
```

---

## ◈ INTERFACE GUIDE

```
┌──────────────────────────────────────────────────────────────┐
│  ✍ Single Sign  │  📦 Batch Sign  │  🃏 Certificate  │  ⚙  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   INPUT  ──▶  CERT GENERATION  ──▶  SIGN  ──▶  VERIFY      │
│                                                              │
│  [ Chaos Log ]────────────────────────────────────────────  │
│  > Certificate issued · Signing complete · Status           │
└──────────────────────────────────────────────────────────────┘
```

| Tab | What to do |
|---|---|
| **✍ Single Sign** | Browse for an input EXE, set an output path, hit *Deal the Cert* |
| **📦 Batch Sign** | Add multiple EXEs, set an output directory and name suffix, hit *Release the Chaos* |
| **🃏 Certificate** | Randomize or manually fill cert fields; load/save presets; export cert files |
| **⚙ Settings** | Pick your timestamp server, hash algorithm (SHA-256/384/512), and RSA key size (2048/3072/4096) |

---

## ◈ UNDERSTANDING SELF-SIGNED CERTIFICATES

```
  PUBLIC CA CHAIN                    CERTOFCHAOS
  ───────────────                    ────────────
  DigiCert Root CA                   Your Cert  ◀── self-signed
       │                             (no chain)
  Intermediate CA
       │                   ✘ SmartScreen will NOT trust this
  Your Code Cert            ✘ Windows Defender will NOT trust this
       │                    ✔ Useful for lab/research contexts
  Signed Binary             ✔ Useful for internal signing pipelines
```

Self-signed certs are useful for studying how security tooling **reacts to any signature vs. no signature**, not for bypassing production trust chains.

---

## ◈ LEGITIMATE USE CASES

- **Red team labs** — observe how EDR and AV products treat signed vs. unsigned payloads in isolated, authorized environments
- **Security research** — study Windows Authenticode, PE format, and certificate metadata handling
- **CTF / training** — practice binary signing and certificate manipulation in safe, controlled challenges
- **Internal dev pipelines** — sign test builds where a commercial certificate is unnecessary overhead

---

## ◈ CONTRIBUTING

Bug fixes, additional signing backend support (e.g. `jsign`), and UI improvements are welcome via pull request.
Please do not submit features that specifically target production system evasion outside of documented research contexts.

---

## ◈ LICENSE

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for full terms.

---

<div align="center">

```
[ CertOfChaos · Self-signed · Self-aware · Definitely not suspicious ]
```

</div>
