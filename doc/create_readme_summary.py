from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

doc = SimpleDocTemplate(
    "GitHub_Calendar_Runbook.pdf",
    pagesize=A4,
    rightMargin=40, leftMargin=40,
    topMargin=40, bottomMargin=40
)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "title",
    parent=styles["Title"],
    fontSize=20,
    textColor=colors.darkblue,
    spaceAfter=18
)

h1 = ParagraphStyle(
    "h1",
    parent=styles["Heading1"],
    fontSize=14,
    textColor=colors.HexColor("#1f4e79"),
    spaceAfter=10
)

body = ParagraphStyle(
    "body",
    parent=styles["BodyText"],
    fontSize=10,
    leading=14
)

code = ParagraphStyle(
    "code",
    fontName="Courier",
    fontSize=9,
    backColor=colors.whitesmoke,
    leading=12
)

content = []

def T(text):
    content.append(Paragraph(text, title))
    content.append(Spacer(1, 12))

def H(text):
    content.append(Paragraph(text, h1))
    content.append(Spacer(1, 6))

def P(text):
    content.append(Paragraph(text, body))
    content.append(Spacer(1, 10))

def C(text):
    content.append(Preformatted(text, code))
    content.append(Spacer(1, 12))


# =========================================================
# TITEL
# =========================================================
T("GitHub Calendar Sync – Vollständiges technisches Runbook")

# =========================================================
# 1 ZIEL
# =========================================================
H("1. Ziel des Systems (Warum existiert das?)")

P("""
Dieses System automatisiert die Erstellung einer iCalendar-Datei (.ics)
aus einem Python-Skript und veröffentlicht diese regelmäßig über GitHub.

Die Datei wird anschließend von Google Calendar abonniert.

Wichtig:
- Kein eigener Server notwendig
- Vollständig automatisiert
- Aktualisierung erfolgt zeitgesteuert über GitHub Actions
""")

# =========================================================
# 2 ARCHITEKTUR
# =========================================================
H("2. Architektur (wie das System funktioniert)")

C("""
Python Script (Logik)
    ↓
GitHub Repository (Code + Dateiablage)
    ↓
GitHub Actions (automatische Ausführung)
    ↓
GitHub Pages (öffentliche URL)
    ↓
Google Calendar (liest ICS Datei)
""")

P("""
Wichtiges Verständnis:
GitHub Actions ist kein Server, sondern ein temporärer Runner.
Er startet, führt das Skript aus und verschwindet wieder.
""")

# =========================================================
# 3 SETUP SCHRITTE
# =========================================================
H("3. Schritt 1 – GitHub Konto")

P("""
Ein GitHub Konto wird benötigt, um:
- Code zu speichern
- Automatisierungen (Actions) zu nutzen
- Datei öffentlich bereitzustellen (Pages)
""")

# =========================================================
H("4. Schritt 2 – Repository erstellen")

P("""
Repository ist der zentrale Speicherort für:
- Python Skript
- Workflow Definition
- erzeugte Kalenderdatei
""")

P("""
Wichtig:
Repository muss PUBLIC sein, sonst funktioniert GitHub Pages nicht ohne Einschränkungen.
""")

# =========================================================
H("5. Schritt 3 – Repository klonen")

C("""
git clone https://github.com/USER/REPO.git
cd REPO
""")

P("""
Was passiert hier?
- Git lädt Projekt lokal herunter
- du arbeitest auf deinem Rechner
- Änderungen werden später zurück hochgeladen
""")

P("""
Typischer Fehler:
GitHub akzeptiert KEINE Passwörter mehr bei HTTPS Git Zugriff.
→ Lösung: Personal Access Token verwenden
""")

# =========================================================
H("6. Schritt 4 – Projektstruktur")

P("""
Benötigte Dateien:
- generate_calendar.py → erzeugt ICS Datei
- requirements.txt → Python Abhängigkeiten
- .github/workflows/update.yml → Automatisierung
""")

