"""Fabrique l'image de l'écran Kindle (Paperwhite 3 : 1072 x 1448, niveaux de gris)."""
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from citations import citation_du_jour
from saints import fete

# ---------- Réglages ----------
LAT, LON = 44.754, -0.487          # Quinsac
TZ = ZoneInfo("Europe/Paris")
# Poubelle : à sortir le lundi soir, en alternance une semaine sur deux.
TRASH_DAY = "lundi"
TRASH_REF = date(2026, 11, 23)          # un lundi où c'était la poubelle jaune
TRASH_CYCLE = ["jaune", "grise"]
# Anniversaires "Prénom=JJ/MM; Prénom=JJ/MM". Réglable dans GitHub (secret BIRTHDAYS).
BIRTHDAYS = os.environ.get("BIRTHDAYS", "")
OUT = os.environ.get("OUT", "output/dashboard.png")
MOCK = "--mock" in sys.argv
# Affichage du matin (Tempo centré + citation) pour les images fabriquées avant cette heure.
# La Kindle les affiche à 7 h 10 ; celle de 12 h 10 est toujours en affichage complet.
HEURE_FIN_MATIN = 11

MOIS_COURT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


def get_json(url, essais=3):
    # Réessaie automatiquement si un site ne répond pas du premier coup
    import time
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kindle-dashboard (usage familial)"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            print(f"Essai {i + 1}/{essais} échoué pour {url.split('?')[0]} : {e}")
            if i == essais - 1:
                raise
            time.sleep(10)


# ---------- Données ----------
def tempo():
    code = {1: "bleu", 2: "blanc", 3: "rouge"}
    out = {}
    for k in ("today", "tomorrow"):
        try:
            out[k] = code.get(get_json(f"https://www.api-couleur-tempo.fr/api/jourTempo/{k}").get("codeJour"), None)
        except Exception as e:
            print("Tempo", k, e)
            out[k] = None
    return out


METEO_BRUT = None   # dernière météo reçue, rangée dans l'image pour servir de secours


def meteo_secours():
    """Relit la météo rangée dans l'image publiée précédemment (si le site météo ne répond pas)."""
    import io
    from PIL import Image
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        return None
    try:
        req = urllib.request.Request(f"https://raw.githubusercontent.com/{repo}/output/dashboard.png",
                                     headers={"User-Agent": "kindle-dashboard"})
        with urllib.request.urlopen(req, timeout=30) as r:
            texte = Image.open(io.BytesIO(r.read())).text.get("meteo")
        return json.loads(texte) if texte else None
    except Exception as e:
        print("Météo de secours indisponible :", e)
        return None


def meteo(today):
    global METEO_BRUT
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={LAT}&longitude={LON}&current=temperature_2m,weather_code"
           "&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max"
           "&timezone=Europe%2FParis&forecast_days=4")
    secours = False
    try:
        m = get_json(url)
        METEO_BRUT = m
    except Exception as e:
        print("Site météo injoignable, utilisation de la dernière météo connue :", e)
        m = meteo_secours()
        if not m:
            raise
        METEO_BRUT = m
        secours = True
    # Aligne les prévisions sur aujourd'hui (utile si la météo de secours date d'hier)
    jours = m["daily"]["time"]
    i = jours.index(today.isoformat())
    m = {"current": m["current"], "daily": {k: v[i:] for k, v in m["daily"].items()}}
    if len(m["daily"]["time"]) < 3:
        raise RuntimeError("Météo de secours trop ancienne")
    if secours:   # pas de température "actuelle" fiable : on affiche la prévision du jour
        m["current"] = {"temperature_2m": m["daily"]["temperature_2m_max"][0], "weather_code": m["daily"]["weather_code"][0]}
        m["secours"] = True
    return m


def air():
    try:
        v = get_json("https://air-quality-api.open-meteo.com/v1/air-quality"
                     f"?latitude={LAT}&longitude={LON}&current=european_aqi&timezone=Europe%2FParis")["current"]["european_aqi"]
    except Exception as e:
        print("Air", e)
        return None
    for seuil, label in ((20, "Bon"), (40, "Moyen"), (60, "Dégradé"), (80, "Mauvais"), (100, "Très mauvais")):
        if v <= seuil:
            return label
    return "Extrêmement mauvais"


