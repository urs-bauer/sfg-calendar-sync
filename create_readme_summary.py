from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

file_path = "GitHub_Calendar_Guide.pdf"
doc = SimpleDocTemplate(file_path, pagesize=A4,
                        rightMargin=40, leftMargin=40,
                        topMargin=40, bottomMargin=40)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle",
    parent=styles["Title"],
    fontSize=20,
    spaceAfter=20,
    textColor=colors.darkblue
)

h1 = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=14,
    spaceAfter=10,
    textColor=colors.HexColor("#1f4e79")
)

h2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=12,
    spaceAfter=6,
    textColor=colors.black
)

body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=10,
    leading=14
)

code = ParagraphStyle(
    "Code",
    parent=styles["BodyText"],
    fontName="Courier",
    fontSize=9,
    backColor=colors.whitesmoke,
    leading=12
)

content = []

def add_title(text):
    content.append(Paragraph(text, title_style))
    content.append(Spacer(1, 12))

def add_h1(text):
    content.append(Paragraph(text, h1))
    content.append(Spacer(1, 6))

def add_h2(text):
    content.append(Paragraph(text, h2))

def add_text(text):
    content.append(Paragraph(text, body))
    content.append(Spacer(1, 8))

def add_code(text):
    content.append(Paragraph(f"<pre>{text}</pre>", code))
    content.append(Spacer(1, 8))

# -------------------------
# TITEL
# -------------------------
add_title("GitHub Calendar Sync – Vollständiger Leitfaden")

# -------------------------
# KAPITEL 1
# -------------------------
add_h1("1. Überblick")

add_text("""
Dieses Projekt erzeugt automatisch eine iCal-Datei (.ics) mit Python
und synchronisiert sie über GitHub Actions und GitHub Pages mit Google Kalender.

Es wird KEIN eigener Server benötigt.
""")

# -------------------------
# KAPITEL 2
# -------------------------
add_h1("2. Systemarchitektur")

add_text("""
Python Skript → erzeugt kalender.ics
↓
GitHub Actions → automatischer täglicher / stündlicher Lauf
↓
GitHub Repository → speichert Datei
↓
GitHub Pages → stellt ICS öffentlich bereit
↓
Google Kalender → abonniert URL
""")

# -------------------------
# SCHRITTE 1–4
# -------------------------
add_h1("3. GitHub Setup (Schritt 1–4)")

add_text("""
- GitHub Account erstellen
- Neues Repository anlegen (public)
- Repository lokal klonen
- Python Projektstruktur erstellen
""")

add_code("""
git clone https://github.com/USER/REPO.git
cd REPO
""")

# -------------------------
# SCHRITTE 5–7
# -------------------------
add_h1("4. Python & GitHub Actions (Schritt 5–7)")

add_text("""
requirements.txt definiert externe Abhängigkeiten.
""")

add_code("""
requests
ics
beautifulsoup4
reportlab
""")

add_text("""
GitHub Actions Workflow führt das Skript regelmäßig aus.
""")

add_code("""
on:
  schedule:
    - cron: '0 */6 * * *'
""")

# -------------------------
# SCHRITTE 8–9
# -------------------------
add_h1("5. Automatisierung (Schritt 8–9)")

add_text("""
Workflow manuell starten oder automatisch laufen lassen.

GitHub Actions:
- installiert Dependencies
- führt Python Skript aus
- commitet kalender.ics automatisch
""")

# -------------------------
# SCHRITTE 10–12
# -------------------------
add_h1("6. Hosting & Google Kalender (Schritt 10–12)")

add_text("""
GitHub Pages aktiviert eine öffentliche URL:

https://USERNAME.github.io/REPO/kalender.ics
""")

add_text("""
Google Kalender:
- „Weitere Kalender → Per URL“
- ICS Link einfügen
""")

# -------------------------
# GIT ANHANG
# -------------------------
add_h1("7. Anhang – Git Befehle")

add_code("""
git status
git add .
git commit -m "message"
git push

git reset
git reset HEAD~1
git reset HEAD~2
""")

# -------------------------
# TOKEN ANHANG
# -------------------------
add_h1("8. GitHub Login & Token")

add_text("""
GitHub akzeptiert KEINE Passwörter mehr für Git.

Stattdessen wird ein Personal Access Token verwendet.
""")

add_code("""
Username: GitHub Username
Password: Personal Access Token
""")

add_text("""
Token erstellen:
https://github.com/settings/tokens

Benötigte Rechte:
- repo
- workflow
""")

# -------------------------
# EXPORT
# -------------------------
doc.build(content)

print("PDF erstellt: GitHub_Calendar_Guide.pdf")