# =========================================================
H("7. Schritt 5 – requirements.txt")

P("""
Diese Datei definiert externe Bibliotheken.

Nur Pakete, die NICHT Teil von Python sind.
""")

C("""
requests
ics
beautifulsoup4
reportlab
""")

P("""
Fehlerquelle:
Wenn hier etwas fehlt → GitHub Action bricht mit "Module not found" ab.
""")

# =========================================================
H("8. Schritt 6 – Python Skript")

P("""
Das Skript erzeugt die Datei kalender.ics.

Wichtig:
- jedes Event benötigt stabile UID
- Zeit muss korrekt gesetzt sein (UTC empfohlen)
""")

P("""
Fehlerquelle:
Wenn UID sich ändert → Google Calendar erstellt doppelte Termine.
""")

# =========================================================
H("9. Schritt 7 – GitHub Actions")

P("""
GitHub Actions führt das Skript automatisch aus.
""")

C("""
on:
  schedule:
    - cron: '0 */6 * * *'
""")

P("""
Bedeutung:
- alle 6 Stunden
- Zeit basiert auf UTC
""")

# =========================================================
H("10. Schritt 8 – Git Befehle (ERKLÄRUNG)")

P("""
Git arbeitet in 3 Stufen:
""")

C("""
1. Arbeitsverzeichnis
   → Datei wurde geändert

2. Staging Area (git add)
   → Änderungen vorgemerkt

3. Commit (git commit)
   → lokaler Versions-Snapshot

4. Remote (git push)
   → Upload zu GitHub
""")

P("""
Warum diese Trennung?
→ Du kannst Änderungen sammeln bevor du sie veröffentlichst
→ Versionen bleiben nachvollziehbar
""")

# =========================================================
H("11. Schritt 9 – Git Reset (Fehlerkorrektur)")

P("""
Reset wird genutzt, wenn etwas falsch gespeichert wurde.
""")

C("""
git reset
→ entfernt Staging

git reset HEAD~1
→ letzten Commit entfernen (Dateien bleiben)

git reset --hard HEAD~1
→ alles löschen (gefährlich)
""")

P("""
Warnung:
--hard löscht echte Arbeit unwiederbringlich.
""")

# =========================================================
H("12. Schritt 10 – GitHub Actions Debugging")

P("""
Fehleranalyse erfolgt im GitHub Actions Tab.
""")

P("""
Typische Fehler:
- Module not found → requirements.txt fehlt
- Authentication failed → Token falsch
- Workflow permission error → workflow scope fehlt
""")

# =========================================================
H("13. Schritt 11 – GitHub Pages")

P("""
Aktivierung:
Settings → Pages → Deploy from branch
""")

P("""
Ergebnis:
Öffentliche URL zur ICS Datei
""")

C("""
https://USER.github.io/REPO/kalender.ics
""")

# =========================================================
H("14. Schritt 12 – Google Kalender")

P("""
Google Kalender abonniert die ICS Datei per URL.
""")

P("""
Wichtig:
- Aktualisierung kann 1–24 Stunden dauern
- Google cached externe Kalender
""")

# =========================================================
H("15. Cron Übersicht")

C("""
0 * * * *      → jede Stunde
0 */2 * * *    → alle 2 Stunden
0 */6 * * *    → alle 6 Stunden
0 5 * * *      → täglich 05:00 UTC
""")

# =========================================================
H("16. Gesamt-Fehlerdiagnose (WICHTIG)")

P("""
Wenn etwas nicht funktioniert:

1. Läuft GitHub Action?
   → sonst kein Update

2. Wird kalender.ics erzeugt?
   → sonst Python Fehler

3. Ist Pages aktiv?
   → sonst keine URL

4. Sieht Google alte Daten?
   → nur Cache Problem
""")

# =========================================================
doc.build(content)

print("PDF erstellt: GitHub_Calendar_Runbook.pdf")
