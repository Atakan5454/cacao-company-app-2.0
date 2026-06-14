# -*- coding: utf-8 -*-
"""
Cacao Company - Digitale klantomgeving (MVP)
=============================================
Een volledig offline, lokaal draaiende web-applicatie voor een premium
chocoladeproducent. Gebouwd met Flask. Alle data wordt opgeslagen in
JSON-bestanden in de map ./data (deze map wordt automatisch aangemaakt).

Start de app met:   python main.py
Open daarna in je browser:   http://127.0.0.1:5000

Geen externe API's, geen cloud, geen database. Alleen Python + Flask.
"""

import os
import json
import hashlib
import secrets
import datetime
from flask import Flask, request, session, jsonify, Response

# ---------------------------------------------------------------------------
# CONFIGURATIE & BESTANDSPADEN
# ---------------------------------------------------------------------------

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")

# Pad naar elk JSON-databestand. De bestanden worden automatisch aangemaakt.
FILES = {
    "accounts": os.path.join(DATA_DIR, "accounts.json"),
    "products": os.path.join(DATA_DIR, "products.json"),
    "registered": os.path.join(DATA_DIR, "registered.json"),
    "orders": os.path.join(DATA_DIR, "orders.json"),
    "complaints": os.path.join(DATA_DIR, "complaints.json"),
    "notifications": os.path.join(DATA_DIR, "notifications.json"),
    "preferences": os.path.join(DATA_DIR, "preferences.json"),
}

app = Flask(__name__)
# Vaste secret key zodat sessies blijven werken na herstart (alleen lokaal gebruik).
app.secret_key = "cacao-company-local-demo-secret-key"


# ---------------------------------------------------------------------------
# OPSLAG HELPERS (JSON) - met foutafhandeling om crashes te voorkomen
# ---------------------------------------------------------------------------

def ensure_data_dir():
    """Maak de data-map aan als die nog niet bestaat."""
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_json(key, default):
    """Laad een JSON-bestand. Bestaat het niet of is het corrupt, dan
    wordt de meegegeven standaardwaarde teruggegeven (en weggeschreven)."""
    ensure_data_dir()
    path = FILES[key]
    if not os.path.isfile(path):
        save_json(key, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupt of onleesbaar bestand: herstel met standaardwaarde.
        save_json(key, default)
        return default


def save_json(key, data):
    """Schrijf data naar het bijbehorende JSON-bestand."""
    ensure_data_dir()
    try:
        with open(FILES[key], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        # Bij schrijffouten niet crashen; de app blijft bruikbaar.
        pass


def hash_password(password):
    """Eenvoudige, lokale wachtwoord-hashing (geen platte opslag)."""
    return hashlib.sha256(("cacao-salt-" + password).encode("utf-8")).hexdigest()


def today():
    return datetime.date.today()


def date_str(d):
    return d.strftime("%d-%m-%Y")


def now_iso():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------------------------------------------------------------------------
# STANDAARD / SEED DATA
# ---------------------------------------------------------------------------

def seed_products():
    """Het volledige assortiment premium chocoladeproducten."""
    return [
        {
            "code": "CACAO-001",
            "naam": "Cacao Company Noir 72%",
            "prijs": 4.95,
            "categorie": "Puur",
            "emoji": "\U0001F36B",
            "ingredienten": "Cacaomassa, rietsuiker, cacaoboter, vanille",
            "allergenen": "Kan sporen van noten en melk bevatten",
            "herkomst": "Ghana (West-Afrika)",
            "houdbaarheid": "12 maanden",
            "beschrijving": "Intense pure chocolade met 72% cacao. Diepe tonen van geroosterde cacao en een fluweelzachte afdronk.",
        },
        {
            "code": "CACAO-002",
            "naam": "Madagascar Vanilla Milk",
            "prijs": 4.50,
            "categorie": "Melk",
            "emoji": "\U0001F36B",
            "ingredienten": "Volle melkpoeder, rietsuiker, cacaoboter, cacaomassa, Bourbon-vanille",
            "allergenen": "Bevat melk. Kan sporen van noten bevatten",
            "herkomst": "Madagascar",
            "houdbaarheid": "10 maanden",
            "beschrijving": "Romige melkchocolade verfijnd met echte Bourbon-vanille uit Madagascar.",
        },
        {
            "code": "CACAO-003",
            "naam": "Ecuador Single Origin 85%",
            "prijs": 5.75,
            "categorie": "Puur",
            "emoji": "\U0001F36B",
            "ingredienten": "Cacaomassa, cacaoboter, rietsuiker",
            "allergenen": "Kan sporen van noten en melk bevatten",
            "herkomst": "Ecuador (Arriba Nacional)",
            "houdbaarheid": "14 maanden",
            "beschrijving": "Single origin reep met krachtige 85% cacao. Florale tonen en een lange, rijke afdronk.",
        },
        {
            "code": "CACAO-004",
            "naam": "Sea Salt Caramel Tablet",
            "prijs": 5.25,
            "categorie": "Caramel",
            "emoji": "\U0001F9C2",
            "ingredienten": "Melkchocolade, karamelvulling, zeezout, cacaoboter, rietsuiker",
            "allergenen": "Bevat melk. Kan sporen van noten bevatten",
            "herkomst": "Belgie (productie) / Ghana (cacao)",
            "houdbaarheid": "9 maanden",
            "beschrijving": "Zachte karamel met een vleugje Bretons zeezout in romige melkchocolade.",
        },
        {
            "code": "CACAO-005",
            "naam": "Ruby Raspberry Crunch",
            "prijs": 5.50,
            "categorie": "Ruby",
            "emoji": "\U0001F353",
            "ingredienten": "Ruby cacao, rietsuiker, cacaoboter, melkpoeder, gevriesdroogde framboos",
            "allergenen": "Bevat melk. Kan sporen van noten bevatten",
            "herkomst": "Ivoorkust",
            "houdbaarheid": "8 maanden",
            "beschrijving": "Natuurlijke roze ruby-chocolade met fris-fruitige framboos en een knapperige crunch.",
        },
        {
            "code": "CACAO-006",
            "naam": "Vegan Oat Mylk Chocolate",
            "prijs": 5.95,
            "categorie": "Vegan",
            "emoji": "\U0001F33F",
            "ingredienten": "Cacaomassa, haverdrankpoeder, kokosbloesemsuiker, cacaoboter",
            "allergenen": "Bevat haver (gluten). Kan sporen van noten bevatten",
            "herkomst": "Peru",
            "houdbaarheid": "11 maanden",
            "beschrijving": "100% plantaardige 'melk'chocolade op basis van haver. Romig, duurzaam en zuivelvrij.",
        },
        {
            "code": "CACAO-007",
            "naam": "Hazelnut Praline Gold",
            "prijs": 6.50,
            "categorie": "Praline",
            "emoji": "\U0001F330",
            "ingredienten": "Melkchocolade, hazelnootpraline, cacaoboter, rietsuiker",
            "allergenen": "Bevat melk en hazelnoten",
            "herkomst": "Italie (Piemonte hazelnoten)",
            "houdbaarheid": "7 maanden",
            "beschrijving": "Luxe praline met geroosterde Piemonte-hazelnoten, afgewerkt met goudglans.",
        },
        {
            "code": "CACAO-008",
            "naam": "White Chocolate Pistachio",
            "prijs": 6.25,
            "categorie": "Wit",
            "emoji": "\U0001F95C",
            "ingredienten": "Cacaoboter, melkpoeder, rietsuiker, pistache",
            "allergenen": "Bevat melk en pistachenoten",
            "herkomst": "Turkije (pistache) / Belgie (productie)",
            "houdbaarheid": "8 maanden",
            "beschrijving": "Zachte witte chocolade met geroosterde pistache. Subtiel zoet en romig.",
        },
    ]


def seed_if_empty():
    """Vul de databestanden bij de eerste start met realistische demodata
    zodat alle functionaliteiten direct zichtbaar zijn tijdens een demo."""

    # 1. Producten (assortiment)
    products = load_json("products", [])
    if not products:
        products = seed_products()
        save_json("products", products)

    # 2. Demo-account
    accounts = load_json("accounts", {})
    if "demo@cacao.nl" not in accounts:
        accounts["demo@cacao.nl"] = {
            "email": "demo@cacao.nl",
            "naam": "Sophie de Vries",
            "wachtwoord": hash_password("demo123"),
            "allergieen": ["Noten"],
            "favorieten": ["Puur", "Caramel"],
        }
        save_json("accounts", accounts)

    # 3. Voorkeuren (notificatie-instellingen per gebruiker)
    preferences = load_json("preferences", {})
    if "demo@cacao.nl" not in preferences:
        preferences["demo@cacao.nl"] = {
            "notif_bestelling": True,
            "notif_klacht": True,
            "notif_houdbaarheid": True,
            "notif_aanbeveling": True,
        }
        save_json("preferences", preferences)

    # 4. Geregistreerde producten (persoonlijke collectie) met houdbaarheidsdatum
    registered = load_json("registered", {})
    if "demo@cacao.nl" not in registered:
        t = today()
        registered["demo@cacao.nl"] = [
            {"code": "CACAO-001", "geregistreerd": date_str(t - datetime.timedelta(days=20)),
             "verloopt": date_str(t + datetime.timedelta(days=120))},
            {"code": "CACAO-004", "geregistreerd": date_str(t - datetime.timedelta(days=60)),
             "verloopt": date_str(t + datetime.timedelta(days=10))},   # bijna verlopen
            {"code": "CACAO-005", "geregistreerd": date_str(t - datetime.timedelta(days=70)),
             "verloopt": date_str(t + datetime.timedelta(days=4))},    # bijna verlopen
        ]
        save_json("registered", registered)

    # 5. Bestellingen
    orders = load_json("orders", [])
    if not any(o.get("email") == "demo@cacao.nl" for o in orders):
        t = today()
        orders.append({
            "id": "ORD-1001",
            "email": "demo@cacao.nl",
            "datum": date_str(t - datetime.timedelta(days=12)),
            "items": [
                {"code": "CACAO-003", "naam": "Ecuador Single Origin 85%", "aantal": 2, "prijs": 5.75},
                {"code": "CACAO-007", "naam": "Hazelnut Praline Gold", "aantal": 1, "prijs": 6.50},
            ],
            "totaal": 18.00,
            "adres": "Cacaostraat 12, 1011 AB Amsterdam",
            "status": "Bezorgd",
        })
        save_json("orders", orders)

    # 6. Klachten
    complaints = load_json("complaints", [])
    if not any(c.get("email") == "demo@cacao.nl" for c in complaints):
        complaints.append({
            "id": "KL-2001",
            "email": "demo@cacao.nl",
            "datum": date_str(today() - datetime.timedelta(days=5)),
            "product": "Sea Salt Caramel Tablet",
            "categorie": "Verpakking",
            "omschrijving": "De verpakking was bij ontvangst licht beschadigd.",
            "foto": "",
            "status": "In behandeling",
        })
        save_json("complaints", complaints)

    # 7. Notificaties
    notifications = load_json("notifications", [])
    if not any(n.get("email") == "demo@cacao.nl" for n in notifications):
        notifications.extend([
            {"id": "N1", "email": "demo@cacao.nl", "tijd": now_iso(), "gelezen": False,
             "type": "houdbaarheid", "titel": "Product bijna verlopen",
             "tekst": "Je Ruby Raspberry Crunch verloopt binnenkort. Geniet er snel van!"},
            {"id": "N2", "email": "demo@cacao.nl", "tijd": now_iso(), "gelezen": False,
             "type": "aanbeveling", "titel": "Nieuw voor jou",
             "tekst": "Op basis van je voorkeuren raden we de Ecuador Single Origin 85% aan."},
            {"id": "N3", "email": "demo@cacao.nl", "tijd": now_iso(), "gelezen": True,
             "type": "klacht", "titel": "Klacht in behandeling",
             "tekst": "Je klacht KL-2001 wordt momenteel behandeld door onze klantenservice."},
        ])
        save_json("notifications", notifications)


# ---------------------------------------------------------------------------
# BUSINESS LOGICA
# ---------------------------------------------------------------------------

def get_product(code):
    """Zoek een product op code."""
    for p in load_json("products", []):
        if p["code"] == code:
            return p
    return None


def add_notification(email, ntype, titel, tekst):
    """Voeg een notificatie toe als de gebruiker dit type aan heeft staan."""
    prefs = load_json("preferences", {}).get(email, {})
    pref_map = {
        "bestelling": "notif_bestelling",
        "klacht": "notif_klacht",
        "houdbaarheid": "notif_houdbaarheid",
        "aanbeveling": "notif_aanbeveling",
    }
    if pref_map.get(ntype) and prefs.get(pref_map[ntype]) is False:
        return  # gebruiker heeft dit notificatietype uitgezet
    notifications = load_json("notifications", [])
    notifications.insert(0, {
        "id": "N" + secrets.token_hex(4),
        "email": email,
        "tijd": now_iso(),
        "gelezen": False,
        "type": ntype,
        "titel": titel,
        "tekst": tekst,
    })
    save_json("notifications", notifications)


def get_recommendations(email):
    """Gepersonaliseerde aanbevelingen op basis van favorieten, eerdere
    bestellingen en geregistreerde producten. Verandert dynamisch mee."""
    accounts = load_json("accounts", {})
    acct = accounts.get(email, {})
    favorieten = set(acct.get("favorieten", []))

    # Verzamel categorieen uit bestellingen en collectie.
    besteld_codes = set()
    for o in load_json("orders", []):
        if o.get("email") == email:
            for it in o.get("items", []):
                besteld_codes.add(it["code"])

    geregistreerd_codes = set(
        r["code"] for r in load_json("registered", {}).get(email, [])
    )

    cat_gewicht = {}
    for c in favorieten:
        cat_gewicht[c] = cat_gewicht.get(c, 0) + 3
    for code in besteld_codes:
        p = get_product(code)
        if p:
            cat_gewicht[p["categorie"]] = cat_gewicht.get(p["categorie"], 0) + 2
    for code in geregistreerd_codes:
        p = get_product(code)
        if p:
            cat_gewicht[p["categorie"]] = cat_gewicht.get(p["categorie"], 0) + 1

    al_bekend = besteld_codes | geregistreerd_codes
    scored = []
    for p in load_json("products", []):
        score = cat_gewicht.get(p["categorie"], 0)
        if p["code"] in al_bekend:
            score -= 8  # liever iets nieuws aanraden dat de klant nog niet heeft
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:4]]


