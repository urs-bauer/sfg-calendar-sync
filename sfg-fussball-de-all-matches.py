#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from ics import Calendar, Event
from datetime import datetime, timedelta
import hashlib
import argparse
import sys
from bs4 import BeautifulSoup
import re
from zoneinfo import ZoneInfo

# Für PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors

# -------------------------------
# Kommandozeilen-Argumente
# -------------------------------

default_time = "2026-05-01"
parser = argparse.ArgumentParser(description="Exportiere Heimspiele als iCal-Datei von fussball.de")
parser.add_argument("output", help="Name der ICS-Datei, z.B. grosssachsenheim.ics")
#parser.add_argument("--start", help="Startdatum YYYY-MM-DD", default=datetime.today().strftime("%Y-%m-%d"))
parser.add_argument("--start", help="Startdatum YYYY-MM-DD", default=datetime.strptime(default_time, "%Y-%m-%d"))
#parser.add_argument("--end", help="Enddatum YYYY-MM-DD", default=(datetime.today() + timedelta(days=365)).strftime("%Y-%m-%d"))
parser.add_argument("--end", help="Enddatum YYYY-MM-DD", default=(datetime.strptime(default_time, "%Y-%m-%d") + timedelta(days=200)).strftime("%Y-%m-%d"))
parser.add_argument(
    "--verbose",
    action='store_const',   # Speichert einen konstanten Wert, wenn das Flag gesetzt ist
    const=1,                # Wert, wenn Flag vorhanden
    default=0,              # Wert, wenn Flag nicht vorhanden
    help="use for additional output in cmd-windows"
)

args = parser.parse_args()

OUTPUT = args.output
START_DATE = args.start
END_DATE = args.end
VERBOSE = args.verbose
#print("Verbose:", VERBOSE)

# -------------------------------
# Vereins-ID (Spfr. Großsachsenheim)
# -------------------------------
# SFG = 00ES8GNAUG00009PVV0AG08LVUPGND5I
# TSV = 00ES8GNAVO00004CVV0AG08LVUPGND5I
CLUB_ID = "00ES8GNAUG00009PVV0AG08LVUPGND5I" #SFG
#CLUB_ID = "00ES8GNAVO00004CVV0AG08LVUPGND5I" #TSV

#Team-ID:
#Herren 1    : 02TBF79BN8000000VS5489BSVV9JRPRB
#TEAM_ID = "02TBF79BN8000000VS5489BSVV9JRPRB" # Herren 1

#Herren 2    : 02TBF8134G000000VS5489BSVV9JRPRB
#TEAM_ID = "02TBF8134G000000VS5489BSVV9JRPRB" # Herren 2

#B-Jugend    : 02ERS8UR28000000VS5489B1VT0RKM5V
#C-Jugend C1 : 02EUOFER4O000000VS5489B2VVP292BR
#C-Jugend C2 : 02Q2PC6HUK000000VS5489B2VT450JFN
#D-Jugend D1 : 011MIE8UOG000000VTVG0001VTR8C1K7
#D-Jugend D2 : 02ERS89HS8000000VS5489B1VT0RKM5V
#E-Jugend E1 : 011MIFC2KK000000VTVG0001VTR8C1K7
#E-Jugend E2 : 02GMPEBCOS000000VS5489B2VSQM9PFD

# Anzahl an Spielen die abgerufen werden sollen
MAX_GAMES = 200  # kann beliebig angepasst werden

# ----------------
# Spielort abrufen
# ----------------
SHOW_LOCATION = "show-venues/checked/"
#SHOW_LOCATION = ""

# -------------------------------
# JSON-URL zusammenbauen
# -------------------------------
# match-type = -1 = alle Spiele
# match-type =  1 = Heimspiele
# match-type =  2 = Auswaertsspiele

try:
    TEAM_ID
except NameError:
    # TEAM_ID existiert nicht
    # Vereinsspielplan alle Spiele 
    URL = (
        f"https://www.fussball.de/ajax.club.matchplan/-/id/{CLUB_ID}/"
        f"mime-type/JSON/mode/PAGE/show-filter/false/max/{MAX_GAMES}/"
        f"datum-von/{START_DATE}/datum-bis/{END_DATE}/"
        f"match-type/-1/{SHOW_LOCATION}offset/0"
    )
else:
    # TEAM_ID existiert
    # Teamspielplan (TEAM_ID) alle Spiele
    URL = (
        f"https://www.fussball.de/ajax.club.matchplan/-/id/{CLUB_ID}/team-id/{TEAM_ID}/"
        f"mime-type/JSON/mode/PAGE/show-filter/false/max/{MAX_GAMES}/"
        f"datum-von/{START_DATE}/datum-bis/{END_DATE}/"
        f"match-type/-1/{SHOW_LOCATION}offset/0"
    )

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "Gecko/20100101 Firefox/128.0"
    )
}