def vacances(today):
    try:
        url = ("https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records"
               "?where=" + urllib.parse.quote(f'location="Bordeaux" and end_date>="{today.isoformat()}"')
               + "&order_by=start_date&limit=10")
        recs = get_json(url)["results"]
    except Exception as e:
        print("Vacances", e)
        return None
    for r in recs:
        if r.get("population") == "Enseignants":
            continue
        start = datetime.fromisoformat(r["start_date"]).astimezone(TZ).date()
        end = datetime.fromisoformat(r["end_date"]).astimezone(TZ).date()
        nom = r.get("description", "Vacances").replace("Vacances d'", "").replace("Vacances de ", "").replace("Vacances ", "")
        if start <= today < end:
            return f"<strong>Vacances</strong> jusqu'au {court(end)}"
        n = (start - today).days
        if 0 < n <= 30:
            return f"<strong>{r.get('description', 'Vacances')}</strong> " + ("demain" if n == 1 else f"dans {n} jours")
        return None
    return None


def anniversaire(today):
    best = None
    for item in BIRTHDAYS.replace("\n", ";").split(";"):
        if "=" not in item:
            continue
        nom, jm = [x.strip() for x in item.split("=", 1)]
        try:
            j, m = [int(x) for x in jm.split("/")[:2]]
            d = date(today.year, m, j)
        except ValueError:
            continue
        if d < today:
            d = date(today.year + 1, m, j)
        n = (d - today).days
        if n <= 7 and (best is None or n < best[0]):
            best = (n, nom, d)
    if not best:
        return None
    n, nom, d = best
    quand = "aujourd'hui" if n == 0 else "demain" if n == 1 else JOURS[d.weekday()]
    return f"Anniv. <strong>{nom}</strong> {quand}"


def poubelle(now):
    today = now.date()
    if JOURS[today.weekday()] != TRASH_DAY:
        return None
    semaines = (today - TRASH_REF).days // 7
    return TRASH_CYCLE[semaines % len(TRASH_CYCLE)]


def lune(now):
    ref = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    p = ((now.astimezone(timezone.utc) - ref).total_seconds() / 86400 / 29.530588853) % 1
    noms = ["Nouvelle lune", "Lune croissante", "Premier quartier", "Lune croissante",
            "Pleine lune", "Lune décroissante", "Dernier quartier", "Lune décroissante"]
    return p, noms[int((p * 8) + 0.5) % 8]


# ---------- Icônes ----------
def wtype(code):
    if code in (0, 1):
        return "sun"
    if code == 2:
        return "partly"
    if code == 3:
        return "cloud"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    return "rain"


WLABEL = {0: "Ensoleillé", 1: "Plutôt ensoleillé", 2: "Éclaircies", 3: "Couvert", 45: "Brouillard", 48: "Brouillard givrant",
          51: "Bruine", 53: "Bruine", 55: "Bruine", 56: "Bruine verglaçante", 57: "Bruine verglaçante",
          61: "Pluie faible", 63: "Pluie", 65: "Forte pluie", 66: "Pluie verglaçante", 67: "Pluie verglaçante",
          71: "Neige faible", 73: "Neige", 75: "Forte neige", 77: "Grains de neige", 80: "Averses", 81: "Averses",
          82: "Fortes averses", 85: "Averses de neige", 86: "Averses de neige", 95: "Orages", 96: "Orages, grêle", 99: "Orages, grêle"}