def days_until(date_string):
    """Aantal dagen tot een datum in formaat dd-mm-YYYY (negatief = verlopen)."""
    try:
        d = datetime.datetime.strptime(date_string, "%d-%m-%Y").date()
        return (d - today()).days
    except (ValueError, TypeError):
        return 9999


def current_user():
    return session.get("user")


# ---------------------------------------------------------------------------
# FAQ / CHATBOT ENGINE (keyword matching, geen externe AI)
# ---------------------------------------------------------------------------

FAQ = [
    (["hallo", "hoi", "hey", "goedemorgen", "goedemiddag"],
     "Hallo! \U0001F44B Ik ben de Cacao Company assistent. Stel gerust een vraag over producten, allergenen, houdbaarheid, bestellingen, klachten of je account."),
    (["allergie", "allergeen", "allergenen", "noten", "gluten", "melk", "lactose", "soja"],
     "Allergeneninformatie staat op elk product. Pure repen kunnen sporen van noten en melk bevatten. Melk-, ruby-, caramel-, praline- en witte chocolade bevatten melk. Vegan Oat Mylk bevat haver (gluten). Hazelnut Praline en White Pistachio bevatten noten. Scan een product of bekijk de details voor de volledige lijst."),
    (["houdbaar", "houdbaarheid", "verloopt", "verlopen", "tht", "vervaldatum", "bewaren"],
     "De houdbaarheid varieert per product (7 tot 14 maanden). Bewaar chocolade koel en droog (15-18 graden), niet in de koelkast. In je collectie zie je welke producten bijna verlopen."),
    (["bestelling", "bestellen", "order", "kopen", "winkelwagen", "afrekenen", "checkout"],
     "Je plaatst een bestelling via de Shop: voeg producten toe aan je winkelwagen, controleer de bestelling en reken af. Je ontvangt direct een bevestiging en een notificatie."),
    (["levering", "bezorging", "verzending", "verzendkosten", "wanneer", "track", "pakket"],
     "Bestellingen worden binnen 2-3 werkdagen bezorgd. Boven de 25 euro is de verzending gratis. Je vindt je bestellingen terug onder Profiel en op het Home-dashboard."),
    (["betaling", "betalen", "ideal", "creditcard", "betaalmethode"],
     "Betalen kan veilig tijdens het afrekenen. In deze demo wordt de betaling gesimuleerd, maar het proces voelt net als een echte checkout."),
    (["klacht", "klagen", "probleem", "kapot", "beschadigd", "retour", "terugsturen"],
     "Een klacht dien je in via Profiel > Klacht indienen. Kies het product, een categorie en een omschrijving. Je kunt de status (Ontvangen, In behandeling, Opgelost) volgen onder je klachtenoverzicht."),
    (["account", "profiel", "wachtwoord", "inloggen", "gegevens", "wijzigen", "email", "naam"],
     "Je accountgegevens beheer je onder Profiel: naam, e-mail, allergieen, favoriete chocoladesoorten en notificatievoorkeuren. Wijzigingen worden direct opgeslagen."),
    (["scan", "scannen", "qr", "code", "registreren", "collectie"],
     "Via de Scan-tab voer je de QR-code van een product in (bijv. CACAO-001). Je ziet dan alle productinformatie en kunt het product toevoegen aan je persoonlijke collectie."),
    (["product", "producten", "assortiment", "reep", "chocolade", "soorten", "smaken"],
     "Ons assortiment bestaat uit 8 premium repen: puur, melk, wit, ruby, vegan, caramel en praline. Bekijk ze in de Shop of scan een reep voor de details."),
    (["herkomst", "cacao", "duurzaam", "duurzaamheid", "bonen", "oorsprong", "fairtrade"],
     "Onze cacao komt onder andere uit Ghana, Ecuador, Madagascar, Peru en Ivoorkust. We werken transparant en duurzaam, met aandacht voor eerlijke handel en herkomst."),
    (["aanbeveling", "aanraden", "tip", "advies", "lekker", "favoriet"],
     "Op je Home-dashboard zie je gepersonaliseerde aanbevelingen op basis van je favorieten, eerdere bestellingen en je collectie. Die passen zich automatisch aan."),
    (["bedankt", "dank", "thanks", "top", "fijn"],
     "Graag gedaan! \U0001F36B Kan ik je nog ergens mee helpen?"),
]

FALLBACK = "Ik kan deze vraag niet beantwoorden. Neem contact op met onze klantenservice."


def chatbot_answer(message):
    """Eenvoudige FAQ-engine: kies het antwoord met de meeste trefwoord-treffers."""
    text = (message or "").lower()
    best_score = 0
    best_answer = FALLBACK
    for keywords, answer in FAQ:
        score = sum(1 for k in keywords if k in text)
        if score > best_score:
            best_score = score
            best_answer = answer
    return best_answer


# ---------------------------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    """Nieuw account aanmaken (lokaal opgeslagen)."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    naam = (data.get("naam") or "").strip()
    wachtwoord = data.get("wachtwoord") or ""

    if not email or "@" not in email or not naam or len(wachtwoord) < 4:
        return jsonify({"ok": False, "fout": "Vul een geldige naam, e-mail en wachtwoord (min. 4 tekens) in."})

    accounts = load_json("accounts", {})
    if email in accounts:
        return jsonify({"ok": False, "fout": "Er bestaat al een account met dit e-mailadres."})

    accounts[email] = {
        "email": email,
        "naam": naam,
        "wachtwoord": hash_password(wachtwoord),
        "allergieen": [],
        "favorieten": [],
    }
    save_json("accounts", accounts)

    prefs = load_json("preferences", {})
    prefs[email] = {"notif_bestelling": True, "notif_klacht": True,
                    "notif_houdbaarheid": True, "notif_aanbeveling": True}
    save_json("preferences", prefs)

    # Lege collectie voor de nieuwe gebruiker.
    registered = load_json("registered", {})
    registered.setdefault(email, [])
    save_json("registered", registered)

    add_notification(email, "aanbeveling", "Welkom bij Cacao Company",
                     "Leuk dat je er bent! Ontdek ons assortiment in de Shop.")
    session["user"] = email
    return jsonify({"ok": True})