print(f"Lade Spiele von {START_DATE} bis {END_DATE} von fussball.de ...")

# request json data from fussball.de (URL)
try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    print("Fehler beim Laden der JSON-Daten:", e)
    sys.exit(1)

# write json data to file
data = response.json()

if "html" not in data:
    print("Keine Spiele gefunden oder JSON-Format hat sich geändert.")
    sys.exit(1)

with open("json.txt", "w", encoding="utf-8") as fj:
    json.dump(data, fj, ensure_ascii=False, indent=2)  # schöne Formatierung

data_html = data['html']
soup = BeautifulSoup(data_html, "html.parser")

print("+++ Daten werden geladen und verarbeitet +++")
# Ergebnisliste
matches = []

# iCal
calendar = Calendar()
calendar.timezone = "Europe/Berlin"
events = 0

# Alle 'row-competition'-Zeilen durchgehen
for row in soup.find_all("tr", class_="row-competition"):
    # Datum / Uhrzeit
    date_td = row.find("td", class_="column-date")
    date_time_text = date_td.get_text(strip=True) if date_td else ""

    # Datum und Uhrzeit trennen
    dt = None
    # Beispiel für Parsing von date_time_text
    date_time_text = date_time_text.strip()  # z.B. "16.05.26 |" oder "16.05.26 |10:30"

    if not "**" in date_time_text:  # Datum enthaelt "**" wenn mehr Datensaetze abgerufen werden, als Spiele hinterlegt sind

        try:
            if "|" in date_time_text:  # Datum ist vorhanden (mit oder ohne Uhrzeit)
                # Entferne Wochentag
                if "," in date_time_text:
                    date_part, time_part = date_time_text.split(",", 1)[1].split("|", 1)
                else:
                   date_part, time_part = date_time_text.split("|", 1)
                date_part = date_part.strip()  # z.B. "16.05.26"
                time_part = time_part.strip()  # z.B. "10:30" oder ""

                if time_part:  # Uhrzeit vorhanden
                    dt = datetime.strptime(f"{date_part} {time_part}", "%d.%m.%y %H:%M")
                else:  # keine Uhrzeit -> 00:00 Uhr
                    dt = datetime.strptime(date_part, "%d.%m.%y")
                    dt = dt.replace(hour=0, minute=0)

                last_date = dt.date()  # merken für Zeilen nur mit Uhrzeit
            else:  # nur Uhrzeit vorhanden, Datum vom vorherigen Event nehmen
                if last_date is not None:
                    t = datetime.strptime(date_time_text, "%H:%M").time()
                    dt = datetime.combine(last_date, t)
                else:
                    print(f"Warnung: Kein Datum vorhanden für Uhrzeit: '{date_time_text}'")
        except ValueError:
            print(f"Warnung: Konnte Datum/Uhrzeit nicht parsen: '{date_time_text}'")
            dt = None

        # Zeitzone ergänzen
        dt = dt.replace(tzinfo=ZoneInfo("Europe/Berlin"))

        # Jugend / Wettbewerb
        team_td = row.find("td", class_="column-team")
        youth_team = team_td.get_text(strip=True) if team_td else ""

        # MATCH_ID
        match_id = None

        # Alle td-Zellen der row durchsuchen
        all_tds = row.find_all("td")

        for td in all_tds:
            td_text = td.get_text(" ", strip=True)

            # Suche nach "... | 123456789"
            m = re.search(r"[A-Z]{2}\s*\|\s*(\d+)", td_text)

            if m:
                match_id = m.group(1)
                break

        # Die beiden aufeinanderfolgenden 'column-club'-Zellen für Heim- und Gastverein
        next_row = row.find_next_sibling("tr")
        home_club_td = next_row.find("td", class_="column-club") if next_row else None
        guest_club_td = next_row.find("td", class_="column-club no-border") if next_row else None

        home_club = home_club_td.get_text(strip=True) if home_club_td else ""
        home_club = home_club.replace("\u200b", "").replace("\xa0", "").strip()
        guest_club = guest_club_td.get_text(strip=True) if guest_club_td else ""
        guest_club = guest_club.replace("\u200b", "").replace("\xa0", "").strip()

        # Anpassung: Wenn SGM in home_club, entferne federführenden Vereinsnamen "TSV Kleinsachsenheim" oder "Spfr Großsachsenheim" oder "(Spfr Großs)"
        if "SGM" in home_club:
            for clubname in ["TSV Kleinsachsenheim", "Spfr Großsachsenheim", "(Spfr Großs)"]:
                home_club = home_club.replace(clubname, "").strip()

        if "SGM" in guest_club:
            for clubname in ["TSV Kleinsachsenheim", "Spfr Großsachsenheim", "(Spfr Großs)"]:
                guest_club = guest_club.replace(clubname, "").strip()
              
        # Ort aus 'row-venue'
        venue_row = next_row.find_next_sibling("tr", class_="row-venue") if next_row else None
        venue_td = venue_row.find("td", colspan="3") if venue_row else None
        venue = venue_td.get_text(strip=True) if venue_td else ""
        venue = venue.replace("\u200b", "").replace("\xa0", "").strip()
