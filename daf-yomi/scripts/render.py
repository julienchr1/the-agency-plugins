#!/usr/bin/env python3
"""Markdown -> HTML -> PDF pour les fiches Daf Yomi.

  python3 scripts/render.py fiches/Bekhorot_5_B.md

Reprend la mise en page et les correctifs de michna-yomit : blocs hebreux en
RTL qui se replient, pas de debordement a l'impression, detection de Chromium
sur macOS comme sous Linux.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
CHROME_BINARIES = ["chromium", "chromium-browser", "google-chrome",
                   "google-chrome-stable", "chrome", "headless_shell"]


def find_chrome():
    env = os.environ.get("DAF_CHROME") or os.environ.get("MICHNA_CHROME")
    if env and (os.path.exists(env) or shutil.which(env)):
        return env if os.path.exists(env) else shutil.which(env)
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    for b in CHROME_BINARIES:
        f = shutil.which(b)
        if f:
            return f
    return None


CSS = """
@page { size: A4; margin: 17mm 15mm; }
body { font-family: "Times New Roman", Times, serif; font-size: 11pt;
  line-height: 1.5; color: #1a1a1a; max-width: 760px; margin: 0 auto; }
@media print { body { max-width: 100%; margin: 0; } }

h1 { font-size: 20pt; margin: 0 0 6pt; color: #1d3f5e;
     border-bottom: 2.5px solid #1d3f5e; padding-bottom: 6pt; }
h2 { font-size: 13.5pt; margin: 18pt 0 7pt; color: #1d3f5e;
     border-bottom: 1px solid #dde3e8; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 5pt; color: #444; }
p { margin: 6pt 0; text-align: justify; }
hr { border: none; border-top: 1px solid #dde3e8; margin: 14pt 0; }

/* Blocs cites : l'arameen est detecte et bascule en RTL. */
blockquote { margin: 9pt 0; padding: 9pt 12pt; background: #f6f8fa;
  border-left: 3px solid #1d3f5e; }
blockquote p { margin: 4pt 0; text-align: left; }
.he, blockquote.rtl p.he {
  direction: rtl; text-align: right;
  unicode-bidi: embed; unicode-bidi: isolate;
  overflow-wrap: break-word; word-wrap: break-word; white-space: normal;
  max-width: 100%; box-sizing: border-box;
  font-family: "Times New Roman", "Arial Hebrew", "SF Hebrew", "FreeSerif", serif;
  font-size: 13pt; line-height: 1.85; }

table { border-collapse: collapse; width: 100%; margin: 9pt 0; font-size: 10pt; }
th, td { border: 1px solid #dde3e8; padding: 4pt 7pt; text-align: left;
         vertical-align: top; }
th { background: #eef2f6; color: #1d3f5e; font-weight: bold; }
ul, ol { margin: 6pt 0 6pt 16pt; } li { margin: 3pt 0; }
a { color: #1d3f5e; text-decoration: none; }
em { font-style: italic; } strong { font-weight: bold; }
code { font-family: inherit; background: #eef2f6; padding: 0 2px; }
"""

HEB = re.compile(r"[֐-׿]")


def mark_rtl(html: str) -> str:
    """Ajoute class=he aux paragraphes majoritairement hebreux."""
    def fix(m):
        inner = m.group(1)
        txt = re.sub(r"<[^>]+>", "", inner)
        heb = len(HEB.findall(txt))
        if heb and heb > len(txt.strip()) * 0.25:
            return f'<p class="he">{inner}</p>'
        return m.group(0)
    return re.sub(r"<p>(.*?)</p>", fix, html, flags=re.S)


def md_to_html(md_path: str, html_path: str) -> str:
    body = subprocess.run(
        ["pandoc", "-f", "markdown+pipe_tables+yaml_metadata_block",
         "-t", "html5", md_path],
        capture_output=True, text=True, check=True).stdout
    body = mark_rtl(body)
    title = os.path.splitext(os.path.basename(md_path))[0]
    html = ('<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">'
            f"<title>{title}</title><style>{CSS}</style></head><body>"
            + body + "</body></html>")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return html_path


def html_to_pdf(html_path: str, pdf_path: str):
    # Chrome exige un chemin ABSOLU derriere file:// — un chemin relatif est
    # interprete comme un nom d'hote et produit une page d'erreur... qui
    # s'imprime en PDF sans erreur visible.
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)
    chrome = find_chrome()
    if not chrome:
        return False, "aucun navigateur trouve (definir DAF_CHROME)"
    prof = os.path.join("/tmp", "daf-yomi-chrome")
    os.makedirs(prof, exist_ok=True)
    # Chrome headless ecrit le PDF puis ne rend pas toujours la main : un
    # timeout n'est donc PAS une preuve d'echec. On verifie le fichier apres.
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox",
             "--no-first-run", "--no-default-browser-check",
             "--disable-extensions", "--disable-sync",
             "--virtual-time-budget=4000",
             f"--user-data-dir={prof}", "--no-pdf-header-footer",
             f"--print-to-pdf={pdf_path}", "file://" + html_path],
            capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        subprocess.run(["pkill", "-f", prof], capture_output=True)
    except Exception as exc:
        return False, str(exc)
    if not (os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000):
        return False, "PDF vide"
    # Un PDF peut exister et ne contenir qu'une page d'erreur du navigateur :
    # on le detecte plutot que d'annoncer un succes.
    with open(pdf_path, "rb") as fh:
        head = fh.read(400000)
    for bad in (b"ERR_INVALID_URL", b"ERR_FILE_NOT_FOUND", b"site can",
                b"t be reached"):
        if bad in head:
            return False, "page d'erreur du navigateur — verifier le chemin"
    return True, os.path.basename(chrome)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: render.py <fichier.md> [...]")
    for md in sys.argv[1:]:
        base = os.path.splitext(md)[0]
        html = base + ".html"
        pdf = base + ".pdf"
        md_to_html(md, html)
        ok, info = html_to_pdf(html, pdf)
        size = os.path.getsize(pdf) // 1024 if ok else 0
        print(f"  {os.path.basename(md)}")
        print(f"    -> {os.path.basename(html)}")
        print(f"    -> {os.path.basename(pdf)}  " +
              (f"{size} Ko  ({info})" if ok else f"ECHEC : {info}"))


if __name__ == "__main__":
    main()