@app.route("/api/login", methods=["POST"])
def api_login():
    """Inloggen met e-mail en wachtwoord."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    wachtwoord = data.get("wachtwoord") or ""
    accounts = load_json("accounts", {})
    acct = accounts.get(email)
    if not acct or acct.get("wachtwoord") != hash_password(wachtwoord):
        return jsonify({"ok": False, "fout": "Onjuiste e-mail of wachtwoord."})
    session["user"] = email
    return jsonify({"ok": True})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"ok": True})


@app.route("/api/state", methods=["GET"])
def api_state():
    """Geef alle data terug die de frontend nodig heeft voor de huidige gebruiker."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401

    accounts = load_json("accounts", {})
    acct = accounts.get(email, {})
    products = load_json("products", [])

    # Geregistreerde producten verrijken met productinfo + houdbaarheidsstatus.
    reg_raw = load_json("registered", {}).get(email, [])
    registered = []
    bijna_verlopen = []
    for r in reg_raw:
        p = get_product(r["code"])
        if not p:
            continue
        dagen = days_until(r.get("verloopt", ""))
        item = dict(p)
        item["geregistreerd"] = r.get("geregistreerd", "")
        item["verloopt"] = r.get("verloopt", "")
        item["dagen_resterend"] = dagen
        if dagen < 0:
            item["status"] = "Verlopen"
        elif dagen <= 14:
            item["status"] = "Bijna verlopen"
            bijna_verlopen.append(item)
        else:
            item["status"] = "Goed"
        registered.append(item)

    orders = [o for o in load_json("orders", []) if o.get("email") == email]
    orders_sorted = sorted(orders, key=lambda o: o.get("id", ""), reverse=True)

    complaints = [c for c in load_json("complaints", []) if c.get("email") == email]
    complaints_sorted = sorted(complaints, key=lambda c: c.get("id", ""), reverse=True)

    notifications = [n for n in load_json("notifications", []) if n.get("email") == email]

    prefs = load_json("preferences", {}).get(email, {})

    return jsonify({
        "ok": True,
        "account": {
            "email": acct.get("email", email),
            "naam": acct.get("naam", ""),
            "allergieen": acct.get("allergieen", []),
            "favorieten": acct.get("favorieten", []),
        },
        "preferences": prefs,
        "products": products,
        "registered": registered,
        "bijna_verlopen": bijna_verlopen,
        "orders": orders_sorted,
        "complaints": complaints_sorted,
        "notifications": notifications,
        "recommendations": get_recommendations(email),
        "categorieen": ["Puur", "Melk", "Wit", "Ruby", "Vegan", "Caramel", "Praline"],
    })


@app.route("/api/scan", methods=["POST"])
def api_scan():
    """Verwerk een (handmatig ingevoerde) productcode."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    product = get_product(code)
    if not product:
        return jsonify({"ok": False, "fout": "Ongeldige code. Probeer bijvoorbeeld CACAO-001 t/m CACAO-008."})
    return jsonify({"ok": True, "product": product})


@app.route("/api/register-product", methods=["POST"])
def api_register_product():
    """Voeg een gescand product toe aan de persoonlijke collectie."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    product = get_product(code)
    if not product:
        return jsonify({"ok": False, "fout": "Onbekend product."})

    registered = load_json("registered", {})
    user_list = registered.setdefault(email, [])
    if any(r["code"] == code for r in user_list):
        return jsonify({"ok": False, "fout": "Dit product staat al in je collectie."})

    # Bereken een houdbaarheidsdatum op basis van de productinfo (maanden).
    maanden = 12
    try:
        maanden = int("".join(ch for ch in product["houdbaarheid"] if ch.isdigit()) or "12")
    except ValueError:
        maanden = 12
    verloopt = today() + datetime.timedelta(days=maanden * 30)

    user_list.append({
        "code": code,
        "geregistreerd": date_str(today()),
        "verloopt": date_str(verloopt),
    })
    save_json("registered", registered)
    return jsonify({"ok": True})


@app.route("/api/order", methods=["POST"])
def api_order():
    """Plaats een bestelling."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])
    adres = (data.get("adres") or "").strip()

    if not items:
        return jsonify({"ok": False, "fout": "Je winkelwagen is leeg."})
    if not adres:
        return jsonify({"ok": False, "fout": "Vul een bezorgadres in."})

    totaal = 0.0
    clean_items = []
    for it in items:
        p = get_product(it.get("code", ""))
        if not p:
            continue
        aantal = max(1, int(it.get("aantal", 1)))
        totaal += p["prijs"] * aantal
        clean_items.append({"code": p["code"], "naam": p["naam"], "aantal": aantal, "prijs": p["prijs"]})

    if not clean_items:
        return jsonify({"ok": False, "fout": "Geen geldige producten in de winkelwagen."})

    orders = load_json("orders", [])
    order_id = "ORD-" + str(1000 + len(orders) + 1)
    order = {
        "id": order_id,
        "email": email,
        "datum": date_str(today()),
        "items": clean_items,
        "totaal": round(totaal, 2),
        "adres": adres,
        "status": "In verwerking",
    }
    orders.append(order)
    save_json("orders", orders)

    add_notification(email, "bestelling", "Bestelling geplaatst",
                     "Je bestelling " + order_id + " van EUR " + ("%.2f" % totaal).replace(".", ",") +
                     " is ontvangen en wordt verwerkt.")
    return jsonify({"ok": True, "order": order})


@app.route("/api/complaint", methods=["POST"])
def api_complaint():
    """Dien een nieuwe klacht in."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    product = (data.get("product") or "").strip()
    categorie = (data.get("categorie") or "").strip()
    omschrijving = (data.get("omschrijving") or "").strip()
    foto = (data.get("foto") or "").strip()

    if not product or not categorie or not omschrijving:
        return jsonify({"ok": False, "fout": "Kies een product, categorie en vul een omschrijving in."})

    complaints = load_json("complaints", [])
    complaint_id = "KL-" + str(2000 + len(complaints) + 1)
    complaint = {
        "id": complaint_id,
        "email": email,
        "datum": date_str(today()),
        "product": product,
        "categorie": categorie,
        "omschrijving": omschrijving,
        "foto": foto,
        "status": "Ontvangen",
    }
    complaints.append(complaint)
    save_json("complaints", complaints)

    add_notification(email, "klacht", "Klacht ontvangen",
                     "Je klacht " + complaint_id + " over " + product + " is ontvangen. Status: Ontvangen.")
    return jsonify({"ok": True, "complaint": complaint})


@app.route("/api/complaint/status", methods=["POST"])
def api_complaint_status():
    """Demo-functie: wijzig de status van een klacht en genereer een notificatie."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    complaint_id = data.get("id")
    nieuwe_status = data.get("status")
    geldige = ["Ontvangen", "In behandeling", "Opgelost"]
    if nieuwe_status not in geldige:
        return jsonify({"ok": False, "fout": "Ongeldige status."})

    complaints = load_json("complaints", [])
    found = None
    for c in complaints:
        if c.get("id") == complaint_id and c.get("email") == email:
            c["status"] = nieuwe_status
            found = c
            break
    if not found:
        return jsonify({"ok": False, "fout": "Klacht niet gevonden."})
    save_json("complaints", complaints)

    add_notification(email, "klacht", "Klachtstatus gewijzigd",
                     "De status van klacht " + complaint_id + " is nu: " + nieuwe_status + ".")
    return jsonify({"ok": True})


@app.route("/api/account", methods=["POST"])
def api_account():
    """Werk accountgegevens en voorkeuren bij."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}

    accounts = load_json("accounts", {})
    acct = accounts.get(email)
    if not acct:
        return jsonify({"ok": False, "fout": "Account niet gevonden."})

    naam = (data.get("naam") or "").strip()
    if naam:
        acct["naam"] = naam
    acct["allergieen"] = data.get("allergieen", acct.get("allergieen", []))
    acct["favorieten"] = data.get("favorieten", acct.get("favorieten", []))
    save_json("accounts", accounts)

    prefs = load_json("preferences", {})
    prefs[email] = {
        "notif_bestelling": bool(data.get("notif_bestelling", True)),
        "notif_klacht": bool(data.get("notif_klacht", True)),
        "notif_houdbaarheid": bool(data.get("notif_houdbaarheid", True)),
        "notif_aanbeveling": bool(data.get("notif_aanbeveling", True)),
    }
    save_json("preferences", prefs)
    return jsonify({"ok": True})


@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    """Markeer alle notificaties van de gebruiker als gelezen."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    notifications = load_json("notifications", [])
    for n in notifications:
        if n.get("email") == email:
            n["gelezen"] = True
    save_json("notifications", notifications)
    return jsonify({"ok": True})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Chatbot-antwoord via de FAQ-engine."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    antwoord = chatbot_answer(data.get("message", ""))
    return jsonify({"ok": True, "antwoord": antwoord})


# ---------------------------------------------------------------------------
# HOOFD-ROUTE: serveer login- of app-pagina
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user():
        return Response(APP_HTML, mimetype="text/html")
    return Response(LOGIN_HTML, mimetype="text/html")


# ===========================================================================
# FRONTEND: LOGIN PAGINA (HTML + CSS + JS)
# ===========================================================================

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cacao Company</title>
<style>
:root{
  --creme:#F7F1E7; --creme-2:#FBF7F0; --bruin:#3E2723; --bruin-2:#5D4037;
  --bruin-3:#6F4E37; --goud:#C2A24C; --goud-licht:#E3CD8F; --tekst:#33271F;
  --grijs:#8C8079; --wit:#FFFFFF; --schaduw:0 18px 50px rgba(62,39,35,.18);
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif;
  background:linear-gradient(160deg,#2A1A14,#4A2F25 60%,#6F4E37);
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  color:var(--tekst);padding:20px;
}
.phone{
  width:100%;max-width:420px;background:var(--creme-2);border-radius:38px;
  box-shadow:var(--schaduw);overflow:hidden;padding:46px 30px 40px;
  border:1px solid rgba(255,255,255,.4);
}
.brand{text-align:center;margin-bottom:34px}
.logo{font-size:54px;line-height:1}
.brand h1{font-family:Georgia,'Times New Roman',serif;font-size:30px;color:var(--bruin);
  letter-spacing:.5px;margin-top:10px}
.brand .tag{color:var(--goud);font-size:13px;letter-spacing:3px;text-transform:uppercase;margin-top:6px}
.tabs{display:flex;background:var(--creme);border-radius:14px;padding:5px;margin-bottom:24px}
.tabs button{flex:1;border:none;background:none;padding:11px;border-radius:10px;
  font-size:14px;font-weight:600;color:var(--grijs);cursor:pointer;transition:.2s}
.tabs button.active{background:var(--wit);color:var(--bruin);box-shadow:0 3px 10px rgba(62,39,35,.1)}
label{display:block;font-size:13px;font-weight:600;color:var(--bruin-2);margin:14px 0 6px}
input{
  width:100%;padding:14px 15px;border:1.5px solid #E6DCC9;border-radius:13px;
  font-size:15px;background:var(--wit);color:var(--tekst);transition:.2s;outline:none;
}
input:focus{border-color:var(--goud);box-shadow:0 0 0 3px rgba(194,162,76,.15)}
.btn{
  width:100%;margin-top:24px;padding:15px;border:none;border-radius:14px;cursor:pointer;
  background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  font-size:16px;font-weight:600;letter-spacing:.3px;box-shadow:0 10px 24px rgba(62,39,35,.32);
  transition:transform .15s,box-shadow .15s;
}
.btn:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(62,39,35,.4)}
.btn:active{transform:translateY(0)}
.foutmelding{background:#FBEAEA;color:#A33;border-radius:11px;padding:11px 14px;
  font-size:13px;margin-top:16px;display:none}
.demo-hint{margin-top:22px;text-align:center;font-size:12px;color:var(--grijs);line-height:1.6}
.demo-hint b{color:var(--bruin-2)}
.hidden{display:none}
</style>
</head>
<body>
<div class="phone">
  <div class="brand">
    <div class="logo">&#127851;</div>
    <h1>Cacao Company</h1>
    <div class="tag">Premium Chocolate</div>
  </div>
  <div class="tabs">
    <button id="tab-login" class="active" onclick="switchTab('login')">Inloggen</button>
    <button id="tab-register" onclick="switchTab('register')">Account aanmaken</button>
  </div>

  <div id="form-login">
    <label>E-mailadres</label>
    <input id="l-email" type="email" placeholder="naam@email.nl" autocomplete="username">
    <label>Wachtwoord</label>
    <input id="l-pass" type="password" placeholder="Je wachtwoord" autocomplete="current-password">
    <button class="btn" onclick="doLogin()">Inloggen</button>
  </div>

  <div id="form-register" class="hidden">
    <label>Naam</label>
    <input id="r-naam" type="text" placeholder="Voor- en achternaam">
    <label>E-mailadres</label>
    <input id="r-email" type="email" placeholder="naam@email.nl">
    <label>Wachtwoord</label>
    <input id="r-pass" type="password" placeholder="Minimaal 4 tekens">
    <button class="btn" onclick="doRegister()">Account aanmaken</button>
  </div>

  <div id="fout" class="foutmelding"></div>

  <div class="demo-hint">
    Demo-account &middot; <b>demo@cacao.nl</b> / <b>demo123</b>
  </div>
</div>

<script>
function switchTab(t){
  document.getElementById('tab-login').classList.toggle('active', t==='login');
  document.getElementById('tab-register').classList.toggle('active', t==='register');
  document.getElementById('form-login').classList.toggle('hidden', t!=='login');
  document.getElementById('form-register').classList.toggle('hidden', t!=='register');
  document.getElementById('fout').style.display='none';
}
function toonFout(msg){
  var f=document.getElementById('fout');
  f.textContent=msg; f.style.display='block';
}
async function doLogin(){
  var email=document.getElementById('l-email').value;
  var wachtwoord=document.getElementById('l-pass').value;
  var r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:email,wachtwoord:wachtwoord})});
  var d=await r.json();
  if(d.ok){location.href='/';}else{toonFout(d.fout);}
}
async function doRegister(){
  var naam=document.getElementById('r-naam').value;
  var email=document.getElementById('r-email').value;
  var wachtwoord=document.getElementById('r-pass').value;
  var r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({naam:naam,email:email,wachtwoord:wachtwoord})});
  var d=await r.json();
  if(d.ok){location.href='/';}else{toonFout(d.fout);}
}
document.addEventListener('keydown',function(e){
  if(e.key==='Enter'){
    if(document.getElementById('form-login').classList.contains('hidden')){doRegister();}
    else{doLogin();}
  }
});
</script>
</body>
</html>"""