#        venue = re.sub(r"\s+", " ", venue)
        for v in ["Rasenplatz, In den Steingruben,", "Rasenplatz, Löchgauerstrasse 60,", "Rasenplatz, In den Steingruben Rasenplatz I,", "Rasenplatz, In den Steingruben Rasenplatz II,"]:
            venue = venue.replace(v, "").strip()

        # Alles in Dictionary speichern
        match_info = {
            "match_id": match_id,
            "date_time_text": date_time_text,
            "date_time": dt,
            "youth_team": youth_team,
            "home_club": home_club,
            "guest_club": guest_club,
            "venue": venue
        }

        matches.append(match_info)

        #iCal
        # Titel und UID
        title = f"{home_club} - {guest_club}"
        if youth_team:
            title = f"[{youth_team}] {title}"

        # MATCH_ID
        # Setze die uid des Termins in iCal auf die match_id
        # Dadurch kann z.B. google Kalender einen bestehenden Termin zuordnen und verschieben
        if match_id:
            uid = f"match_id_{match_id}"
            #uid = hashlib.md5(f"fussball.de-{match_id}".encode()).hexdigest()
        else:
            uid = hashlib.md5(f"{home_club}_{guest_club}".encode()).hexdigest()

        # Event erstellen
        event = Event()
        event.uid = uid
        event.name = title         
        event.begin = dt
        event.end = dt + timedelta(hours=2)
        event.location = venue
        desc_lines = [f"Liga: {youth_team}", f"Heim: {home_club}", f"Auswärts: {guest_club}"]
        if venue:
            desc_lines.append(f"Ort: {venue}")
        event.description = "\n".join(desc_lines)
        #event.description += f"\nGenerated: {datetime.now()}" #for debugging only, use datetime so that ical-files is changed 

        calendar.events.add(event)
        events += 1

# Ergebnis anzeigen
if VERBOSE:
    print()
    print("++++++++++++++++")
    for m in matches:
        print(m)
    print("++++++++++++++++")

# -------------------------------
# ICS-Datei speichern
# -------------------------------
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.writelines(calendar.serialize_iter())

print()
print(f"{events} Spiele gefunden")
print("FERTIG")
print(f"# iCal Datei erstellt: {OUTPUT}")

# -------------------------------
# PDF-Ausgabe erstellen
# -------------------------------
OUTPUT_PDF = "alle_spiele.pdf"

doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4)
styles = getSampleStyleSheet()
elements = []

# Überschrift
elements.append(Paragraph("Vereins-Spielplan", styles['Title']))
elements.append(Spacer(1, 12))

# Eigene Styles
bold_style = ParagraphStyle(
    'bold', 
    parent=styles['Normal'], 
    fontName='Helvetica-Bold', 
    fontSize=11, 
    spaceAfter=2
)
normal_style = ParagraphStyle(
    'normal', 
    parent=styles['Normal'], 
    fontName='Helvetica', 
    fontSize=10, 
    spaceAfter=2
)
spiel_style = ParagraphStyle(
    'spiel', 
    parent=styles['Normal'], 
    fontName='Helvetica-Bold', 
    fontSize=14,   # nur für diese Zeile größer
    spaceAfter=8
)

for m in matches:
    # Datum + Uhrzeit
    if m["date_time"]:
        datum_uhrzeit = m["date_time"].strftime("%d.%m.%Y %H:%M")
    else:
        datum_uhrzeit = "unbekannt"
    elements.append(Paragraph(datum_uhrzeit, bold_style))

    # Jugend/Liga
    liga_text = m["youth_team"] if m["youth_team"] else "-"
    elements.append(Paragraph(liga_text, normal_style))

    # Heimteam gegen Gastteam
    spiel_text = f"{m['home_club']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp : &nbsp;&nbsp;&nbsp;&nbsp;&nbsp {m['guest_club']}"
    elements.append(Paragraph(spiel_text, spiel_style))

    # Spielort
    if "spielfrei" in m["guest_club"]:
        ort_text = f"Spielort: -"
    else:
        ort_text = m["venue"] if m["venue"] else "-"
        ort_text = f"Spielort: {ort_text}"
    elements.append(Paragraph(ort_text, normal_style))

    # Abstand zwischen Spielen 
    elements.append(Spacer(1, 25))  # ca. 25 Punkte Abstand

# PDF bauen
doc.build(elements)
print(f"# PDF erstellt: {OUTPUT_PDF}")