CLOUD = '<path d="M17.5 19H8a5 5 0 1 1 .9-9.9A6 6 0 0 1 20 12a3.5 3.5 0 0 1-2.5 7z"/>'
ICON = {
    "sun": '<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
    "partly": '<circle cx="8" cy="8" r="3"/><path d="M8 2v1.5M2 8h1.5M3.8 3.8l1 1M12.2 3.8l-1 1"/><path d="M18 20H9a4 4 0 1 1 1-7.9A5 5 0 0 1 19.5 14a3 3 0 0 1-1.5 6z"/>',
    "cloud": CLOUD,
    "fog": '<path d="M17.5 14H8a5 5 0 1 1 .9-9.9A6 6 0 0 1 20 7a3.5 3.5 0 0 1-2.5 7z"/><path d="M3 18h18M5 21h14"/>',
    "rain": '<path d="M17.5 17H8a5 5 0 1 1 .9-9.9A6 6 0 0 1 20 10a3.5 3.5 0 0 1-2.5 7z"/><path d="M9 19l-1 3M13 19l-1 3M17 19l-1 3"/>',
    "snow": '<path d="M17.5 17H8a5 5 0 1 1 .9-9.9A6 6 0 0 1 20 10a3.5 3.5 0 0 1-2.5 7z"/><path d="M8 20h.01M12 21h.01M16 20h.01M10 23h.01M14 23h.01"/>',
    "storm": '<path d="M17.5 16H8a5 5 0 1 1 .9-9.9A6 6 0 0 1 20 9a3.5 3.5 0 0 1-2.5 7z"/><path d="M12 16l-2 4h4l-2 4"/>',
}


def icon(t, size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICON[t]}</svg>')


def moon_svg(p, size=40):
    r, c = 10, 12
    k = math.cos(2 * math.pi * p)          # 1 = nouvelle, -1 = pleine
    rx = abs(k) * r
    if p < 0.5:   # croissante : partie éclairée à droite
        outer = f"M{c},{c-r} A{r},{r} 0 0 1 {c},{c+r}"
        inner = f"A{rx:.2f},{r} 0 0 {1 if k < 0 else 0} {c},{c-r}"
    else:         # décroissante : partie éclairée à gauche
        outer = f"M{c},{c-r} A{r},{r} 0 0 0 {c},{c+r}"
        inner = f"A{rx:.2f},{r} 0 0 {0 if k < 0 else 1} {c},{c-r}"
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24"><circle cx="{c}" cy="{c}" r="{r}" fill="#111"/>'
            f'<path d="{outer} {inner} Z" fill="#ffffff"/><circle cx="{c}" cy="{c}" r="{r}" fill="none" stroke="#111" stroke-width="1.6"/></svg>')


def court(d):
    return f"{JOURS[d.weekday()][:3]}. {d.day} {MOIS_COURT[d.month-1]}"


# ---------- Mise en page ----------
TEMPO_BOX = {
    "rouge": ('background:#111;color:#ffffff;padding:18px 22px', '', 'ROUGE'),
    "blanc": ('border:3px solid #111;background:repeating-linear-gradient(135deg,#ffffff 0 10px,#c4c4bf 10px 14px);padding:15px 19px',
              'background:#ffffff;align-self:flex-start;padding:0 6px', 'BLANC'),
    "bleu": ('border:3px solid #111;padding:15px 19px', '', 'BLEU'),
    None: ('border:3px dashed #111;padding:15px 19px', '', '—'),
}


def tempo_box(titre, couleur, attente=False, grand=False):
    box, lab, mot = TEMPO_BOX[couleur]
    taille_mot = 84 if grand else 64
    centre = ""
    if grand:
        lab = lab.replace("align-self:flex-start", "align-self:center")
        centre = ";align-items:center;text-align:center"
    if couleur is None and attente:
        mot = '<span style="font-size:34px">Connu vers 11 h</span>'
    return (f'<div style="{box};display:flex;flex-direction:column;gap:6px{centre}">'
            f'<div style="font-size:21px;font-weight:500;{lab}">{titre}</div>'
            f'<div style="font-family:Literata,Georgia,serif;font-size:{taille_mot}px;font-weight:700;line-height:1;{lab}">{mot}</div></div>')