# ===========================================================================
# FRONTEND: APP (HTML + CSS + JS) - single page met bottom navigation
# ===========================================================================

APP_HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cacao Company</title>
<style>
:root{
  --creme:#F7F1E7; --creme-2:#FBF7F0; --bruin:#3E2723; --bruin-2:#5D4037;
  --bruin-3:#6F4E37; --goud:#C2A24C; --goud-licht:#E3CD8F; --tekst:#33271F;
  --grijs:#8C8079; --grijs-licht:#B8ADA3; --wit:#FFFFFF;
  --schaduw:0 18px 50px rgba(62,39,35,.18); --kaart-schaduw:0 6px 18px rgba(62,39,35,.08);
  --groen:#4F7A52; --oranje:#C77A2B; --rood:#B4503E; --blauw:#5A6B8C;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{
  font-family:'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif;
  background:linear-gradient(160deg,#2A1A14,#4A2F25 60%,#6F4E37);
  min-height:100vh;display:flex;align-items:center;justify-content:center;color:var(--tekst);
}
#app{
  width:100%;max-width:430px;height:92vh;max-height:900px;background:var(--creme-2);
  border-radius:40px;box-shadow:var(--schaduw);overflow:hidden;position:relative;
  display:flex;flex-direction:column;border:1px solid rgba(255,255,255,.35);
}
/* Topbar */
.topbar{
  background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  padding:20px 22px 18px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;
}
.topbar .titel{font-family:Georgia,serif;font-size:21px;letter-spacing:.3px;display:flex;align-items:center;gap:9px}
.bell{position:relative;font-size:22px;cursor:pointer;background:rgba(255,255,255,.12);
  width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.2s}
.bell:hover{background:rgba(255,255,255,.22)}
.badge{position:absolute;top:-3px;right:-3px;background:var(--goud);color:var(--bruin);
  font-size:11px;font-weight:700;min-width:19px;height:19px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;padding:0 5px;border:2px solid var(--bruin)}
/* Scherm */
#scherm{flex:1;overflow-y:auto;padding:20px 18px 24px;-webkit-overflow-scrolling:touch}
#scherm::-webkit-scrollbar{width:0}
/* Bottom nav */
.nav{
  display:flex;background:var(--wit);border-top:1px solid #EFE6D6;flex-shrink:0;
  box-shadow:0 -6px 20px rgba(62,39,35,.06);
}
.nav button{flex:1;border:none;background:none;padding:11px 4px 13px;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--grijs-licht);
  font-size:10.5px;font-weight:600;transition:.2s}
.nav button .ico{font-size:21px;transition:transform .2s}
.nav button.active{color:var(--bruin)}
.nav button.active .ico{transform:translateY(-2px) scale(1.12)}
/* Algemene componenten */
h2.sectie{font-family:Georgia,serif;font-size:19px;color:var(--bruin);margin:22px 4px 12px;font-weight:600}
h2.sectie:first-child{margin-top:4px}
.kaart{background:var(--wit);border-radius:20px;padding:16px;box-shadow:var(--kaart-schaduw);margin-bottom:13px}
.welkom{background:linear-gradient(135deg,#fff,#FBF3E3);border-radius:22px;padding:20px;
  box-shadow:var(--kaart-schaduw);margin-bottom:6px;border:1px solid #F1E6D0}
.welkom .hi{font-size:13px;color:var(--goud);font-weight:700;letter-spacing:1.5px;text-transform:uppercase}
.welkom .naam{font-family:Georgia,serif;font-size:25px;color:var(--bruin);margin-top:3px}
.welkom .sub{font-size:13.5px;color:var(--grijs);margin-top:7px;line-height:1.5}
/* Productkaart horizontaal scroll */
.hscroll{display:flex;gap:13px;overflow-x:auto;padding:4px 4px 8px;scroll-snap-type:x mandatory}
.hscroll::-webkit-scrollbar{height:0}
.prodkaart{min-width:155px;width:155px;background:var(--wit);border-radius:20px;
  box-shadow:var(--kaart-schaduw);overflow:hidden;cursor:pointer;scroll-snap-align:start;
  transition:transform .18s;display:flex;flex-direction:column}
.prodkaart:active{transform:scale(.97)}
.prodkaart .emoji{height:96px;display:flex;align-items:center;justify-content:center;font-size:46px;
  background:linear-gradient(135deg,#F3E9D6,#EADFC6)}
.prodkaart .info{padding:11px 12px 13px;flex:1;display:flex;flex-direction:column}
.prodkaart .pn{font-size:13.5px;font-weight:700;color:var(--bruin);line-height:1.25}
.prodkaart .pc{font-size:11px;color:var(--grijs);margin-top:3px}
.prodkaart .pp{font-size:15px;font-weight:700;color:var(--goud);margin-top:auto;padding-top:8px}
.cat-pill{display:inline-block;background:var(--creme);color:var(--bruin-2);font-size:11px;
  font-weight:600;padding:3px 9px;border-radius:8px;align-self:flex-start;margin-top:4px}
/* Lijst-item */
.li{display:flex;align-items:center;gap:13px;padding:13px 4px;border-bottom:1px solid #F1E9DB}
.li:last-child{border-bottom:none}
.li .ic{width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#F3E9D6,#EADFC6);
  display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0}
.li .mid{flex:1;min-width:0}
.li .t{font-size:14.5px;font-weight:700;color:var(--bruin)}
.li .s{font-size:12.5px;color:var(--grijs);margin-top:2px}
.li .r{text-align:right;flex-shrink:0}
/* Status badges */
.status{font-size:11px;font-weight:700;padding:4px 10px;border-radius:9px;display:inline-block;white-space:nowrap}
.st-goed{background:#E7F0E6;color:var(--groen)}
.st-bijna{background:#FBEFDF;color:var(--oranje)}
.st-verlopen{background:#F7E3DF;color:var(--rood)}
.st-ontvangen{background:#E9EDF4;color:var(--blauw)}
.st-behandeling{background:#FBEFDF;color:var(--oranje)}
.st-opgelost{background:#E7F0E6;color:var(--groen)}
.st-verwerking{background:#FBEFDF;color:var(--oranje)}
.st-bezorgd{background:#E7F0E6;color:var(--groen)}
/* Knoppen */
.btn{padding:14px;border:none;border-radius:14px;cursor:pointer;width:100%;
  background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  font-size:15px;font-weight:600;box-shadow:0 8px 20px rgba(62,39,35,.28);transition:transform .15s}
.btn:hover{transform:translateY(-2px)}
.btn:active{transform:translateY(0)}
.btn.goud{background:linear-gradient(135deg,var(--goud),#A8843A);color:#fff}
.btn.licht{background:var(--creme);color:var(--bruin);box-shadow:none;border:1.5px solid #E6DCC9}
.btn.klein{width:auto;padding:9px 16px;font-size:13px;border-radius:11px}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
/* Formulier */
label{display:block;font-size:13px;font-weight:600;color:var(--bruin-2);margin:14px 0 6px}
input,select,textarea{width:100%;padding:13px 14px;border:1.5px solid #E6DCC9;border-radius:13px;
  font-size:15px;background:var(--wit);color:var(--tekst);outline:none;font-family:inherit;transition:.2s}
input:focus,select:focus,textarea:focus{border-color:var(--goud);box-shadow:0 0 0 3px rgba(194,162,76,.15)}
textarea{resize:vertical;min-height:90px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.chip{padding:8px 14px;border-radius:20px;border:1.5px solid #E6DCC9;background:var(--wit);
  font-size:13px;font-weight:600;color:var(--bruin-2);cursor:pointer;transition:.18s}
.chip.on{background:var(--bruin);color:#F8EFDD;border-color:var(--bruin)}
/* Overlay (subpaginas) */
.overlay{position:absolute;inset:0;background:var(--creme-2);z-index:30;display:flex;flex-direction:column;
  animation:slide .25s ease}
@keyframes slide{from{transform:translateX(100%)}to{transform:translateX(0)}}
.ov-top{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;padding:18px 18px;
  display:flex;align-items:center;gap:14px;flex-shrink:0}
.ov-top .back{font-size:22px;cursor:pointer;background:rgba(255,255,255,.12);width:38px;height:38px;
  border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.2s}
.ov-top .back:hover{background:rgba(255,255,255,.22)}
.ov-top .titel{font-family:Georgia,serif;font-size:18px}
.ov-body{flex:1;overflow-y:auto;padding:20px 18px 26px}
.ov-body::-webkit-scrollbar{width:0}
/* Productdetail */
.detail-hero{height:170px;border-radius:22px;display:flex;align-items:center;justify-content:center;
  font-size:80px;background:linear-gradient(135deg,#F3E9D6,#EADFC6);margin-bottom:16px;box-shadow:var(--kaart-schaduw)}
.detail-naam{font-family:Georgia,serif;font-size:24px;color:var(--bruin)}
.detail-prijs{font-size:22px;font-weight:700;color:var(--goud);margin:6px 0}
.info-rij{padding:13px 0;border-bottom:1px solid #F1E9DB}
.info-rij .lbl{font-size:12px;font-weight:700;color:var(--goud);text-transform:uppercase;letter-spacing:.6px}
.info-rij .val{font-size:14.5px;color:var(--tekst);margin-top:4px;line-height:1.5}
/* Scanner */
.scanner{aspect-ratio:1;background:linear-gradient(160deg,#241612,#3E2723);border-radius:26px;
  position:relative;margin-bottom:18px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.scan-frame{width:62%;aspect-ratio:1;border-radius:20px;position:relative}
.scan-frame span{position:absolute;width:34px;height:34px;border:3.5px solid var(--goud)}
.scan-frame .tl{top:0;left:0;border-right:none;border-bottom:none;border-radius:14px 0 0 0}
.scan-frame .tr{top:0;right:0;border-left:none;border-bottom:none;border-radius:0 14px 0 0}
.scan-frame .bl{bottom:0;left:0;border-right:none;border-top:none;border-radius:0 0 0 14px}
.scan-frame .br{bottom:0;right:0;border-left:none;border-top:none;border-radius:0 0 14px 0}
.scan-line{position:absolute;left:8%;right:8%;height:3px;background:linear-gradient(90deg,transparent,var(--goud),transparent);
  border-radius:3px;top:10%;animation:scan 2.4s ease-in-out infinite;box-shadow:0 0 12px var(--goud)}
@keyframes scan{0%,100%{top:12%}50%{top:84%}}
.scan-emoji{position:absolute;font-size:46px;opacity:.25}
/* Chat */
.chat-wrap{display:flex;flex-direction:column;height:100%}
.chat-msgs{flex:1;overflow-y:auto;padding:6px 2px 12px;display:flex;flex-direction:column;gap:11px}
.chat-msgs::-webkit-scrollbar{width:0}
.bubble{max-width:80%;padding:12px 15px;border-radius:18px;font-size:14px;line-height:1.5;box-shadow:var(--kaart-schaduw)}
.bubble.bot{background:var(--wit);color:var(--tekst);align-self:flex-start;border-bottom-left-radius:5px}
.bubble.user{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  align-self:flex-end;border-bottom-right-radius:5px}
.chat-quick{display:flex;gap:8px;overflow-x:auto;padding:8px 0}
.chat-quick::-webkit-scrollbar{height:0}
.chat-quick .chip{white-space:nowrap;flex-shrink:0}
.chat-input{display:flex;gap:9px;padding-top:10px;align-items:center}
.chat-input input{border-radius:24px}
.chat-input .send{width:48px;height:48px;flex-shrink:0;border:none;border-radius:50%;cursor:pointer;
  background:linear-gradient(135deg,var(--goud),#A8843A);color:#fff;font-size:19px;
  display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(194,162,76,.4)}
/* Winkelwagen */
.cart-bar{position:sticky;bottom:0;background:var(--wit);border-radius:18px;padding:14px;
  box-shadow:0 -4px 20px rgba(62,39,35,.12);margin-top:8px;border:1px solid #F1E6D0}
.qty{display:flex;align-items:center;gap:11px}
.qty button{width:30px;height:30px;border-radius:9px;border:1.5px solid #E6DCC9;background:var(--wit);
  font-size:17px;font-weight:700;color:var(--bruin);cursor:pointer;line-height:1}
.qty .n{font-size:15px;font-weight:700;min-width:20px;text-align:center}
/* Notificatie-item */
.notif{display:flex;gap:12px;padding:13px;border-radius:15px;margin-bottom:9px;background:var(--wit);
  box-shadow:var(--kaart-schaduw)}
.notif.unread{border-left:4px solid var(--goud)}
.notif .ni{font-size:22px}
.notif .nt{font-size:14px;font-weight:700;color:var(--bruin)}
.notif .nx{font-size:12.5px;color:var(--grijs);margin-top:3px;line-height:1.45}
.notif .nz{font-size:11px;color:var(--grijs-licht);margin-top:5px}
.leeg{text-align:center;color:var(--grijs);font-size:13.5px;padding:30px 10px;line-height:1.6}
.leeg .e{font-size:40px;display:block;margin-bottom:10px;opacity:.6}
.toast{position:absolute;left:50%;bottom:86px;transform:translateX(-50%);background:var(--bruin);
  color:#F8EFDD;padding:13px 22px;border-radius:30px;font-size:13.5px;font-weight:600;z-index:60;
  box-shadow:var(--schaduw);opacity:0;transition:opacity .3s,transform .3s;pointer-events:none;white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(-6px)}
.divider{height:1px;background:#EFE6D6;margin:18px 0}
.muted{font-size:12.5px;color:var(--grijs);line-height:1.5}
.row-between{display:flex;justify-content:space-between;align-items:center}
.totaal-rij{display:flex;justify-content:space-between;font-size:17px;font-weight:700;color:var(--bruin);
  padding:12px 0;border-top:2px solid #EFE6D6;margin-top:6px}
</style>
</head>
<body>
<div id="app">
  <div class="topbar">
    <div class="titel">&#127851; Cacao Company</div>
    <div class="bell" onclick="openNotificaties()">&#128276;<span id="notif-badge" class="badge" style="display:none">0</span></div>
  </div>
  <div id="scherm"></div>
  <div class="nav">
    <button id="nav-home" onclick="gaNaar('home')"><span class="ico">&#127968;</span>Home</button>
    <button id="nav-scan" onclick="gaNaar('scan')"><span class="ico">&#128247;</span>Scan</button>
    <button id="nav-chat" onclick="gaNaar('chat')"><span class="ico">&#128172;</span>Assistent</button>
    <button id="nav-shop" onclick="gaNaar('shop')"><span class="ico">&#128722;</span>Shop</button>
    <button id="nav-profiel" onclick="gaNaar('profiel')"><span class="ico">&#128100;</span>Profiel</button>
  </div>
  <div id="overlay-host"></div>
  <div id="toast" class="toast"></div>
</div>

<script>
/* ============== STATE ============== */
var STATE = null;
var TAB = 'home';
var CART = {};          // code -> aantal
var CHAT = [];          // {rol, tekst}

/* ============== HELPERS ============== */
function euro(n){ return 'EUR ' + n.toFixed(2).replace('.', ','); }
function el(id){ return document.getElementById(id); }
function esc(s){ var d=document.createElement('div'); d.textContent=s==null?'':String(s); return d.innerHTML; }

function statusClass(s){
  var m={'Goed':'st-goed','Bijna verlopen':'st-bijna','Verlopen':'st-verlopen',
    'Ontvangen':'st-ontvangen','In behandeling':'st-behandeling','Opgelost':'st-opgelost',
    'In verwerking':'st-verwerking','Bezorgd':'st-bezorgd'};
  return m[s]||'st-ontvangen';
}
function toast(msg){
  var t=el('toast'); t.textContent=msg; t.classList.add('show');
  clearTimeout(t._t); t._t=setTimeout(function(){t.classList.remove('show');},2200);
}
async function api(url, body){
  var opt={headers:{'Content-Type':'application/json'}};
  if(body!==undefined){ opt.method='POST'; opt.body=JSON.stringify(body); }
  var r=await fetch(url, opt);
  if(r.status===401){ location.href='/'; return {ok:false}; }
  return await r.json();
}
async function laadState(){
  var d=await api('/api/state');
  if(d.ok){ STATE=d; updateBadge(); }
  return d;
}
function updateBadge(){
  if(!STATE) return;
  var n=STATE.notifications.filter(function(x){return !x.gelezen;}).length;
  var b=el('notif-badge');
  if(n>0){ b.textContent=n; b.style.display='flex'; } else { b.style.display='none'; }
}
function cartCount(){ var s=0; for(var k in CART){ s+=CART[k]; } return s; }
function cartTotaal(){
  var s=0; for(var k in CART){ var p=prodByCode(k); if(p) s+=p.prijs*CART[k]; } return s;
}
function prodByCode(c){ return STATE.products.filter(function(p){return p.code===c;})[0]; }

/* ============== NAVIGATIE ============== */
function gaNaar(tab){
  TAB=tab; sluitOverlay();
  ['home','scan','chat','shop','profiel'].forEach(function(t){
    el('nav-'+t).classList.toggle('active', t===tab);
  });
  render();
}
function render(){
  if(TAB==='home') renderHome();
  else if(TAB==='scan') renderScan();
  else if(TAB==='chat') renderChat();
  else if(TAB==='shop') renderShop();
  else if(TAB==='profiel') renderProfiel();
}

/* ============== OVERLAY ============== */
function openOverlay(titel, bodyHTML){
  el('overlay-host').innerHTML =
    '<div class="overlay"><div class="ov-top"><div class="back" onclick="sluitOverlay()">&#8249;</div>'+
    '<div class="titel">'+titel+'</div></div><div class="ov-body" id="ov-body">'+bodyHTML+'</div></div>';
}
function sluitOverlay(){ el('overlay-host').innerHTML=''; }

/* ============== HOME ============== */
function renderHome(){
  var s=STATE;
  var h='';
  var voornaam=(s.account.naam||'').split(' ')[0]||'klant';
  h+='<div class="welkom"><div class="hi">Welkom terug</div>'+
     '<div class="naam">Hallo, '+esc(voornaam)+' \uD83D\uDC4B</div>'+
     '<div class="sub">Ontdek je collectie, je laatste bestellingen en aanbevelingen die bij jou passen.</div></div>';

  // Aanbevelingen
  h+='<h2 class="sectie">Aanbevolen voor jou \u2728</h2>';
  h+='<div class="hscroll">';
  s.recommendations.forEach(function(p){ h+=prodCardHTML(p); });
  h+='</div>';

  // Bijna verlopen
  if(s.bijna_verlopen.length){
    h+='<h2 class="sectie">Bijna verlopen \u23F3</h2>';
    s.bijna_verlopen.forEach(function(p){
      var dg=p.dagen_resterend;
      var tekst = dg<0 ? 'Verlopen' : (dg===0?'Verloopt vandaag':'Nog '+dg+' dag'+(dg===1?'':'en'));
      h+='<div class="kaart li" onclick="openProduct(\''+p.code+'\')"><div class="ic">'+p.emoji+'</div>'+
         '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">Houdbaar tot '+esc(p.verloopt)+'</div></div>'+
         '<div class="r"><span class="status st-bijna">'+tekst+'</span></div></div>';
    });
  }

  // Geregistreerde producten
  h+='<div class="row-between" style="margin:22px 4px 12px"><h2 class="sectie" style="margin:0">Mijn collectie</h2>'+
     '<span class="muted">'+s.registered.length+' product'+(s.registered.length===1?'':'en')+'</span></div>';
  if(s.registered.length){
    s.registered.slice(0,4).forEach(function(p){
      h+='<div class="kaart li" onclick="openProduct(\''+p.code+'\')"><div class="ic">'+p.emoji+'</div>'+
         '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+esc(p.herkomst)+'</div></div>'+
         '<div class="r"><span class="status '+statusClass(p.status)+'">'+p.status+'</span></div></div>';
    });
  } else {
    h+='<div class="kaart"><div class="leeg"><span class="e">\uD83D\uDCE6</span>Nog geen producten geregistreerd. Scan een reep om te beginnen.</div></div>';
  }

  // Recente bestellingen
  h+='<h2 class="sectie">Recente bestellingen</h2>';
  if(s.orders.length){
    s.orders.slice(0,3).forEach(function(o){
      h+='<div class="kaart li" onclick="openOrder(\''+o.id+'\')"><div class="ic">\uD83D\uDCE6</div>'+
         '<div class="mid"><div class="t">'+esc(o.id)+'</div><div class="s">'+esc(o.datum)+' &middot; '+euro(o.totaal)+'</div></div>'+
         '<div class="r"><span class="status '+statusClass(o.status)+'">'+o.status+'</span></div></div>';
    });
  } else {
    h+='<div class="kaart"><div class="leeg"><span class="e">\uD83D\uDED2</span>Nog geen bestellingen geplaatst.</div></div>';
  }

  // Recente notificaties
  h+='<div class="row-between" style="margin:22px 4px 12px"><h2 class="sectie" style="margin:0">Notificaties</h2>'+
     '<span class="muted" style="cursor:pointer;color:var(--goud)" onclick="openNotificaties()">Alles bekijken</span></div>';
  if(s.notifications.length){
    s.notifications.slice(0,3).forEach(function(n){ h+=notifHTML(n); });
  } else {
    h+='<div class="kaart"><div class="leeg"><span class="e">\uD83D\uDD14</span>Geen notificaties.</div></div>';
  }

  el('scherm').innerHTML=h;
}

function prodCardHTML(p){
  return '<div class="prodkaart" onclick="openProduct(\''+p.code+'\')">'+
    '<div class="emoji">'+p.emoji+'</div><div class="info">'+
    '<div class="pn">'+esc(p.naam)+'</div>'+
    '<span class="cat-pill">'+esc(p.categorie)+'</span>'+
    '<div class="pp">'+euro(p.prijs)+'</div></div></div>';
}
function notifHTML(n){
  var ico={'bestelling':'\uD83D\uDCE6','klacht':'\uD83D\uDCDD','houdbaarheid':'\u23F3','aanbeveling':'\u2728'}[n.type]||'\uD83D\uDD14';
  return '<div class="notif '+(n.gelezen?'':'unread')+'"><div class="ni">'+ico+'</div>'+
    '<div><div class="nt">'+esc(n.titel)+'</div><div class="nx">'+esc(n.tekst)+'</div>'+
    '<div class="nz">'+esc(n.tijd)+'</div></div></div>';
}

/* ============== NOTIFICATIES ============== */
async function openNotificaties(){
  var h='';
  if(STATE.notifications.length){
    STATE.notifications.forEach(function(n){ h+=notifHTML(n); });
  } else {
    h='<div class="leeg"><span class="e">\uD83D\uDD14</span>Je hebt nog geen notificaties.</div>';
  }
  openOverlay('Notificaties', h);
  await api('/api/notifications/read', {});
  await laadState();
}

/* ============== PRODUCTDETAIL ============== */
function openProduct(code){
  var p=prodByCode(code); if(!p) return;
  var inCollectie = STATE.registered.some(function(r){return r.code===code;});
  var h='<div class="detail-hero">'+p.emoji+'</div>'+
    '<div class="cat-pill">'+esc(p.categorie)+'</div>'+
    '<div class="detail-naam">'+esc(p.naam)+'</div>'+
    '<div class="detail-prijs">'+euro(p.prijs)+'</div>'+
    '<div class="muted" style="margin-bottom:8px">'+esc(p.beschrijving)+'</div>'+
    '<div class="info-rij"><div class="lbl">Herkomst</div><div class="val">\uD83C\uDF0D '+esc(p.herkomst)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Ingredienten</div><div class="val">'+esc(p.ingredienten)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Allergenen</div><div class="val">\u26A0\uFE0F '+esc(p.allergenen)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Houdbaarheid</div><div class="val">'+esc(p.houdbaarheid)+'</div></div>'+
    '<div style="margin-top:20px;display:flex;flex-direction:column;gap:10px">';
  if(inCollectie){
    h+='<button class="btn licht" disabled>\u2713 In je collectie</button>';
  } else {
    h+='<button class="btn goud" onclick="registreerProduct(\''+code+'\')">+ Toevoegen aan collectie</button>';
  }
  h+='<button class="btn" onclick="voegToeAanCart(\''+code+'\');toast(\'Toegevoegd aan winkelwagen\')">In winkelwagen \u2013 '+euro(p.prijs)+'</button>';
  h+='</div>';
  openOverlay('Productinformatie', h);
}
async function registreerProduct(code){
  var d=await api('/api/register-product', {code:code});
  if(d.ok){ toast('Toegevoegd aan je collectie'); await laadState(); openProduct(code); }
  else toast(d.fout);
}

/* ============== SCAN ============== */
function renderScan(){
  var h='<div class="scanner"><div class="scan-emoji">\uD83D\uDCF1</div>'+
    '<div class="scan-frame"><span class="tl"></span><span class="tr"></span>'+
    '<span class="bl"></span><span class="br"></span><div class="scan-line"></div></div></div>'+
    '<div class="muted" style="text-align:center;margin-bottom:14px">Richt de camera op de QR-code van je reep, of voer de code hieronder handmatig in.</div>'+
    '<label>Productcode</label>'+
    '<input id="scan-code" placeholder="bijv. CACAO-001" style="text-transform:uppercase" onkeydown="if(event.key===\'Enter\')doScan()">'+
    '<div id="scan-fout" style="color:var(--rood);font-size:13px;margin-top:8px;display:none"></div>'+
    '<button class="btn goud" style="margin-top:16px" onclick="doScan()">\uD83D\uDD0D Scan / Zoek product</button>'+
    '<div class="muted" style="text-align:center;margin-top:14px">Demo-codes: CACAO-001 t/m CACAO-008</div>'+
    '<div id="scan-resultaat" style="margin-top:18px"></div>';
  el('scherm').innerHTML=h;
}
async function doScan(){
  var code=el('scan-code').value.trim().toUpperCase();
  var foutEl=el('scan-fout'); foutEl.style.display='none';
  el('scan-resultaat').innerHTML='';
  if(!code){ foutEl.textContent='Voer een productcode in.'; foutEl.style.display='block'; return; }
  var d=await api('/api/scan', {code:code});
  if(!d.ok){ foutEl.textContent=d.fout; foutEl.style.display='block'; return; }
  var p=d.product;
  var inCollectie = STATE.registered.some(function(r){return r.code===p.code;});
  var h='<div class="kaart"><div class="li" style="border:none;padding:0 0 12px">'+
    '<div class="ic" style="width:60px;height:60px;font-size:30px">'+p.emoji+'</div>'+
    '<div class="mid"><div class="t" style="font-size:16px">'+esc(p.naam)+'</div>'+
    '<div class="s">'+esc(p.categorie)+' &middot; '+euro(p.prijs)+'</div></div></div>'+
    '<div class="info-rij"><div class="lbl">Herkomst</div><div class="val">\uD83C\uDF0D '+esc(p.herkomst)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Ingredienten</div><div class="val">'+esc(p.ingredienten)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Allergenen</div><div class="val">\u26A0\uFE0F '+esc(p.allergenen)+'</div></div>'+
    '<div class="info-rij" style="border:none"><div class="lbl">Houdbaarheid</div><div class="val">'+esc(p.houdbaarheid)+'</div></div>';
  if(inCollectie){ h+='<button class="btn licht" style="margin-top:14px" disabled>\u2713 Al in je collectie</button>'; }
  else { h+='<button class="btn goud" style="margin-top:14px" onclick="registreerVanuitScan(\''+p.code+'\')">+ Toevoegen aan collectie</button>'; }
  h+='</div>';
  el('scan-resultaat').innerHTML=h;
}
async function registreerVanuitScan(code){
  var d=await api('/api/register-product', {code:code});
  if(d.ok){ toast('Toegevoegd aan je collectie'); await laadState(); doScan(); }
  else toast(d.fout);
}

/* ============== CHAT ============== */
function renderChat(){
  if(CHAT.length===0){
    CHAT.push({rol:'bot', tekst:'Hallo! \uD83D\uDC4B Ik ben de Cacao Company assistent. Waarmee kan ik je helpen?'});
  }
  var quick=['Allergenen','Houdbaarheid','Bestelling','Klacht indienen','Herkomst cacao'];
  var h='<div class="chat-wrap"><div class="chat-msgs" id="chat-msgs"></div>'+
    '<div class="chat-quick">';
  quick.forEach(function(q){ h+='<div class="chip" onclick="stuurChat(\''+q+'\')">'+q+'</div>'; });
  h+='</div><div class="chat-input"><input id="chat-in" placeholder="Typ je vraag..." '+
    'onkeydown="if(event.key===\'Enter\')stuurChat()"><button class="send" onclick="stuurChat()">\u27A4</button></div></div>';
  el('scherm').innerHTML=h;
  el('scherm').style.padding='12px 16px 16px';
  tekenChat();
}
function tekenChat(){
  var c=el('chat-msgs'); if(!c) return;
  c.innerHTML = CHAT.map(function(m){
    return '<div class="bubble '+(m.rol==='user'?'user':'bot')+'">'+esc(m.tekst)+'</div>';
  }).join('');
  c.scrollTop=c.scrollHeight;
}
async function stuurChat(tekst){
  var inp=el('chat-in');
  var bericht = tekst!==undefined ? tekst : (inp?inp.value.trim():'');
  if(!bericht) return;
  if(inp) inp.value='';
  CHAT.push({rol:'user', tekst:bericht}); tekenChat();
  var d=await api('/api/chat', {message:bericht});
  CHAT.push({rol:'bot', tekst: d.ok ? d.antwoord : 'Er ging iets mis. Probeer het opnieuw.'});
  tekenChat();
}

/* ============== SHOP ============== */
function renderShop(){
  el('scherm').style.padding='20px 18px 24px';
  var s=STATE;
  var h='<h2 class="sectie">Ons assortiment \uD83C\uDF6B</h2>';
  h+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:13px">';
  s.products.forEach(function(p){
    h+='<div class="prodkaart" style="min-width:0;width:auto" onclick="openProduct(\''+p.code+'\')">'+
      '<div class="emoji">'+p.emoji+'</div><div class="info">'+
      '<div class="pn">'+esc(p.naam)+'</div><span class="cat-pill">'+esc(p.categorie)+'</span>'+
      '<div class="pp">'+euro(p.prijs)+'</div>'+
      '<button class="btn klein goud" style="width:100%;margin-top:9px" onclick="event.stopPropagation();voegToeAanCart(\''+p.code+'\')">In mandje</button>'+
      '</div></div>';
  });
  h+='</div>';
  el('scherm').innerHTML=h;
  toonCartBalk();
}
function voegToeAanCart(code){
  CART[code]=(CART[code]||0)+1;
  toast('Toegevoegd aan winkelwagen');
  if(TAB==='shop') toonCartBalk();
}
function toonCartBalk(){
  var bestaand=el('cart-balk'); if(bestaand) bestaand.remove();
  var n=cartCount(); if(n===0) return;
  var div=document.createElement('div');
  div.id='cart-balk'; div.className='cart-bar';
  div.innerHTML='<div class="row-between"><div><div style="font-weight:700;color:var(--bruin)">'+
    n+' artikel'+(n===1?'':'en')+'</div><div class="muted">'+euro(cartTotaal())+'</div></div>'+
    '<button class="btn klein goud" onclick="openWinkelwagen()">Naar winkelwagen \u2192</button></div>';
  el('scherm').appendChild(div);
}

/* ============== WINKELWAGEN & CHECKOUT ============== */
function openWinkelwagen(){
  if(cartCount()===0){ toast('Je winkelwagen is leeg'); return; }
  var h='';
  for(var code in CART){
    var p=prodByCode(code); if(!p) continue;
    h+='<div class="kaart li" style="cursor:default"><div class="ic">'+p.emoji+'</div>'+
      '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+euro(p.prijs)+' per stuk</div></div>'+
      '<div class="qty"><button onclick="wijzigCart(\''+code+'\',-1)">\u2212</button>'+
      '<span class="n" id="q-'+code+'">'+CART[code]+'</span>'+
      '<button onclick="wijzigCart(\''+code+'\',1)">+</button></div></div>';
  }
  h+='<div class="kaart"><div class="totaal-rij" style="border:none;padding:0"><span>Totaal</span>'+
    '<span id="cart-totaal">'+euro(cartTotaal())+'</span></div></div>';
  h+='<button class="btn goud" onclick="openCheckout()">Bestelling controleren \u2192</button>';
  openOverlay('Winkelwagen', h);
}
function wijzigCart(code, delta){
  CART[code]=(CART[code]||0)+delta;
  if(CART[code]<=0){ delete CART[code]; }
  if(cartCount()===0){ sluitOverlay(); if(TAB==='shop') toonCartBalk(); toast('Winkelwagen geleegd'); return; }
  openWinkelwagen();
}
function openCheckout(){
  var adres = STATE._adres || '';
  var h='<h2 class="sectie" style="margin-top:0">Bezorgadres</h2>'+
    '<input id="co-adres" placeholder="Straat, postcode, plaats" value="'+esc(adres)+'">'+
    '<h2 class="sectie">Overzicht</h2><div class="kaart">';
  for(var code in CART){
    var p=prodByCode(code); if(!p) continue;
    h+='<div class="li" style="padding:9px 0"><div class="mid"><div class="t" style="font-size:14px">'+
      CART[code]+'\u00D7 '+esc(p.naam)+'</div></div><div class="r" style="font-weight:700;color:var(--bruin)">'+
      euro(p.prijs*CART[code])+'</div></div>';
  }
  var verzend = cartTotaal()>=25 ? 0 : 3.95;
  h+='<div class="li" style="padding:9px 0;border-top:1px solid #F1E9DB"><div class="mid"><div class="s">Verzendkosten'+
    (verzend===0?' (gratis vanaf EUR 25)':'')+'</div></div><div class="r" style="font-weight:700;color:var(--bruin)">'+
    (verzend===0?'Gratis':euro(verzend))+'</div></div>';
  h+='<div class="totaal-rij"><span>Te betalen</span><span>'+euro(cartTotaal()+verzend)+'</span></div></div>';
  h+='<h2 class="sectie">Betaalwijze</h2>'+
    '<div class="kaart li" style="cursor:default"><div class="ic">\uD83D\uDCB3</div>'+
    '<div class="mid"><div class="t">iDEAL (gesimuleerd)</div><div class="s">Veilig afrekenen \u2013 demo</div></div>'+
    '<div class="r">\u2713</div></div>';
  h+='<button class="btn goud" id="btn-betaal" onclick="plaatsBestelling()">\uD83D\uDD12 Nu betalen \u2013 '+euro(cartTotaal()+verzend)+'</button>';
  openOverlay('Afrekenen', h);
}
async function plaatsBestelling(){
  var adres=el('co-adres').value.trim();
  if(!adres){ toast('Vul een bezorgadres in'); return; }
  STATE._adres=adres;
  var btn=el('btn-betaal'); btn.disabled=true; btn.textContent='Betaling verwerken...';
  var items=[]; for(var code in CART){ items.push({code:code, aantal:CART[code]}); }
  // Korte vertraging om een echte betaling na te bootsen.
  await new Promise(function(r){ setTimeout(r, 1100); });
  var d=await api('/api/order', {items:items, adres:adres});
  if(!d.ok){ toast(d.fout); btn.disabled=false; return; }
  CART={};
  await laadState();
  var o=d.order;
  var h='<div style="text-align:center;padding:24px 6px">'+
    '<div style="font-size:64px">\u2705</div>'+
    '<h2 style="font-family:Georgia,serif;color:var(--bruin);font-size:24px;margin:14px 0 6px">Bedankt voor je bestelling!</h2>'+
    '<div class="muted">Je bestelling <b>'+esc(o.id)+'</b> is geplaatst.<br>Verwachte bezorging binnen 2-3 werkdagen.</div></div>'+
    '<div class="kaart"><div class="row-between"><span class="muted">Bestelnummer</span><b>'+esc(o.id)+'</b></div>'+
    '<div class="divider"></div><div class="row-between"><span class="muted">Bezorgadres</span><span style="text-align:right;max-width:60%">'+esc(o.adres)+'</span></div>'+
    '<div class="divider"></div><div class="totaal-rij" style="border:none;padding:0"><span>Totaal</span><span>'+euro(o.totaal)+'</span></div></div>'+
    '<button class="btn" onclick="sluitOverlay();gaNaar(\'home\')">Terug naar home</button>';
  openOverlay('Bevestiging', h);
}

/* ============== PROFIEL ============== */
function renderProfiel(){
  el('scherm').style.padding='20px 18px 24px';
  var a=STATE.account;
  var initialen=(a.naam||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();
  var h='<div class="kaart" style="text-align:center;padding:24px">'+
    '<div style="width:74px;height:74px;border-radius:50%;margin:0 auto 12px;background:linear-gradient(135deg,var(--bruin),var(--bruin-3));'+
    'color:#F8EFDD;display:flex;align-items:center;justify-content:center;font-size:27px;font-weight:700;font-family:Georgia,serif">'+esc(initialen)+'</div>'+
    '<div style="font-family:Georgia,serif;font-size:21px;color:var(--bruin)">'+esc(a.naam)+'</div>'+
    '<div class="muted">'+esc(a.email)+'</div></div>';

  h+='<div class="kaart li" onclick="openAccount()"><div class="ic">\u2699\uFE0F</div>'+
    '<div class="mid"><div class="t">Accountgegevens</div><div class="s">Naam, allergieen, voorkeuren</div></div><div class="r">\u203A</div></div>';
  h+='<div class="kaart li" onclick="openCollectie()"><div class="ic">\uD83D\uDCE6</div>'+
    '<div class="mid"><div class="t">Mijn collectie</div><div class="s">'+STATE.registered.length+' geregistreerde producten</div></div><div class="r">\u203A</div></div>';
  h+='<div class="kaart li" onclick="openOrders()"><div class="ic">\uD83D\uDED2</div>'+
    '<div class="mid"><div class="t">Mijn bestellingen</div><div class="s">'+STATE.orders.length+' bestellingen</div></div><div class="r">\u203A</div></div>';
  h+='<div class="kaart li" onclick="openKlachtForm()"><div class="ic">\uD83D\uDCDD</div>'+
    '<div class="mid"><div class="t">Klacht indienen</div><div class="s">Meld een probleem met een product</div></div><div class="r">\u203A</div></div>';
  var openKl=STATE.complaints.filter(function(c){return c.status!=='Opgelost';}).length;
  h+='<div class="kaart li" onclick="openKlachten()"><div class="ic">\uD83D\uDCCB</div>'+
    '<div class="mid"><div class="t">Mijn klachten</div><div class="s">'+STATE.complaints.length+' klacht'+(STATE.complaints.length===1?'':'en')+
    (openKl?' &middot; '+openKl+' open':'')+'</div></div><div class="r">\u203A</div></div>';

  h+='<div style="margin-top:20px"><button class="btn licht" onclick="uitloggen()">Uitloggen</button></div>';
  h+='<div class="muted" style="text-align:center;margin-top:16px">Cacao Company \u00B7 MVP demo</div>';
  el('scherm').innerHTML=h;
}

/* ----- Account bewerken ----- */
function openAccount(){
  var a=STATE.account, pr=STATE.preferences;
  var allergieenOpties=['Noten','Melk','Gluten','Soja','Pinda','Lactose'];
  var h='<label>Naam</label><input id="ac-naam" value="'+esc(a.naam)+'">'+
    '<label>E-mailadres</label><input id="ac-email" value="'+esc(a.email)+'" disabled style="opacity:.6">'+
    '<label>Allergieen</label><div class="chips" id="ac-allergie">';
  allergieenOpties.forEach(function(opt){
    var on=a.allergieen.indexOf(opt)>=0;
    h+='<div class="chip '+(on?'on':'')+'" data-v="'+opt+'" onclick="this.classList.toggle(\'on\')">'+opt+'</div>';
  });
  h+='</div><label>Favoriete chocoladesoorten</label><div class="chips" id="ac-fav">';
  STATE.categorieen.forEach(function(opt){
    var on=a.favorieten.indexOf(opt)>=0;
    h+='<div class="chip '+(on?'on':'')+'" data-v="'+opt+'" onclick="this.classList.toggle(\'on\')">'+opt+'</div>';
  });
  h+='</div><label style="margin-top:18px">Notificatievoorkeuren</label>';
  var notifs=[['notif_bestelling','Bestellingen'],['notif_klacht','Klachtstatus'],
    ['notif_houdbaarheid','Houdbaarheid'],['notif_aanbeveling','Aanbevelingen']];
  h+='<div class="chips" id="ac-notif">';
  notifs.forEach(function(n){
    var on=pr[n[0]]!==false;
    h+='<div class="chip '+(on?'on':'')+'" data-v="'+n[0]+'" onclick="this.classList.toggle(\'on\')">'+n[1]+'</div>';
  });
  h+='</div><button class="btn goud" style="margin-top:22px" onclick="bewaarAccount()">Wijzigingen opslaan</button>';
  openOverlay('Accountgegevens', h);
}
async function bewaarAccount(){
  function gekozen(id){ return Array.prototype.slice.call(el(id).querySelectorAll('.chip.on')).map(function(c){return c.getAttribute('data-v');}); }
  var allergie=gekozen('ac-allergie'), fav=gekozen('ac-fav'), notif=gekozen('ac-notif');
  var body={naam:el('ac-naam').value.trim(), allergieen:allergie, favorieten:fav,
    notif_bestelling:notif.indexOf('notif_bestelling')>=0,
    notif_klacht:notif.indexOf('notif_klacht')>=0,
    notif_houdbaarheid:notif.indexOf('notif_houdbaarheid')>=0,
    notif_aanbeveling:notif.indexOf('notif_aanbeveling')>=0};
  var d=await api('/api/account', body);
  if(d.ok){ await laadState(); sluitOverlay(); toast('Wijzigingen opgeslagen \u2713'); if(TAB==='profiel') renderProfiel(); }
  else toast(d.fout||'Opslaan mislukt');
}

/* ----- Collectie ----- */
function openCollectie(){
  var h='';
  if(STATE.registered.length){
    STATE.registered.forEach(function(p){
      h+='<div class="kaart li" onclick="openProduct(\''+p.code+'\')"><div class="ic">'+p.emoji+'</div>'+
        '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+esc(p.herkomst)+' &middot; tot '+esc(p.verloopt)+'</div></div>'+
        '<div class="r"><span class="status '+statusClass(p.status)+'">'+p.status+'</span></div></div>';
    });
  } else {
    h='<div class="leeg"><span class="e">\uD83D\uDCE6</span>Nog geen geregistreerde producten.<br>Scan een reep om je collectie te starten.</div>';
  }
  openOverlay('Mijn collectie', h);
}

/* ----- Bestellingen ----- */
function openOrders(){
  var h='';
  if(STATE.orders.length){
    STATE.orders.forEach(function(o){
      h+='<div class="kaart li" onclick="openOrder(\''+o.id+'\')"><div class="ic">\uD83D\uDCE6</div>'+
        '<div class="mid"><div class="t">'+esc(o.id)+'</div><div class="s">'+esc(o.datum)+' &middot; '+o.items.length+' artikel'+(o.items.length===1?'':'en')+'</div></div>'+
        '<div class="r"><div style="font-weight:700;color:var(--bruin)">'+euro(o.totaal)+'</div>'+
        '<span class="status '+statusClass(o.status)+'" style="margin-top:5px">'+o.status+'</span></div></div>';
    });
  } else { h='<div class="leeg"><span class="e">\uD83D\uDED2</span>Nog geen bestellingen.</div>'; }
  openOverlay('Mijn bestellingen', h);
}
function openOrder(id){
  var o=STATE.orders.filter(function(x){return x.id===id;})[0]; if(!o) return;
  var h='<div class="kaart"><div class="row-between"><div><div style="font-family:Georgia,serif;font-size:19px;color:var(--bruin)">'+esc(o.id)+'</div>'+
    '<div class="muted">'+esc(o.datum)+'</div></div><span class="status '+statusClass(o.status)+'">'+o.status+'</span></div></div>';
  h+='<h2 class="sectie">Producten</h2><div class="kaart">';
  o.items.forEach(function(it){
    h+='<div class="li" style="padding:10px 0"><div class="mid"><div class="t" style="font-size:14px">'+it.aantal+'\u00D7 '+esc(it.naam)+'</div></div>'+
      '<div class="r" style="font-weight:700;color:var(--bruin)">'+euro(it.prijs*it.aantal)+'</div></div>';
  });
  h+='<div class="totaal-rij"><span>Totaal</span><span>'+euro(o.totaal)+'</span></div></div>';
  h+='<h2 class="sectie">Bezorgadres</h2><div class="kaart"><div class="val">\uD83D\uDCCD '+esc(o.adres)+'</div></div>';
  openOverlay('Bestelling', h);
}

/* ----- Klacht indienen ----- */
function openKlachtForm(){
  var h='<label>Product</label><select id="kl-product"><option value="">Kies een product...</option>';
  STATE.products.forEach(function(p){ h+='<option>'+esc(p.naam)+'</option>'; });
  h+='</select><label>Categorie</label><select id="kl-cat">';
  ['Smaak','Verpakking','Levering','Kwaliteit','Allergenen','Anders'].forEach(function(c){ h+='<option>'+c+'</option>'; });
  h+='</select><label>Omschrijving</label><textarea id="kl-oms" placeholder="Beschrijf je klacht zo duidelijk mogelijk..."></textarea>'+
    '<label>Foto toevoegen (optioneel)</label>'+
    '<input type="file" id="kl-foto" accept="image/*" onchange="this.nextElementSibling.textContent=this.files.length?(\'\uD83D\uDCCE \'+this.files[0].name):\'\'" style="padding:10px">'+
    '<div class="muted" style="margin-top:5px"></div>'+
    '<button class="btn goud" style="margin-top:22px" onclick="verstuurKlacht()">Klacht verzenden</button>';
  openOverlay('Klacht indienen', h);
}
async function verstuurKlacht(){
  var product=el('kl-product').value, cat=el('kl-cat').value, oms=el('kl-oms').value.trim();
  var fotoInput=el('kl-foto');
  var foto = (fotoInput && fotoInput.files.length) ? fotoInput.files[0].name : '';
  if(!product){ toast('Kies een product'); return; }
  if(!oms){ toast('Vul een omschrijving in'); return; }
  var d=await api('/api/complaint', {product:product, categorie:cat, omschrijving:oms, foto:foto});
  if(!d.ok){ toast(d.fout); return; }
  await laadState();
  var c=d.complaint;
  var h='<div style="text-align:center;padding:24px 6px"><div style="font-size:62px">\uD83D\uDCEC</div>'+
    '<h2 style="font-family:Georgia,serif;color:var(--bruin);font-size:23px;margin:12px 0 6px">Klacht ontvangen</h2>'+
    '<div class="muted">Je klacht <b>'+esc(c.id)+'</b> is geregistreerd.<br>Status: <b>Ontvangen</b>.<br>We nemen zo snel mogelijk contact op.</div></div>'+
    '<button class="btn" onclick="openKlachten()">Bekijk mijn klachten</button>'+
    '<button class="btn licht" style="margin-top:10px" onclick="sluitOverlay();gaNaar(\'profiel\')">Sluiten</button>';
  openOverlay('Bevestiging', h);
}

/* ----- Klachten volgen ----- */
function openKlachten(){
  var h='';
  if(STATE.complaints.length){
    STATE.complaints.forEach(function(c){
      h+='<div class="kaart li" onclick="openKlacht(\''+c.id+'\')"><div class="ic">\uD83D\uDCDD</div>'+
        '<div class="mid"><div class="t">'+esc(c.product)+'</div><div class="s">'+esc(c.datum)+' &middot; '+esc(c.categorie)+'</div></div>'+
        '<div class="r"><span class="status '+statusClass(c.status)+'">'+c.status+'</span></div></div>';
    });
  } else { h='<div class="leeg"><span class="e">\uD83D\uDCCB</span>Je hebt nog geen klachten ingediend.</div>'; }
  openOverlay('Mijn klachten', h);
}
function openKlacht(id){
  var c=STATE.complaints.filter(function(x){return x.id===id;})[0]; if(!c) return;
  var h='<div class="kaart"><div class="row-between"><div style="font-family:Georgia,serif;font-size:18px;color:var(--bruin)">'+esc(c.id)+'</div>'+
    '<span class="status '+statusClass(c.status)+'">'+c.status+'</span></div>'+
    '<div class="divider"></div>'+
    '<div class="info-rij" style="padding-top:0"><div class="lbl">Product</div><div class="val">'+esc(c.product)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Categorie</div><div class="val">'+esc(c.categorie)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Datum</div><div class="val">'+esc(c.datum)+'</div></div>'+
    '<div class="info-rij"'+(c.foto?'':' style="border:none"')+'><div class="lbl">Omschrijving</div><div class="val">'+esc(c.omschrijving)+'</div></div>';
  if(c.foto){ h+='<div class="info-rij" style="border:none"><div class="lbl">Bijlage</div><div class="val">\uD83D\uDCCE '+esc(c.foto)+'</div></div>'; }
  h+='</div>';
  // Demo-functionaliteit: statuswijziging
  h+='<h2 class="sectie">Status wijzigen (demo)</h2><div class="chips">';
  ['Ontvangen','In behandeling','Opgelost'].forEach(function(st){
    h+='<div class="chip '+(c.status===st?'on':'')+'" onclick="wijzigKlachtStatus(\''+c.id+'\',\''+st+'\')">'+st+'</div>';
  });
  h+='</div><div class="muted" style="margin-top:10px">Bij een statuswijziging ontvang je automatisch een notificatie.</div>';
  openOverlay('Klacht '+esc(c.id), h);
}
async function wijzigKlachtStatus(id, status){
  var d=await api('/api/complaint/status', {id:id, status:status});
  if(d.ok){ await laadState(); toast('Status: '+status); openKlacht(id); }
  else toast(d.fout);
}

/* ----- Uitloggen ----- */
async function uitloggen(){
  await api('/api/logout', {});
  location.href='/';
}

/* ============== START ============== */
(async function(){
  await laadState();
  if(!STATE){ location.href='/'; return; }
  gaNaar('home');
})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# START VAN DE APPLICATIE
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Vul databestanden met demodata bij de eerste start.
    seed_if_empty()
    print("=" * 56)
    print("  Cacao Company draait nu!")
    print("  Open in je browser:  http://127.0.0.1:5000")
    print("  Demo-login: demo@cacao.nl / demo123")
    print("  Stoppen: druk op Ctrl + C")
    print("=" * 56)
    app.run(host="127.0.0.1", port=5000, debug=False)