def build_html(now, d):
    today = now.date()
    m = d["meteo"]
    daily = m["daily"]
    cur = m["current"]
    sr = datetime.fromisoformat(daily["sunrise"][0]).strftime("%H:%M")
    ss = datetime.fromisoformat(daily["sunset"][0]).strftime("%H:%M")
    p, lune_nom = lune(now)

    jours_html = []
    for i in (1, 2):
        dd = today + timedelta(days=i)
        nom = "Demain" if i == 1 else JOURS[dd.weekday()].capitalize()
        sep = "padding-left:24px;border-left:2px solid #111;" if i == 2 else ""
        pluie = daily["precipitation_probability_max"][i]
        pluie_txt = f'<div style="font-size:20px;font-weight:500">Pluie {pluie} %</div>' if pluie is not None and pluie >= 30 else ""
        jours_html.append(
            f'<div style="display:flex;align-items:center;gap:16px;{sep}">{icon(wtype(daily["weather_code"][i]), 76)}'
            f'<div style="display:flex;flex-direction:column;gap:2px"><div style="font-size:26px;font-weight:700">{nom}</div>'
            f'<div style="font-size:38px;font-weight:600;line-height:1.15">{round(daily["temperature_2m_min"][i])}° / {round(daily["temperature_2m_max"][i])}°</div>{pluie_txt}</div></div>')

    poub = ('<div style="display:flex;align-items:center;gap:10px;font-size:22px;font-weight:600">'
            '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/></svg><span>Ce soir : sortir la poubelle ' + d["poubelle"] + '</span></div>') if d["poubelle"] else ""

    bas = [x for x in (d["vacances"], d["anniv"]) if x]
    bas_html = ""
    if bas:
        bas_html = ('<div style="height:2px;background:#111"></div>'
                    '<div style="display:flex;justify-content:space-between;align-items:baseline;font-size:23px;font-weight:500">'
                    + "".join(f"<div>{x}</div>" for x in bas) + "</div>")

    t = d["tempo"]
    if now.hour < HEURE_FIN_MATIN or "--matin" in sys.argv:
        texte, auteur = citation_du_jour(today)
        taille = 46 if len(texte) <= 70 else 40 if len(texte) <= 110 else 34
        milieu = f"""<div style="display:flex;justify-content:center">
 <div style="width:62%;display:grid">{tempo_box("Tempo aujourd'hui", t["today"], grand=True)}</div>
</div>

<div style="height:2px;background:#111"></div>

<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:18px;padding:10px 20px;text-align:center">
 <div style="font-family:Literata,Georgia,serif;font-style:italic;font-size:{taille}px;line-height:1.3">« {texte} »</div>
 <div style="font-size:22px;font-weight:600;color:#222">{auteur}</div>
</div>
"""
    else:
        milieu = f"""<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px">
 {tempo_box("Tempo aujourd'hui", t["today"])}
 {tempo_box("Tempo demain", t["tomorrow"], attente=now.hour < 12)}
</div>

<div style="height:2px;background:#111"></div>

<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px">{"".join(jours_html)}</div>

<div style="height:2px;background:#111"></div>

<div style="display:grid;grid-template-columns:minmax(0,0.95fr) minmax(0,1.45fr) minmax(0,0.8fr)">
 <div style="display:flex;flex-direction:column;gap:4px;padding-right:16px">
  <div style="font-size:18px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase">Soleil</div>
  <div style="font-size:24px;font-weight:600">Lever {sr}</div><div style="font-size:24px;font-weight:600">Coucher {ss}</div>
 </div>
 <div style="display:flex;flex-direction:column;gap:4px;padding:0 16px;border-left:2px solid #111">
  <div style="font-size:18px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase">Lune</div>
  <div style="display:flex;align-items:center;gap:10px">{moon_svg(p, 52)}<div style="font-size:22px;font-weight:600;line-height:1.2;white-space:nowrap">{lune_nom}</div></div>
 </div>
 <div style="display:flex;flex-direction:column;gap:4px;padding-left:16px;border-left:2px solid #111">
  <div style="font-size:18px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase">Air</div>
  <div style="font-family:Literata,Georgia,serif;font-size:{34 if (d["air"] or "—") in ("Bon", "Moyen", "—") else 24}px;font-weight:700;line-height:1.2">{d["air"] or "—"}</div>
 </div>
</div>
"""

    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600;7..72,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>body{{margin:0;background:#ffffff}}</style></head><body>
<div style="width:758px;height:1024px;box-sizing:border-box;background:#ffffff;color:#111;font-family:Inter,sans-serif;padding:40px 48px 22px;display:flex;flex-direction:column;justify-content:space-between;gap:20px">

<div style="display:flex;flex-direction:column;gap:14px">
 <div style="display:flex;justify-content:space-between;align-items:center">
  <div style="display:flex;align-items:center;gap:22px">
   <div style="font-family:Literata,Georgia,serif;font-size:150px;font-weight:700;line-height:.85;letter-spacing:-3px">{today.day}</div>
   <div style="display:flex;flex-direction:column;gap:6px">
    <div style="font-family:Literata,Georgia,serif;font-size:46px;font-weight:600;line-height:1">{JOURS[today.weekday()].capitalize()}</div>
    <div style="font-family:Literata,Georgia,serif;font-size:46px;font-weight:600;line-height:1">{MOIS[today.month-1].capitalize()}</div>
   </div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">
   <div style="display:flex;align-items:center;gap:10px">{icon(wtype(cur["weather_code"]), 60)}
    <div style="font-family:Literata,Georgia,serif;font-size:72px;font-weight:700;line-height:1">{round(cur["temperature_2m"])}°</div></div>
   <div style="font-size:22px;font-weight:500;text-align:right">{"Prévision" if m.get("secours") else WLABEL.get(cur["weather_code"], "")} · {round(daily["temperature_2m_min"][0])}° / {round(daily["temperature_2m_max"][0])}°</div>
  </div>
 </div>
 <div style="font-family:Literata,Georgia,serif;font-size:28px;font-weight:600">{fete(today)}</div>
 {poub}
</div>

<div style="height:3px;background:#111"></div>

{milieu}

{bas_html}

<div style="display:flex;justify-content:flex-end;font-size:13px;color:#444">
 <span>Mis à jour {court(today)} à {now.strftime("%H:%M")}</span>
</div>
</div></body></html>"""


def collect(now):
    today = now.date()
    if MOCK:
        return {
            "meteo": {"current": {"temperature_2m": 9.2, "weather_code": 80},
                      "daily": {"weather_code": [80, 2, 0], "temperature_2m_max": [12, 13, 14], "temperature_2m_min": [6, 4, 3],
                                "sunrise": ["2026-11-25T08:20", "", ""], "sunset": ["2026-11-25T17:20", "", ""],
                                "precipitation_probability_max": [80, 40, 5]}},
            "tempo": {"today": "rouge", "tomorrow": None}, "air": "Bon", "poubelle": "jaune",
            "vacances": "<strong>Vacances de Noël</strong> dans 24 jours", "anniv": "Anniv. <strong>Mamie</strong> samedi",
        }
    return {"meteo": meteo(today), "tempo": tempo(), "air": air(), "poubelle": poubelle(now),
            "vacances": vacances(today), "anniv": anniversaire(today)}


def main():
    from PIL import Image
    from playwright.sync_api import sync_playwright

    now = datetime.now(TZ)
    html = build_html(now, collect(now))
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 758, "height": 1024}, device_scale_factor=1072 / 758)
        try:
            page.set_content(html, wait_until="networkidle", timeout=60000)
        except Exception as e:  # polices lentes : on continue avec ce qui est chargé
            print("Chargement de la page incomplet :", e)
        page.evaluate("document.fonts.ready")
        page.screenshot(path=OUT)
        b.close()
    from PIL.PngImagePlugin import PngInfo
    info = PngInfo()
    if METEO_BRUT:
        info.add_text("meteo", json.dumps(METEO_BRUT))
    Image.open(OUT).convert("L").resize((1072, 1448), Image.LANCZOS).save(OUT, optimize=True, pnginfo=info)
    print("Image écrite :", OUT)


if __name__ == "__main__":
    main()
