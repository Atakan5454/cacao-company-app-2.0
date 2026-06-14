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
             "verloopt": date_str(t + datetime.timedelta(days=10))},  # bijna verlopen
            {"code": "CACAO-005", "geregistreerd": date_str(t - datetime.timedelta(days=70)),
             "verloopt": date_str(t + datetime.timedelta(days=4))},  # bijna verlopen
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

@app.route("/api/order/cancel", methods=["POST"])
def api_order_cancel():
    """Annuleer een bestelling (indien nog mogelijk)."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    order_id = data.get("id")
    orders = load_json("orders", [])
    found = None
    for o in orders:
        if o.get("id") == order_id and o.get("email") == email:
            found = o
            break
    if not found:
        return jsonify({"ok": False, "fout": "Bestelling niet gevonden."})
    if found.get("status") in ("Bezorgd", "Geannuleerd"):
        return jsonify({"ok": False, "fout": "Deze bestelling kan niet meer worden geannuleerd."})
    found["status"] = "Geannuleerd"
    save_json("orders", orders)
    add_notification(email, "bestelling", "Bestelling geannuleerd",
                     "Je bestelling " + str(order_id) + " is geannuleerd.")
    return jsonify({"ok": True})


@app.route("/api/unregister-product", methods=["POST"])
def api_unregister_product():
    """Verwijder een product uit de persoonlijke collectie."""
    email = current_user()
    if not email:
        return jsonify({"ok": False, "fout": "Niet ingelogd."}), 401
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip().upper()
    registered = load_json("registered", {})
    user_list = registered.get(email, [])
    new_list = [r for r in user_list if r.get("code") != code]
    if len(new_list) == len(user_list):
        return jsonify({"ok": False, "fout": "Dit product staat niet in je collectie."})
    registered[email] = new_list
    save_json("registered", registered)
    return jsonify({"ok": True})


@app.route("/")
def index():
    if current_user():
        return Response(APP_HTML, mimetype="text/html")
    return Response(LOGIN_HTML, mimetype="text/html")


# ===========================================================================
# LOGO (eigen huisstijl) - ingebed als data-URI zodat alles in 1 bestand blijft
# ===========================================================================

LOGO_DATA_URI = "data:image/png;base64,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"

# ===========================================================================
# GEDEELDE STIJL (design tokens + device-frame) - gebruikt door login en app
# ===========================================================================

SHARED_CSS = r"""
:root{
  --creme:#F7F1E7; --creme-2:#FCF8F1; --bruin:#3E2723; --bruin-2:#5D4037;
  --bruin-3:#6F4E37; --goud:#C2A24C; --goud-licht:#E3CD8F; --tekst:#33271F;
  --grijs:#8C8079; --grijs-licht:#B8ADA3; --wit:#FFFFFF;
  --schaduw:0 40px 90px rgba(20,10,6,.55); --kaart-schaduw:0 6px 18px rgba(62,39,35,.08);
  --groen:#4F7A52; --oranje:#C77A2B; --rood:#B4503E; --blauw:#5A6B8C;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{height:100%}
body{
  font-family:'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif;
  background:
    radial-gradient(1200px 700px at 50% -10%, #4a3328 0%, transparent 60%),
    linear-gradient(160deg,#241712,#160d09 70%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  color:var(--tekst);padding:18px;
}
/* ---- iPhone 17 Pro frame ---- */
.device{
  /* Vaste iPhone-maat: de breedte volgt ALLEEN uit de hoogte (verhouding 0.462,
     zoals een iPhone Pro), nooit uit de pagina-inhoud. flex:0 0 auto voorkomt
     dat brede inhoud het toestel oprekt -> elke pagina is exact even breed. */
  --device-h:min(900px,95vh);
  position:relative;flex:0 0 auto;height:var(--device-h);width:calc(var(--device-h) * 0.5625);
  background:linear-gradient(150deg,#2b2b2e,#101012);
  border-radius:58px;padding:11px;box-shadow:var(--schaduw),0 0 0 2px rgba(255,255,255,.04) inset;
}
.device::before{ /* titanium rand-glans */
  content:"";position:absolute;inset:2px;border-radius:58px;pointer-events:none;
  background:linear-gradient(135deg,rgba(255,255,255,.16),transparent 22%,transparent 78%,rgba(255,255,255,.10));
}
.screen{
  position:relative;height:100%;width:100%;background:var(--creme-2);
  border-radius:49px;overflow:hidden;display:flex;flex-direction:column;
}
/* statusbalk */
.statusbar{
  height:54px;flex-shrink:0;display:flex;align-items:flex-end;justify-content:space-between;
  padding:0 30px 7px;font-size:15px;font-weight:600;letter-spacing:.3px;position:relative;z-index:5;
}
.statusbar .klok{font-weight:700}
.statusbar .icons{display:flex;align-items:center;gap:7px}
.statusbar .icons svg{display:block}
/* home-indicator */
.home-indicator{position:absolute;bottom:7px;left:50%;transform:translateX(-50%);
  width:128px;height:5px;border-radius:3px;background:rgba(40,25,18,.30);z-index:9}
"""

# ===========================================================================
# FRONTEND: LOGIN PAGINA
# ===========================================================================

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Cacao Company</title>
<style>
""" + SHARED_CSS + r"""
.screen{justify-content:flex-start;background:
  radial-gradient(900px 500px at 50% 0%, #FFFDF8 0%, var(--creme-2) 55%);}
.login-body{flex:1;display:flex;flex-direction:column;justify-content:flex-start;
  padding:14px 26px 22px;overflow-y:auto}
.login-inner{width:100%;margin:auto 0}
.login-body::-webkit-scrollbar{width:0}
.brand{text-align:center;margin-bottom:16px}
.brand img{width:112px;height:auto;display:block;margin:0 auto;
  filter:drop-shadow(0 10px 22px rgba(62,39,35,.22))}
.brand .tag{color:var(--goud);font-size:11.5px;letter-spacing:4px;text-transform:uppercase;margin-top:12px;font-weight:700}
.login-card{background:var(--wit);border-radius:24px;padding:20px 18px;box-shadow:0 14px 34px rgba(62,39,35,.12);border:1px solid #F1E8D6}
.tabs{display:flex;background:#F0E8D8;border-radius:15px;padding:4px;margin-bottom:18px}
.tabs button{flex:1;border:none;background:none;padding:9px;border-radius:10px;
  font-size:14px;font-weight:600;color:var(--grijs);cursor:pointer;transition:.2s}
.tabs button.active{background:var(--wit);color:var(--bruin);box-shadow:0 3px 10px rgba(62,39,35,.12)}
label{display:block;font-size:12.5px;font-weight:600;color:var(--bruin-2);margin:13px 0 6px}
input{width:100%;padding:15px;border:1.5px solid #E6DCC9;border-radius:14px;
  font-size:15px;background:var(--wit);color:var(--tekst);transition:.2s;outline:none}
input:focus{border-color:var(--goud);box-shadow:0 0 0 3px rgba(194,162,76,.16)}
.btn{width:100%;margin-top:18px;padding:13px;border:none;border-radius:14px;cursor:pointer;
  background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  font-size:16px;font-weight:600;letter-spacing:.3px;box-shadow:0 12px 26px rgba(62,39,35,.34);
  transition:transform .15s,box-shadow .15s}
.btn:hover{transform:translateY(-2px);box-shadow:0 16px 32px rgba(62,39,35,.42)}
.btn:active{transform:translateY(0)}
.foutmelding{background:#FBEAEA;color:#A33;border-radius:12px;padding:12px 14px;
  font-size:13px;margin-top:16px;display:none}
.demo-hint{margin-top:24px;text-align:center;font-size:12px;color:var(--grijs);line-height:1.7}
.demo-hint b{color:var(--bruin-2)}
.hidden{display:none}
</style>
</head>
<body>
<div class="device">
  <div class="screen">

    <div class="statusbar">
      <span class="klok" id="klok">9:41</span>
      <span class="icons">
        <svg width="18" height="12" viewBox="0 0 18 12"><rect x="0" y="7" width="3" height="5" rx="1" fill="#33271F"/><rect x="5" y="4.5" width="3" height="7.5" rx="1" fill="#33271F"/><rect x="10" y="2" width="3" height="10" rx="1" fill="#33271F"/><rect x="15" y="0" width="3" height="12" rx="1" fill="#33271F"/></svg>
        <svg width="17" height="12" viewBox="0 0 17 12"><path d="M8.5 2.5c2.6 0 5 1 6.8 2.7l1.4-1.5C14.5 1.4 11.6 0 8.5 0S2.5 1.4 0 3.7l1.4 1.5C3.1 3.5 5.5 2.5 8.5 2.5z" fill="#33271F"/><path d="M8.5 6c1.5 0 2.9.6 3.9 1.6l1.4-1.5C12.4 4.8 10.5 4 8.5 4s-3.9.8-5.3 2.1l1.4 1.5C5.6 6.6 7 6 8.5 6z" fill="#33271F"/><circle cx="8.5" cy="10.2" r="1.8" fill="#33271F"/></svg>
        <svg width="26" height="13" viewBox="0 0 26 13"><rect x="0.5" y="0.5" width="22" height="12" rx="3.5" fill="none" stroke="#33271F" stroke-opacity=".5"/><rect x="2.5" y="2.5" width="16" height="8" rx="1.5" fill="#33271F"/><rect x="24" y="4" width="2" height="5" rx="1" fill="#33271F" fill-opacity=".5"/></svg>
      </span>
    </div>
    <div class="login-body">
      <div class="login-inner">
      <div class="brand">
        <img src="data:image/png;base64,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" alt="Cacao Company logo">
        <div class="tag">Premium Chocolate</div>
      </div>
      <div class="login-card">
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
      </div>
      </div>
    </div>
    <div class="home-indicator"></div>
  </div>
</div>
<script>
function klok(){var d=new Date();var h=d.getHours(),m=d.getMinutes();
  document.getElementById('klok').textContent=h+':'+(m<10?'0':'')+m;}
function sizeDevice(){var d=document.querySelector('.device');if(!d)return;var r=9/16;var mh=window.innerHeight*0.97,mw=window.innerWidth*0.97;var h=Math.min(mh,940),w=h*r;if(w>mw){w=mw;h=w/r;}d.style.height=Math.round(h)+'px';d.style.width=Math.round(w)+'px';}
sizeDevice(); window.addEventListener('resize',sizeDevice);
klok(); setInterval(klok,10000);
function switchTab(t){
  document.getElementById('tab-login').classList.toggle('active', t==='login');
  document.getElementById('tab-register').classList.toggle('active', t==='register');
  document.getElementById('form-login').classList.toggle('hidden', t!=='login');
  document.getElementById('form-register').classList.toggle('hidden', t!=='register');
  document.getElementById('fout').style.display='none';
}
function toonFout(msg){var f=document.getElementById('fout');f.textContent=msg;f.style.display='block';}
async function doLogin(){
  var r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:document.getElementById('l-email').value,wachtwoord:document.getElementById('l-pass').value})});
  var d=await r.json(); if(d.ok){location.href='/';}else{toonFout(d.fout);}
}
async function doRegister(){
  var r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({naam:document.getElementById('r-naam').value,email:document.getElementById('r-email').value,wachtwoord:document.getElementById('r-pass').value})});
  var d=await r.json(); if(d.ok){location.href='/';}else{toonFout(d.fout);}
}
document.addEventListener('keydown',function(e){
  if(e.key==='Enter'){ if(document.getElementById('form-login').classList.contains('hidden')){doRegister();}else{doLogin();} }
});
</script>
</body>
</html>"""

# ===========================================================================
# FRONTEND: APP (single page met bottom navigation)
# ===========================================================================

APP_HTML = r"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Cacao Company</title>
<style>
""" + SHARED_CSS + r"""
/* Topbar */
.topbar{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  padding:6px 20px 16px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;
  box-shadow:0 8px 22px rgba(62,39,35,.18);position:relative;z-index:4}
.statusbar{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F3E7D2}
.statusbar .klok{color:#F8EFDD}
.topbar .titel{font-family:Georgia,serif;font-size:20px;letter-spacing:.4px}
.topbar .titel small{display:block;font-family:'Segoe UI',sans-serif;font-size:10px;letter-spacing:3px;
  color:var(--goud-licht);font-weight:700;text-transform:uppercase;margin-top:2px}
.bell{position:relative;font-size:20px;cursor:pointer;background:rgba(255,255,255,.12);
  width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.2s}
.bell:hover{background:rgba(255,255,255,.22)}
.badge{position:absolute;top:-3px;right:-3px;background:var(--goud);color:var(--bruin);
  font-size:11px;font-weight:700;min-width:19px;height:19px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;padding:0 5px;border:2px solid var(--bruin)}
#scherm{flex:1;min-width:0;overflow-y:auto;overflow-x:hidden;padding:18px 16px 22px;-webkit-overflow-scrolling:touch}
#scherm::-webkit-scrollbar{width:0}
/* Bottom nav */
.nav{display:flex;background:var(--wit);border-top:1px solid #EFE6D6;flex-shrink:0;
  padding-bottom:18px;box-shadow:0 -6px 20px rgba(62,39,35,.06)}
.nav button{flex:1;border:none;background:none;padding:10px 4px 6px;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--grijs-licht);
  font-size:10px;font-weight:600;transition:.2s}
.nav button .ico{font-size:20px;transition:transform .2s}
.nav button.active{color:var(--bruin)}
.nav button.active .ico{transform:translateY(-2px) scale(1.12)}
/* Componenten */
h2.sectie{font-family:Georgia,serif;font-size:18px;color:var(--bruin);margin:20px 4px 11px;font-weight:600}
h2.sectie:first-child{margin-top:2px}
.kaart{background:var(--wit);border-radius:20px;padding:15px;box-shadow:var(--kaart-schaduw);margin-bottom:12px}
.welkom{background:linear-gradient(135deg,#fff,#FBF3E3);border-radius:22px;padding:16px;
  box-shadow:var(--kaart-schaduw);margin-bottom:4px;border:1px solid #F1E6D0}
.welkom .hi{font-size:12px;color:var(--goud);font-weight:700;letter-spacing:1.6px;text-transform:uppercase}
.welkom .naam{font-family:Georgia,serif;font-size:24px;color:var(--bruin);margin-top:3px}
.welkom .sub{font-size:13px;color:var(--grijs);margin-top:7px;line-height:1.5}
.hscroll{display:flex;gap:12px;overflow-x:auto;padding:4px 4px 8px;scroll-snap-type:x mandatory}
.hscroll::-webkit-scrollbar{height:0}
.prodkaart{min-width:152px;width:152px;background:var(--wit);border-radius:20px;
  box-shadow:var(--kaart-schaduw);overflow:hidden;cursor:pointer;scroll-snap-align:start;
  transition:transform .18s;display:flex;flex-direction:column}
.prodkaart:active{transform:scale(.97)}
.prodkaart .beeld{aspect-ratio:1/1;width:100%;overflow:hidden}
.prodkaart .info{padding:11px 12px 13px;flex:1;display:flex;flex-direction:column}
.prodkaart .pn{font-size:13px;font-weight:700;color:var(--bruin);line-height:1.25}
.prodkaart .pp{font-size:15px;font-weight:700;color:var(--goud);margin-top:auto;padding-top:8px}
.cat-pill{display:inline-block;background:var(--creme);color:var(--bruin-2);font-size:10.5px;
  font-weight:600;padding:3px 9px;border-radius:8px;align-self:flex-start;margin-top:5px}
.li{display:flex;align-items:center;gap:13px;padding:12px 4px;border-bottom:1px solid #F1E9DB}
.li:last-child{border-bottom:none}
.li .ic{width:50px;height:50px;border-radius:15px;overflow:hidden;flex-shrink:0;box-shadow:0 3px 8px rgba(62,39,35,.10)}
.li .ic.plain{display:flex;align-items:center;justify-content:center;font-size:24px;
  background:linear-gradient(135deg,#F3E9D6,#EADFC6)}
.li .mid{flex:1;min-width:0}
.li .t{font-size:14px;font-weight:700;color:var(--bruin)}
.li .s{font-size:12.5px;color:var(--grijs);margin-top:2px}
.li .r{text-align:right;flex-shrink:0}
.status{font-size:11px;font-weight:700;padding:4px 10px;border-radius:9px;display:inline-block;white-space:nowrap}
.st-goed{background:#E7F0E6;color:var(--groen)}
.st-bijna{background:#FBEFDF;color:var(--oranje)}
.st-verlopen{background:#F7E3DF;color:var(--rood)}
.st-ontvangen{background:#E9EDF4;color:var(--blauw)}
.st-behandeling{background:#FBEFDF;color:var(--oranje)}
.st-opgelost{background:#E7F0E6;color:var(--groen)}
.st-verwerking{background:#FBEFDF;color:var(--oranje)}
.st-bezorgd{background:#E7F0E6;color:var(--groen)}
.st-geannuleerd{background:#F3E7E4;color:var(--rood)}
.btn{padding:15px;border:none;border-radius:15px;cursor:pointer;width:100%;
  background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  font-size:15px;font-weight:600;box-shadow:0 8px 20px rgba(62,39,35,.28);transition:transform .15s}
.btn:hover{transform:translateY(-2px)}
.btn:active{transform:translateY(0)}
.btn.goud{background:linear-gradient(135deg,var(--goud),#A8843A);color:#fff}
.btn.licht{background:var(--creme);color:var(--bruin);box-shadow:none;border:1.5px solid #E6DCC9}
.btn.rood-licht{background:#F7ECEA;color:var(--rood);box-shadow:none;border:1.5px solid #EAD2CC}
.btn.klein{width:auto;padding:9px 16px;font-size:13px;border-radius:12px}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
label{display:block;font-size:12.5px;font-weight:600;color:var(--bruin-2);margin:13px 0 6px}
input,select,textarea{width:100%;padding:13px 14px;border:1.5px solid #E6DCC9;border-radius:13px;
  font-size:15px;background:var(--wit);color:var(--tekst);outline:none;font-family:inherit;transition:.2s}
input:focus,select:focus,textarea:focus{border-color:var(--goud);box-shadow:0 0 0 3px rgba(194,162,76,.15)}
textarea{resize:vertical;min-height:90px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.chip{padding:8px 14px;border-radius:20px;border:1.5px solid #E6DCC9;background:var(--wit);
  font-size:13px;font-weight:600;color:var(--bruin-2);cursor:pointer;transition:.18s}
.chip.on{background:var(--bruin);color:#F8EFDD;border-color:var(--bruin)}
.overlay{position:absolute;inset:0;background:var(--creme-2);z-index:30;display:flex;flex-direction:column;
  border-radius:49px;overflow:hidden;animation:slide .25s ease}
@keyframes slide{from{transform:translateX(100%)}to{transform:translateX(0)}}
.ov-top{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;
  padding:46px 18px 16px;display:flex;align-items:center;gap:14px;flex-shrink:0}
.ov-top .back{font-size:22px;cursor:pointer;background:rgba(255,255,255,.12);width:38px;height:38px;
  border-radius:50%;display:flex;align-items:center;justify-content:center;transition:.2s}
.ov-top .back:hover{background:rgba(255,255,255,.22)}
.ov-top .titel{font-family:Georgia,serif;font-size:18px}
.ov-body{flex:1;overflow-y:auto;padding:18px 16px 30px}
.ov-body::-webkit-scrollbar{width:0}
.detail-hero{width:74%;max-width:236px;aspect-ratio:1/1;border-radius:24px;overflow:hidden;margin:0 auto 18px;box-shadow:0 14px 34px rgba(62,39,35,.16)}
.detail-naam{font-family:Georgia,serif;font-size:23px;color:var(--bruin)}
.detail-prijs{font-size:21px;font-weight:700;color:var(--goud);margin:6px 0}
.info-rij{padding:13px 0;border-bottom:1px solid #F1E9DB}
.info-rij .lbl{font-size:11.5px;font-weight:700;color:var(--goud);text-transform:uppercase;letter-spacing:.6px}
.info-rij .val{font-size:14px;color:var(--tekst);margin-top:4px;line-height:1.5}
.scanner{aspect-ratio:1;width:236px;max-width:72%;margin-left:auto;margin-right:auto;background:linear-gradient(160deg,#241612,#3E2723);border-radius:26px;
  position:relative;margin-bottom:18px;overflow:hidden;display:flex;align-items:center;justify-content:center}
.scan-frame{width:62%;aspect-ratio:1;position:relative}
.scan-frame span{position:absolute;width:34px;height:34px;border:3.5px solid var(--goud)}
.scan-frame .tl{top:0;left:0;border-right:none;border-bottom:none;border-radius:14px 0 0 0}
.scan-frame .tr{top:0;right:0;border-left:none;border-bottom:none;border-radius:0 14px 0 0}
.scan-frame .bl{bottom:0;left:0;border-right:none;border-top:none;border-radius:0 0 0 14px}
.scan-frame .br{bottom:0;right:0;border-left:none;border-top:none;border-radius:0 0 14px 0}
.scan-line{position:absolute;left:8%;right:8%;height:3px;background:linear-gradient(90deg,transparent,var(--goud),transparent);
  border-radius:3px;top:10%;animation:scan 2.4s ease-in-out infinite;box-shadow:0 0 12px var(--goud)}
@keyframes scan{0%,100%{top:12%}50%{top:84%}}
.scan-emoji{position:absolute;font-size:44px;opacity:.22}
.chat-wrap{display:flex;flex-direction:column;height:100%}
.chat-msgs{flex:1;overflow-y:auto;padding:6px 2px 12px;display:flex;flex-direction:column;gap:11px}
.chat-msgs::-webkit-scrollbar{width:0}
.bubble{max-width:80%;padding:12px 15px;border-radius:18px;font-size:14px;line-height:1.5;box-shadow:var(--kaart-schaduw)}
.bubble.bot{background:var(--wit);color:var(--tekst);align-self:flex-start;border-bottom-left-radius:5px}
.bubble.user{background:linear-gradient(135deg,var(--bruin),var(--bruin-3));color:#F8EFDD;align-self:flex-end;border-bottom-right-radius:5px}
.chat-quick{display:flex;gap:8px;overflow-x:auto;padding:8px 0}
.chat-quick::-webkit-scrollbar{height:0}
.chat-quick .chip{white-space:nowrap;flex-shrink:0}
.chat-input{display:flex;gap:9px;padding-top:10px;align-items:center}
.chat-input input{border-radius:24px}
.chat-input .send{width:48px;height:48px;flex-shrink:0;border:none;border-radius:50%;cursor:pointer;
  background:linear-gradient(135deg,var(--goud),#A8843A);color:#fff;font-size:19px;
  display:flex;align-items:center;justify-content:center;box-shadow:0 6px 16px rgba(194,162,76,.4)}
.cart-bar{position:sticky;bottom:0;background:var(--wit);border-radius:18px;padding:14px;
  box-shadow:0 -4px 20px rgba(62,39,35,.12);margin-top:8px;border:1px solid #F1E6D0}
.qty{display:flex;align-items:center;gap:11px}
.qty button{width:30px;height:30px;border-radius:9px;border:1.5px solid #E6DCC9;background:var(--wit);
  font-size:17px;font-weight:700;color:var(--bruin);cursor:pointer;line-height:1}
.qty .n{font-size:15px;font-weight:700;min-width:20px;text-align:center}
.notif{display:flex;gap:12px;padding:13px;border-radius:15px;margin-bottom:9px;background:var(--wit);box-shadow:var(--kaart-schaduw)}
.notif.unread{border-left:4px solid var(--goud)}
.notif .ni{font-size:22px}
.notif .nt{font-size:14px;font-weight:700;color:var(--bruin)}
.notif .nx{font-size:12.5px;color:var(--grijs);margin-top:3px;line-height:1.45}
.notif .nz{font-size:11px;color:var(--grijs-licht);margin-top:5px}
.leeg{text-align:center;color:var(--grijs);font-size:13.5px;padding:30px 10px;line-height:1.6}
.leeg .e{font-size:40px;display:block;margin-bottom:10px;opacity:.6}
.toast{position:absolute;left:50%;bottom:96px;transform:translateX(-50%);background:var(--bruin);
  color:#F8EFDD;padding:13px 22px;border-radius:30px;font-size:13.5px;font-weight:600;z-index:60;
  box-shadow:var(--schaduw);opacity:0;transition:opacity .3s,transform .3s;pointer-events:none;white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(-6px)}
.divider{height:1px;background:#EFE6D6;margin:18px 0}
.muted{font-size:12.5px;color:var(--grijs);line-height:1.5}
.row-between{display:flex;justify-content:space-between;align-items:center}
.totaal-rij{display:flex;justify-content:space-between;font-size:17px;font-weight:700;color:var(--bruin);
  padding:12px 0;border-top:2px solid #EFE6D6;margin-top:6px}

/* --- Icoonsysteem (premium, vector) --- */
.g-ic{display:block;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;width:23px;height:23px}
.nav button .ico{display:flex}
.bell{color:#F8EFDD}
.bell .g-ic{width:21px;height:21px}
.ov-top .back .g-ic{width:22px;height:22px}
.li .ic.plain{color:var(--bruin-3)}
.li .ic.plain .g-ic{width:24px;height:24px}
.li .r .g-ic{width:18px;height:18px;color:var(--grijs-licht)}
.notif .ni{width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#F4ECDB,#EADFC6);display:flex;align-items:center;justify-content:center;color:var(--bruin-3)}
.notif .ni .g-ic{width:21px;height:21px}
.leeg .e{color:var(--grijs-licht)}
.leeg .e .g-ic{width:46px;height:46px;margin:0 auto}
.inline-ic{display:inline-flex;vertical-align:-2px;margin-right:5px;color:var(--goud)}
.inline-ic.warn{color:var(--oranje)}
.inline-ic .g-ic{width:14px;height:14px}
.h-ic{display:inline-flex;vertical-align:-1px;color:var(--goud)}
.h-ic .g-ic{width:15px;height:15px}
.btn-ic{display:inline-flex;vertical-align:-3px;margin-right:6px}
.btn-ic .g-ic{width:16px;height:16px}
.scan-emoji{color:var(--goud)}
.scan-emoji .g-ic{width:46px;height:46px}
.chat-input .send .g-ic{width:20px;height:20px}
.big-ic{display:flex;justify-content:center;color:var(--goud);margin-bottom:6px}
.big-ic.ok{color:var(--groen)}
.big-ic .g-ic{width:58px;height:58px}
/* --- Home (iPhone-app stijl) --- */
.home-greet{margin:0 2px 14px}
.home-greet .hg-hi{font-size:11px;color:var(--goud);font-weight:700;letter-spacing:1.6px;text-transform:uppercase}
.home-greet .hg-name{font-family:Georgia,serif;font-size:25px;color:var(--bruin);margin-top:3px}
.home-greet .hg-sub{font-size:12.5px;color:var(--grijs);margin-top:3px}
.qa{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-bottom:8px}
.qa .tile{background:var(--wit);border-radius:18px;padding:12px 4px 10px;box-shadow:var(--kaart-schaduw);display:flex;flex-direction:column;align-items:center;gap:7px;cursor:pointer;transition:transform .15s}
.qa .tile:active{transform:scale(.95)}
.qa .tile .tic{width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,#F4ECDB,#EADFC6);display:flex;align-items:center;justify-content:center;color:var(--bruin-3)}
.qa .tile .tic .g-ic{width:21px;height:21px}
.qa .tile .tl{font-size:10px;font-weight:600;color:var(--bruin-2);text-align:center;line-height:1.2}
.alert-card{background:linear-gradient(135deg,#FBEFDF,#F6E4CC);border-radius:18px;padding:13px 14px;display:flex;align-items:center;gap:12px;cursor:pointer;border:1px solid #F0DBBE;box-shadow:var(--kaart-schaduw)}
.alert-card .ai{color:var(--oranje);flex-shrink:0;display:flex}
.alert-card .ai .g-ic{width:24px;height:24px}
.alert-card .ach{color:var(--oranje);display:flex}
.alert-card .ach .g-ic{width:18px;height:18px}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.stat{background:var(--wit);border-radius:18px;padding:14px 15px;box-shadow:var(--kaart-schaduw);cursor:pointer;position:relative;overflow:hidden}
.stat .si{position:absolute;top:12px;right:12px;color:var(--goud);opacity:.75;display:flex}
.stat .si .g-ic{width:20px;height:20px}
.stat .sv{font-family:Georgia,serif;font-size:27px;color:var(--bruin);font-weight:700;line-height:1}
.stat .sl{font-size:11.5px;color:var(--grijs);margin-top:4px}
</style>
</head>
<body>
<div class="device">
 <div class="screen">

  <div class="statusbar">
    <span class="klok" id="klok">9:41</span>
    <span class="icons">
      <svg width="18" height="12" viewBox="0 0 18 12"><rect x="0" y="7" width="3" height="5" rx="1" fill="#F8EFDD"/><rect x="5" y="4.5" width="3" height="7.5" rx="1" fill="#F8EFDD"/><rect x="10" y="2" width="3" height="10" rx="1" fill="#F8EFDD"/><rect x="15" y="0" width="3" height="12" rx="1" fill="#F8EFDD"/></svg>
      <svg width="17" height="12" viewBox="0 0 17 12"><path d="M8.5 2.5c2.6 0 5 1 6.8 2.7l1.4-1.5C14.5 1.4 11.6 0 8.5 0S2.5 1.4 0 3.7l1.4 1.5C3.1 3.5 5.5 2.5 8.5 2.5z" fill="#F8EFDD"/><path d="M8.5 6c1.5 0 2.9.6 3.9 1.6l1.4-1.5C12.4 4.8 10.5 4 8.5 4s-3.9.8-5.3 2.1l1.4 1.5C5.6 6.6 7 6 8.5 6z" fill="#F8EFDD"/><circle cx="8.5" cy="10.2" r="1.8" fill="#F8EFDD"/></svg>
      <svg width="26" height="13" viewBox="0 0 26 13"><rect x="0.5" y="0.5" width="22" height="12" rx="3.5" fill="none" stroke="#F8EFDD" stroke-opacity=".6"/><rect x="2.5" y="2.5" width="16" height="8" rx="1.5" fill="#F8EFDD"/><rect x="24" y="4" width="2" height="5" rx="1" fill="#F8EFDD" fill-opacity=".6"/></svg>
    </span>
  </div>
  <div class="topbar">
    <div class="titel">Cacao Company<small>Premium Chocolate</small></div>
    <div class="bell" onclick="openNotificaties()"><svg class="g-ic" viewBox="0 0 24 24"><path d="M6 9.5a6 6 0 0 1 12 0c0 4.5 2 5.5 2 5.5H4s2-1 2-5.5z"/><path d="M10 18.5a2 2 0 0 0 4 0"/></svg><span id="notif-badge" class="badge" style="display:none">0</span></div>
  </div>
  <div id="scherm"></div>
  <div class="nav">
    <button id="nav-home" onclick="gaNaar('home')"><span class="ico"><svg class="g-ic" viewBox="0 0 24 24"><path d="M3.5 11.5 12 4.5l8.5 7"/><path d="M5.5 10.2V19.5h13V10.2"/><path d="M10 19.5v-5h4v5"/></svg></span>Home</button>
    <button id="nav-scan" onclick="gaNaar('scan')"><span class="ico"><svg class="g-ic" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="3"/><path d="M8.5 7 10 4.5h4L15.5 7"/><circle cx="12" cy="13.5" r="3.3"/></svg></span>Scan</button>
    <button id="nav-chat" onclick="gaNaar('chat')"><span class="ico"><svg class="g-ic" viewBox="0 0 24 24"><path d="M20 13.5a2.5 2.5 0 0 1-2.5 2.5H10l-4 3.2V16H6.5A2.5 2.5 0 0 1 4 13.5v-6A2.5 2.5 0 0 1 6.5 5h11A2.5 2.5 0 0 1 20 7.5z"/></svg></span>Assistent</button>
    <button id="nav-shop" onclick="gaNaar('shop')"><span class="ico"><svg class="g-ic" viewBox="0 0 24 24"><path d="M6 8h12l-1 11.5H7z"/><path d="M9 8V6.8a3 3 0 0 1 6 0V8"/></svg></span>Shop</button>
    <button id="nav-profiel" onclick="gaNaar('profiel')"><span class="ico"><svg class="g-ic" viewBox="0 0 24 24"><circle cx="12" cy="8.5" r="3.6"/><path d="M5.5 19.5a6.5 6.5 0 0 1 13 0"/></svg></span>Profiel</button>
  </div>
  <div id="overlay-host"></div>
  <div id="toast" class="toast"></div>
  <div class="home-indicator"></div>
 </div>
</div>

<script>
/* ============== STATE ============== */
var STATE=null, TAB='home', CART={}, CHAT=[];

/* ============== ICOONSYSTEEM (premium vector, vervangt emoji) ============== */
var ICONP={
 box:'<path d="M4 8.3 12 4.8l8 3.5v7.4L12 19.2l-8-3.5z"/><path d="M4 8.3 12 11.8l8-3.5"/><path d="M12 11.8v7.4"/>',
 bag:'<path d="M6 8h12l-1 11.5H7z"/><path d="M9 8V6.8a3 3 0 0 1 6 0V8"/>',
 cart:'<circle cx="9.5" cy="19" r="1.4"/><circle cx="16.5" cy="19" r="1.4"/><path d="M3.5 5h2l2.2 9.5h9.3L19 8H7.2"/>',
 card:'<rect x="3" y="6" width="18" height="12" rx="2.6"/><path d="M3 10h18"/><path d="M6.5 14.5h4"/>',
 doc:'<path d="M7 4h7l4 4v12H7z"/><path d="M13.8 4v4.2H18"/><path d="M9.5 12.5h6M9.5 15.5h6"/>',
 clipboard:'<rect x="6" y="5" width="12" height="15" rx="2.2"/><rect x="9" y="3.4" width="6" height="3.4" rx="1.2"/><path d="M9.5 11.5h5M9.5 14.5h3.5"/>',
 gear:'<circle cx="12" cy="12" r="3"/><path d="M12 4v2.4M12 17.6V20M4 12h2.4M17.6 12H20M6.2 6.2 7.9 7.9M16.1 16.1 17.8 17.8M17.8 6.2 16.1 7.9M7.9 16.1 6.2 17.8"/>',
 bell:'<path d="M6 9.5a6 6 0 0 1 12 0c0 4.5 2 5.5 2 5.5H4s2-1 2-5.5z"/><path d="M10 18.5a2 2 0 0 0 4 0"/>',
 mail:'<rect x="3" y="6" width="18" height="12" rx="2.6"/><path d="M4 7.5 12 13l8-5.5"/>',
 pin:'<path d="M12 20.5s5.5-5 5.5-9.5a5.5 5.5 0 0 0-11 0c0 4.5 5.5 9.5 5.5 9.5z"/><circle cx="12" cy="11" r="2.2"/>',
 globe:'<circle cx="12" cy="12" r="8.4"/><path d="M3.6 12h16.8"/><path d="M12 3.6c2.6 2.4 2.6 14.4 0 16.8M12 3.6c-2.6 2.4-2.6 14.4 0 16.8"/>',
 alert:'<path d="M12 4.5 20.5 19H3.5z"/><path d="M12 10v4.3"/><path d="M12 16.7v.2"/>',
 sparkle:'<path d="M12 4.5l1.5 4.6 4.6 1.5-4.6 1.5L12 16.7l-1.5-4.6L5.9 10.6l4.6-1.5z"/><path d="M18.5 4.5l.6 1.8 1.8.6-1.8.6-.6 1.8-.6-1.8-1.8-.6 1.8-.6z"/>',
 clock:'<circle cx="12" cy="12" r="8.4"/><path d="M12 7.4V12l3.2 2"/>',
 search:'<circle cx="11" cy="11" r="6.4"/><path d="M15.8 15.8 20 20"/>',
 send:'<path d="M20.5 4 9.8 14.7"/><path d="M20.5 4 14 20l-4.2-7.3L3 8.5z"/>',
 lock:'<rect x="5.5" y="10.5" width="13" height="9" rx="2.2"/><path d="M8.4 10.5V8a3.6 3.6 0 0 1 7.2 0v2.5"/>',
 clip:'<path d="M16 8.5 9.5 15a2.5 2.5 0 0 1-3.5-3.5l7-7a4 4 0 0 1 5.6 5.6l-7.2 7.2a5.5 5.5 0 0 1-7.8-7.8l6.8-6.8"/>',
 camera:'<rect x="3" y="7" width="18" height="13" rx="3"/><path d="M8.5 7 10 4.5h4L15.5 7"/><circle cx="12" cy="13.5" r="3.3"/>',
 'check-circle':'<circle cx="12" cy="12" r="8.5"/><path d="M8 12.4 10.7 15 16 9.5"/>',
 chevR:'<path d="M9.5 5.5 15.5 12l-6 6.5"/>',
 chevL:'<path d="M14.5 5.5 8.5 12l6 6.5"/>'
};
function ic(n){return '<svg class="g-ic" viewBox="0 0 24 24">'+(ICONP[n]||'')+'</svg>';}
function inlineIc(n,c){return '<span class="inline-ic'+(c?' '+c:'')+'">'+ic(n)+'</span>';}
function hIc(n){return ' <span class="h-ic">'+ic(n)+'</span>';}
function btnIc(n){return '<span class="btn-ic">'+ic(n)+'</span>';}


/* ============== PRODUCTILLUSTRATIES (1 huisstijl, vector) ============== */
/* Per chocoladesoort een kleurpalet; per product een subtiele garnering,
   zodat elk product herkenbaar is maar alles dezelfde stijl houdt. */
var CAT={
  'Puur':   {bar:'#43291c',barL:'#5a3a28',sq:'#311d12',edge:'#caa75e',bg1:'#f1e6cf',bg2:'#e4d2ab',pod:'#b8893f'},
  'Melk':   {bar:'#7c5230',barL:'#956840',sq:'#5f3d22',edge:'#caa75e',bg1:'#f3e7d2',bg2:'#ecd7b4',pod:'#b8893f'},
  'Wit':    {bar:'#ecdcb4',barL:'#f6e9c9',sq:'#dcc795',edge:'#d8c389',bg1:'#f7f0de',bg2:'#efe1c4',pod:'#c3a55a'},
  'Ruby':   {bar:'#c06f7e',barL:'#d18a96',sq:'#a85365',edge:'#caa75e',bg1:'#f5e2e4',bg2:'#eccdd1',pod:'#b8893f'},
  'Vegan':  {bar:'#6e4a2c',barL:'#866038',sq:'#543820',edge:'#8aa55e',bg1:'#eee8d2',bg2:'#e1d8b2',pod:'#7f9a52'},
  'Caramel':{bar:'#a9712e',barL:'#c08a40',sq:'#875829',edge:'#caa75e',bg1:'#f4e6c9',bg2:'#edd5a3',pod:'#b8893f'},
  'Praline':{bar:'#8a5a33',barL:'#a06f42',sq:'#6c4526',edge:'#caa75e',bg1:'#f1e3c8',bg2:'#e7d1a4',pod:'#b8893f'}
};
/* Specifieke afwijking voor donkerdere reep (85%) */
var CODECOLOR={'CACAO-003':{bar:'#35211a',barL:'#492f24',sq:'#261511'}};
/* Cacao-% voor de etiketten + garnering (smaakaccent) per product */
var PCT={'CACAO-001':'72% CACAO','CACAO-003':'85% CACAO'};
var GARNISH={
  'CACAO-004':['dots','#fbf6ea'],   /* zeezout  */
  'CACAO-005':['dots','#c0405a'],   /* framboos */
  'CACAO-008':['dots','#7a9a4e'],   /* pistache */
  'CACAO-006':['leaf'],             /* vegan    */
  'CACAO-007':['nut']               /* hazelnoot*/
};
/* Genereert per product een premium verpakking/wikkel in 1 vaste huisstijl:
   foil met sheen, gecrimpte randen, cremekleurig etiket met merk, soort en %. */
function prodImg(p){
  var c=Object.assign({},CAT[p.categorie]||CAT['Puur'], CODECOLOR[p.code]||{});
  var id='G'+p.code.replace(/[^A-Za-z0-9]/g,'');
  var ink='#4a2e20';
  var s='<svg viewBox="0 0 120 120" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block">';
  s+='<defs>'+
     '<linearGradient id="'+id+'bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="'+c.bg1+'"/><stop offset="1" stop-color="'+c.bg2+'"/></linearGradient>'+
     '<linearGradient id="'+id+'f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="'+c.sq+'"/><stop offset=".18" stop-color="'+c.bar+'"/><stop offset=".44" stop-color="'+c.barL+'"/><stop offset=".56" stop-color="'+c.barL+'"/><stop offset=".82" stop-color="'+c.bar+'"/><stop offset="1" stop-color="'+c.sq+'"/></linearGradient>'+
     '<linearGradient id="'+id+'sh" x1="0" y1="0" x2="0.7" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".30"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>'+
     '</defs>';
  s+='<rect width="120" height="120" fill="url(#'+id+'bg)"/>';
  s+='<ellipse cx="60" cy="103" rx="27" ry="4.5" fill="#000" opacity=".13"/>';
  /* kortere, iets bredere wikkel */
  s+='<rect x="39" y="24" width="42" height="76" rx="7" fill="url(#'+id+'f)" stroke="'+c.edge+'" stroke-width="1"/>';
  function crimp(y){var r='<rect x="39" y="'+y+'" width="42" height="6" fill="'+c.sq+'" opacity=".5"/>';
    for(var x=41;x<81;x+=3){r+='<line x1="'+x+'" y1="'+y+'" x2="'+x+'" y2="'+(y+6)+'" stroke="'+c.bg1+'" stroke-opacity=".20" stroke-width=".7"/>';} return r;}
  s+=crimp(24)+crimp(94);
  s+='<g transform="translate(60,38)"><path d="M0,-6 C2.9,-3.8 2.9,3.8 0,6 C-2.9,3.8 -2.9,-3.8 0,-6 Z" fill="'+c.pod+'"/><path d="M0,-5 L0,5 M-1.5,-4 L-1.5,4 M1.5,-4 L1.5,4" stroke="#fff" stroke-opacity=".35" stroke-width=".5" fill="none"/></g>';
  s+='<rect x="35" y="48" width="50" height="30" rx="4" fill="#F8F0E0" stroke="'+c.edge+'" stroke-width="1"/>';
  s+='<text x="60" y="56" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="3.4" letter-spacing="1.2" font-weight="700" fill="'+c.pod+'">CACAO CO.</text>';
  s+='<text x="60" y="67" text-anchor="middle" font-family="Georgia,serif" font-size="7.5" font-weight="700" fill="'+ink+'">'+(p.categorie||'').toUpperCase()+'</text>';
  s+='<line x1="48" y1="71" x2="72" y2="71" stroke="'+c.pod+'" stroke-width=".8"/>';
  s+='<text x="60" y="76" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="3.4" letter-spacing="1" fill="#8a7a6a">'+(PCT[p.code]||'FIJNE CHOCOLADE')+'</text>';
  var g=GARNISH[p.code];
  if(g&&g[0]==='dots'){ [[50,85,1.5],[60,88,1.4],[70,85,1.5],[60,90.5,1.2]].forEach(function(d){ s+='<circle cx="'+d[0]+'" cy="'+d[1]+'" r="'+d[2]+'" fill="'+g[1]+'"/>'; }); }
  else if(g&&g[0]==='leaf'){ s+='<path d="M60,82 C55,82.5 53,87 60,90 C61,86 64,83.5 60,82 Z" fill="#8aa55e"/>'; }
  else if(g&&g[0]==='nut'){ s+='<circle cx="60" cy="86" r="3.6" fill="#8a5a33" stroke="#6c4426" stroke-width=".7"/><path d="M60 82.8 L60 89.2" stroke="#6c4426" stroke-width=".5"/>'; }
  s+='<rect x="39" y="24" width="42" height="76" rx="7" fill="url(#'+id+'sh)"/>';
  s+='<rect x="41.5" y="32" width="1.6" height="60" rx="1" fill="#fff" opacity=".10"/>';
  s+='</svg>';
  return s;
}

/* ============== HELPERS ============== */
function euro(n){return 'EUR '+n.toFixed(2).replace('.',',');}
function el(id){return document.getElementById(id);}
function esc(s){var d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML;}
function statusClass(s){var m={'Goed':'st-goed','Bijna verlopen':'st-bijna','Verlopen':'st-verlopen',
  'Ontvangen':'st-ontvangen','In behandeling':'st-behandeling','Opgelost':'st-opgelost',
  'In verwerking':'st-verwerking','Bezorgd':'st-bezorgd','Geannuleerd':'st-geannuleerd'};return m[s]||'st-ontvangen';}
function toast(msg){var t=el('toast');t.textContent=msg;t.classList.add('show');
  clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove('show');},2200);}
async function api(url,body){var opt={headers:{'Content-Type':'application/json'}};
  if(body!==undefined){opt.method='POST';opt.body=JSON.stringify(body);}
  var r=await fetch(url,opt); if(r.status===401){location.href='/';return {ok:false};} return await r.json();}
async function laadState(){var d=await api('/api/state');if(d.ok){STATE=d;updateBadge();}return d;}
function updateBadge(){if(!STATE)return;var n=STATE.notifications.filter(function(x){return !x.gelezen;}).length;
  var b=el('notif-badge');if(n>0){b.textContent=n;b.style.display='flex';}else{b.style.display='none';}}
function cartCount(){var s=0;for(var k in CART){s+=CART[k];}return s;}
function cartTotaal(){var s=0;for(var k in CART){var p=prodByCode(k);if(p)s+=p.prijs*CART[k];}return s;}
function prodByCode(c){return STATE.products.filter(function(p){return p.code===c;})[0];}
function klok(){var d=new Date();var h=d.getHours(),m=d.getMinutes();var e=el('klok');if(e)e.textContent=h+':'+(m<10?'0':'')+m;}

/* ============== NAVIGATIE ============== */
function gaNaar(tab){TAB=tab;sluitOverlay();
  ['home','scan','chat','shop','profiel'].forEach(function(t){el('nav-'+t).classList.toggle('active',t===tab);});
  el('scherm').style.padding = (tab==='chat') ? '12px 16px 16px' : '18px 16px 22px';
  render();}
function render(){if(TAB==='home')renderHome();else if(TAB==='scan')renderScan();
  else if(TAB==='chat')renderChat();else if(TAB==='shop')renderShop();else if(TAB==='profiel')renderProfiel();}

/* ============== OVERLAY ============== */
function openOverlay(titel,bodyHTML){el('overlay-host').innerHTML=
  '<div class="overlay"><div class="ov-top"><div class="back" onclick="sluitOverlay()">'+ic("chevL")+'</div>'+
  '<div class="titel">'+titel+'</div></div><div class="ov-body" id="ov-body">'+bodyHTML+'</div></div>';}
function sluitOverlay(){el('overlay-host').innerHTML='';}

/* ============== HOME ============== */
function renderHome(){
  var s=STATE, voornaam=(s.account.naam||'').split(' ')[0]||'klant';
  var datum=new Date().toLocaleDateString('nl-NL',{weekday:'long',day:'numeric',month:'long'});
  datum=datum.charAt(0).toUpperCase()+datum.slice(1);
  var h='';
  /* groet */
  h+='<div class="home-greet"><div class="hg-hi">Welkom terug</div>'+
     '<div class="hg-name">Hallo, '+esc(voornaam)+'</div>'+
     '<div class="hg-sub">'+esc(datum)+'</div></div>';
  /* attentie: bijna verlopen */
  if(s.bijna_verlopen.length){
    h+='<div class="alert-card" onclick="openCollectie()"><div class="ai">'+ic('clock')+'</div>'+
       '<div style="flex:1"><div style="font-weight:700;color:var(--bruin);font-size:14px">'+s.bijna_verlopen.length+' product'+(s.bijna_verlopen.length===1?'':'en')+' bijna verlopen</div>'+
       '<div class="muted">Bekijk je collectie</div></div><div class="ach">'+ic('chevR')+'</div></div>';
  }
  /* aanbevelingen */
  h+='<h2 class="sectie">Aanbevolen voor jou'+hIc('sparkle')+'</h2><div class="hscroll">';
  s.recommendations.forEach(function(p){h+=prodCardHTML(p);}); h+='</div>';
  /* overzicht in cijfers */
  h+='<div class="stats" style="margin-top:6px">'+
     '<div class="stat" onclick="openCollectie()"><div class="si">'+ic('box')+'</div><div class="sv">'+s.registered.length+'</div><div class="sl">In mijn collectie</div></div>'+
     '<div class="stat" onclick="openOrders()"><div class="si">'+ic('bag')+'</div><div class="sv">'+s.orders.length+'</div><div class="sl">Bestellingen</div></div></div>';
  /* recente bestelling */
  h+='<div class="row-between" style="margin:20px 4px 11px"><h2 class="sectie" style="margin:0">Recente bestelling</h2>';
  if(s.orders.length) h+='<span class="muted" style="cursor:pointer;color:var(--goud)" onclick="openOrders()">Alles</span>';
  h+='</div>';
  if(s.orders.length){
    var o=s.orders[0];
    h+='<div class="kaart li" onclick="openOrder(\''+o.id+'\')"><div class="ic plain">'+ic('box')+'</div>'+
       '<div class="mid"><div class="t">'+esc(o.id)+'</div><div class="s">'+esc(o.datum)+' \u00B7 '+euro(o.totaal)+'</div></div>'+
       '<div class="r"><span class="status '+statusClass(o.status)+'">'+o.status+'</span></div></div>';
  }else{
    h+='<div class="kaart"><div class="leeg"><span class="e">'+ic('bag')+'</span>Nog geen bestellingen. Bekijk de shop voor onze repen.</div></div>';
  }
  el('scherm').innerHTML=h;
}
function qaTile(icon,label,action){
  return '<div class="tile" onclick="'+action+'"><div class="tic">'+ic(icon)+'</div><div class="tl">'+label+'</div></div>';
}
function prodCardHTML(p){
  return '<div class="prodkaart" onclick="openProduct(\''+p.code+'\')">'+
    '<div class="beeld">'+prodImg(p)+'</div><div class="info">'+
    '<div class="pn">'+esc(p.naam)+'</div><span class="cat-pill">'+esc(p.categorie)+'</span>'+
    '<div class="pp">'+euro(p.prijs)+'</div></div></div>';
}
function notifHTML(n){
  var map={'bestelling':'box','klacht':'doc','houdbaarheid':'clock','aanbeveling':'sparkle'};
  var ico=ic(map[n.type]||'bell');
  return '<div class="notif '+(n.gelezen?'':'unread')+'"><div class="ni">'+ico+'</div>'+
    '<div><div class="nt">'+esc(n.titel)+'</div><div class="nx">'+esc(n.tekst)+'</div><div class="nz">'+esc(n.tijd)+'</div></div></div>';
}

/* ============== NOTIFICATIES ============== */
async function openNotificaties(){
  var h='';
  if(STATE.notifications.length){STATE.notifications.forEach(function(n){h+=notifHTML(n);});}
  else{h='<div class="leeg"><span class="e">'+ic("bell")+'</span>Je hebt nog geen notificaties.</div>';}
  openOverlay('Notificaties',h); await api('/api/notifications/read',{}); await laadState();
}

/* ============== PRODUCTDETAIL ============== */
function openProduct(code){
  var p=prodByCode(code); if(!p)return;
  var inCollectie=STATE.registered.some(function(r){return r.code===code;});
  var h='<div class="detail-hero">'+prodImg(p)+'</div>'+
    '<div class="cat-pill">'+esc(p.categorie)+'</div>'+
    '<div class="detail-naam">'+esc(p.naam)+'</div>'+
    '<div class="detail-prijs">'+euro(p.prijs)+'</div>'+
    '<div class="muted" style="margin-bottom:8px">'+esc(p.beschrijving)+'</div>'+
    '<div class="info-rij"><div class="lbl">Herkomst</div><div class="val">'+inlineIc("globe")+' '+esc(p.herkomst)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Ingredienten</div><div class="val">'+esc(p.ingredienten)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Allergenen</div><div class="val">'+inlineIc("alert","warn")+' '+esc(p.allergenen)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Houdbaarheid</div><div class="val">'+esc(p.houdbaarheid)+'</div></div>'+
    '<div style="margin-top:20px;display:flex;flex-direction:column;gap:10px">';
  if(inCollectie){h+='<button class="btn licht" disabled>\u2713 In je collectie</button>';h+='<button class="btn rood-licht" onclick="verwijderUitCollectie(\''+code+'\')">Verwijderen uit collectie</button>';}
  else{h+='<button class="btn goud" onclick="registreerProduct(\''+code+'\')">+ Toevoegen aan collectie</button>';}
  h+='<button class="btn" onclick="voegToeAanCart(\''+code+'\');toast(\'Toegevoegd aan winkelwagen\')">In winkelwagen \u2013 '+euro(p.prijs)+'</button></div>';
  openOverlay('Productinformatie',h);
}
async function registreerProduct(code){var d=await api('/api/register-product',{code:code});
  if(d.ok){toast('Toegevoegd aan je collectie');await laadState();openProduct(code);}else toast(d.fout);}

/* ============== SCAN ============== */
function renderScan(){
  var h='<div class="scanner"><div class="scan-emoji">'+ic("camera")+'</div>'+
    '<div class="scan-frame"><span class="tl"></span><span class="tr"></span><span class="bl"></span><span class="br"></span><div class="scan-line"></div></div></div>'+
    '<div class="muted" style="text-align:center;margin-bottom:14px">Richt de camera op de QR-code van je reep, of voer de code hieronder handmatig in.</div>'+
    '<label>Productcode</label>'+
    '<input id="scan-code" placeholder="bijv. CACAO-001" style="text-transform:uppercase" onkeydown="if(event.key===\'Enter\')doScan()">'+
    '<div id="scan-fout" style="color:var(--rood);font-size:13px;margin-top:8px;display:none"></div>'+
    '<button class="btn goud" style="margin-top:16px" onclick="doScan()">'+btnIc("search")+'Scan / Zoek product</button>'+
    '<div id="scan-resultaat" style="margin-top:18px"></div>'+
    '<div class="divider"></div>'+
    '<button class="btn licht" onclick="toggleProductLijst()">'+btnIc("box")+'Kies een product uit de lijst</button>'+
    '<div id="prod-lijst" style="margin-top:14px;display:none"></div>';
  el('scherm').innerHTML=h;
}
async function doScan(){
  var code=el('scan-code').value.trim().toUpperCase(),foutEl=el('scan-fout');
  foutEl.style.display='none'; el('scan-resultaat').innerHTML='';
  if(!code){foutEl.textContent='Voer een productcode in.';foutEl.style.display='block';return;}
  var d=await api('/api/scan',{code:code});
  if(!d.ok){foutEl.textContent=d.fout;foutEl.style.display='block';return;}
  var p=d.product,inCollectie=STATE.registered.some(function(r){return r.code===p.code;});
  var h='<div class="kaart"><div class="li" style="border:none;padding:0 0 12px">'+
    '<div class="ic" style="width:62px;height:62px">'+prodImg(p)+'</div>'+
    '<div class="mid"><div class="t" style="font-size:16px">'+esc(p.naam)+'</div><div class="s">'+esc(p.categorie)+' &middot; '+euro(p.prijs)+'</div></div></div>'+
    '<div class="info-rij"><div class="lbl">Herkomst</div><div class="val">'+inlineIc("globe")+' '+esc(p.herkomst)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Ingredienten</div><div class="val">'+esc(p.ingredienten)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Allergenen</div><div class="val">'+inlineIc("alert","warn")+' '+esc(p.allergenen)+'</div></div>'+
    '<div class="info-rij" style="border:none"><div class="lbl">Houdbaarheid</div><div class="val">'+esc(p.houdbaarheid)+'</div></div>';
  if(inCollectie){h+='<button class="btn licht" style="margin-top:14px" disabled>\u2713 Al in je collectie</button>';}
  else{h+='<button class="btn goud" style="margin-top:14px" onclick="registreerVanuitScan(\''+p.code+'\')">+ Toevoegen aan collectie</button>';}
  h+='</div>'; el('scan-resultaat').innerHTML=h;
}
async function registreerVanuitScan(code){var d=await api('/api/register-product',{code:code});
  if(d.ok){toast('Toegevoegd aan je collectie');await laadState();doScan();}else toast(d.fout);}

/* ============== CHAT ============== */
function renderChat(){
  if(CHAT.length===0){CHAT.push({rol:'bot',tekst:'Hallo! Ik ben de Cacao Company assistent. Waarmee kan ik je helpen?'});}
  var quick=['Allergenen','Houdbaarheid','Bestelling','Klacht indienen','Herkomst cacao'];
  var h='<div class="chat-wrap"><div class="chat-msgs" id="chat-msgs"></div><div class="chat-quick">';
  quick.forEach(function(q){h+='<div class="chip" onclick="stuurChat(\''+q+'\')">'+q+'</div>';});
  h+='</div><div class="chat-input"><input id="chat-in" placeholder="Typ je vraag..." onkeydown="if(event.key===\'Enter\')stuurChat()"><button class="send" onclick="stuurChat()">'+ic("send")+'</button></div></div>';
  el('scherm').innerHTML=h; tekenChat();
}
function tekenChat(){var c=el('chat-msgs');if(!c)return;
  c.innerHTML=CHAT.map(function(m){return '<div class="bubble '+(m.rol==='user'?'user':'bot')+'">'+esc(m.tekst)+'</div>';}).join('');
  c.scrollTop=c.scrollHeight;}
async function stuurChat(tekst){
  var inp=el('chat-in'),bericht=tekst!==undefined?tekst:(inp?inp.value.trim():'');
  if(!bericht)return; if(inp)inp.value='';
  CHAT.push({rol:'user',tekst:bericht}); tekenChat();
  var d=await api('/api/chat',{message:bericht});
  CHAT.push({rol:'bot',tekst:d.ok?d.antwoord:'Er ging iets mis. Probeer het opnieuw.'}); tekenChat();
}

/* ============== SHOP ============== */
function renderShop(){
  var s=STATE,h='<h2 class="sectie">Ons assortiment</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">';
  s.products.forEach(function(p){
    h+='<div class="prodkaart" style="min-width:0;width:auto" onclick="openProduct(\''+p.code+'\')">'+
      '<div class="beeld">'+prodImg(p)+'</div><div class="info">'+
      '<div class="pn">'+esc(p.naam)+'</div><span class="cat-pill">'+esc(p.categorie)+'</span>'+
      '<div class="pp">'+euro(p.prijs)+'</div>'+
      '<button class="btn klein goud" style="width:100%;margin-top:9px" onclick="event.stopPropagation();voegToeAanCart(\''+p.code+'\')">In mandje</button>'+
      '</div></div>';
  });
  h+='</div>'; el('scherm').innerHTML=h; toonCartBalk();
}
function voegToeAanCart(code){CART[code]=(CART[code]||0)+1;toast('Toegevoegd aan winkelwagen');if(TAB==='shop')toonCartBalk();}
function toonCartBalk(){
  var b=el('cart-balk');if(b)b.remove(); var n=cartCount();if(n===0)return;
  var div=document.createElement('div');div.id='cart-balk';div.className='cart-bar';
  div.innerHTML='<div class="row-between"><div><div style="font-weight:700;color:var(--bruin)">'+n+' artikel'+(n===1?'':'en')+
    '</div><div class="muted">'+euro(cartTotaal())+'</div></div>'+
    '<button class="btn klein goud" onclick="openWinkelwagen()">Naar winkelwagen \u2192</button></div>';
  el('scherm').appendChild(div);
}

/* ============== WINKELWAGEN & CHECKOUT ============== */
function openWinkelwagen(){
  if(cartCount()===0){toast('Je winkelwagen is leeg');return;}
  var h='';
  for(var code in CART){var p=prodByCode(code);if(!p)continue;
    h+='<div class="kaart li" style="cursor:default"><div class="ic">'+prodImg(p)+'</div>'+
      '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+euro(p.prijs)+' per stuk</div></div>'+
      '<div class="qty"><button onclick="wijzigCart(\''+code+'\',-1)">\u2212</button>'+
      '<span class="n" id="q-'+code+'">'+CART[code]+'</span><button onclick="wijzigCart(\''+code+'\',1)">+</button></div></div>';
  }
  h+='<div class="kaart"><div class="totaal-rij" style="border:none;padding:0"><span>Totaal</span><span id="cart-totaal">'+euro(cartTotaal())+'</span></div></div>'+
     '<button class="btn goud" onclick="openCheckout()">Bestelling controleren \u2192</button>';
  openOverlay('Winkelwagen',h);
}
function wijzigCart(code,delta){CART[code]=(CART[code]||0)+delta;if(CART[code]<=0)delete CART[code];
  if(cartCount()===0){sluitOverlay();if(TAB==='shop')toonCartBalk();toast('Winkelwagen geleegd');return;}openWinkelwagen();}
function openCheckout(){
  var adres=STATE._adres||'',h='<h2 class="sectie" style="margin-top:0">Bezorgadres</h2>'+
    '<input id="co-adres" placeholder="Straat, postcode, plaats" value="'+esc(adres)+'">'+
    '<h2 class="sectie">Overzicht</h2><div class="kaart">';
  for(var code in CART){var p=prodByCode(code);if(!p)continue;
    h+='<div class="li" style="padding:9px 0"><div class="mid"><div class="t" style="font-size:14px">'+CART[code]+'\u00D7 '+esc(p.naam)+'</div></div>'+
      '<div class="r" style="font-weight:700;color:var(--bruin)">'+euro(p.prijs*CART[code])+'</div></div>';}
  var verzend=cartTotaal()>=25?0:3.95;
  h+='<div class="li" style="padding:9px 0;border-top:1px solid #F1E9DB"><div class="mid"><div class="s">Verzendkosten'+
    (verzend===0?' (gratis vanaf EUR 25)':'')+'</div></div><div class="r" style="font-weight:700;color:var(--bruin)">'+
    (verzend===0?'Gratis':euro(verzend))+'</div></div>'+
    '<div class="totaal-rij"><span>Te betalen</span><span>'+euro(cartTotaal()+verzend)+'</span></div></div>';
  h+='<h2 class="sectie">Betaalwijze</h2><div class="kaart li" style="cursor:default"><div class="ic plain">'+ic("card")+'</div>'+
    '<div class="mid"><div class="t">iDEAL (gesimuleerd)</div><div class="s">Veilig afrekenen \u2013 demo</div></div><div class="r">\u2713</div></div>';
  h+='<button class="btn goud" id="btn-betaal" onclick="plaatsBestelling()">'+btnIc("lock")+'Nu betalen \u2013 '+euro(cartTotaal()+verzend)+'</button>';
  openOverlay('Afrekenen',h);
}
async function plaatsBestelling(){
  var adres=el('co-adres').value.trim();
  if(!adres){toast('Vul een bezorgadres in');return;}
  STATE._adres=adres;
  var btn=el('btn-betaal');btn.disabled=true;btn.textContent='Betaling verwerken...';
  var items=[];for(var code in CART){items.push({code:code,aantal:CART[code]});}
  await new Promise(function(r){setTimeout(r,1100);});
  var d=await api('/api/order',{items:items,adres:adres});
  if(!d.ok){toast(d.fout);btn.disabled=false;return;}
  CART={}; await laadState(); var o=d.order;
  var h='<div style="text-align:center;padding:24px 6px"><div class="big-ic ok">'+ic("check-circle")+'</div>'+
    '<h2 style="font-family:Georgia,serif;color:var(--bruin);font-size:24px;margin:14px 0 6px">Bedankt voor je bestelling!</h2>'+
    '<div class="muted">Je bestelling <b>'+esc(o.id)+'</b> is geplaatst.<br>Verwachte bezorging binnen 2-3 werkdagen.</div></div>'+
    '<div class="kaart"><div class="row-between"><span class="muted">Bestelnummer</span><b>'+esc(o.id)+'</b></div><div class="divider"></div>'+
    '<div class="row-between"><span class="muted">Bezorgadres</span><span style="text-align:right;max-width:60%">'+esc(o.adres)+'</span></div><div class="divider"></div>'+
    '<div class="totaal-rij" style="border:none;padding:0"><span>Totaal</span><span>'+euro(o.totaal)+'</span></div></div>'+
    '<button class="btn" onclick="sluitOverlay();gaNaar(\'home\')">Terug naar home</button>';
  openOverlay('Bevestiging',h);
}

/* ============== PROFIEL ============== */
function renderProfiel(){
  var a=STATE.account,initialen=(a.naam||'?').split(' ').map(function(w){return w[0];}).slice(0,2).join('').toUpperCase();
  var h='<div class="kaart" style="text-align:center;padding:24px">'+
    '<div style="width:74px;height:74px;border-radius:50%;margin:0 auto 12px;background:linear-gradient(135deg,var(--bruin),var(--bruin-3));'+
    'color:#F8EFDD;display:flex;align-items:center;justify-content:center;font-size:27px;font-weight:700;font-family:Georgia,serif">'+esc(initialen)+'</div>'+
    '<div style="font-family:Georgia,serif;font-size:21px;color:var(--bruin)">'+esc(a.naam)+'</div><div class="muted">'+esc(a.email)+'</div></div>';
  h+='<div class="kaart li" onclick="openAccount()"><div class="ic plain">'+ic("gear")+'</div><div class="mid"><div class="t">Accountgegevens</div><div class="s">Naam, allergieen, voorkeuren</div></div><div class="r">'+ic("chevR")+'</div></div>';
  h+='<div class="kaart li" onclick="openCollectie()"><div class="ic plain">'+ic("box")+'</div><div class="mid"><div class="t">Mijn collectie</div><div class="s">'+STATE.registered.length+' geregistreerde producten</div></div><div class="r">'+ic("chevR")+'</div></div>';
  h+='<div class="kaart li" onclick="openOrders()"><div class="ic plain">'+ic("bag")+'</div><div class="mid"><div class="t">Mijn bestellingen</div><div class="s">'+STATE.orders.length+' bestellingen</div></div><div class="r">'+ic("chevR")+'</div></div>';
  h+='<div class="kaart li" onclick="openKlachtForm()"><div class="ic plain">'+ic("doc")+'</div><div class="mid"><div class="t">Klacht indienen</div><div class="s">Meld een probleem met een product</div></div><div class="r">'+ic("chevR")+'</div></div>';
  var openKl=STATE.complaints.filter(function(c){return c.status!=='Opgelost';}).length;
  h+='<div class="kaart li" onclick="openKlachten()"><div class="ic plain">'+ic("clipboard")+'</div><div class="mid"><div class="t">Mijn klachten</div><div class="s">'+STATE.complaints.length+' klacht'+(STATE.complaints.length===1?'':'en')+(openKl?' &middot; '+openKl+' open':'')+'</div></div><div class="r">'+ic("chevR")+'</div></div>';
  h+='<div style="margin-top:20px"><button class="btn licht" onclick="uitloggen()">Uitloggen</button></div>';
  h+='<div class="muted" style="text-align:center;margin-top:16px">Cacao Company \u00B7 MVP demo</div>';
  el('scherm').innerHTML=h;
}
function openAccount(){
  var a=STATE.account,pr=STATE.preferences,allergieenOpties=['Noten','Melk','Gluten','Soja','Pinda','Lactose'];
  var h='<label>Naam</label><input id="ac-naam" value="'+esc(a.naam)+'">'+
    '<label>E-mailadres</label><input id="ac-email" value="'+esc(a.email)+'" disabled style="opacity:.6">'+
    '<label>Allergieen</label><div class="chips" id="ac-allergie">';
  allergieenOpties.forEach(function(opt){var on=a.allergieen.indexOf(opt)>=0;
    h+='<div class="chip '+(on?'on':'')+'" data-v="'+opt+'" onclick="this.classList.toggle(\'on\')">'+opt+'</div>';});
  h+='</div><label>Favoriete chocoladesoorten</label><div class="chips" id="ac-fav">';
  STATE.categorieen.forEach(function(opt){var on=a.favorieten.indexOf(opt)>=0;
    h+='<div class="chip '+(on?'on':'')+'" data-v="'+opt+'" onclick="this.classList.toggle(\'on\')">'+opt+'</div>';});
  h+='</div><label style="margin-top:18px">Notificatievoorkeuren</label><div class="chips" id="ac-notif">';
  [['notif_bestelling','Bestellingen'],['notif_klacht','Klachtstatus'],['notif_houdbaarheid','Houdbaarheid'],['notif_aanbeveling','Aanbevelingen']]
    .forEach(function(n){var on=pr[n[0]]!==false;
      h+='<div class="chip '+(on?'on':'')+'" data-v="'+n[0]+'" onclick="this.classList.toggle(\'on\')">'+n[1]+'</div>';});
  h+='</div><button class="btn goud" style="margin-top:22px" onclick="bewaarAccount()">Wijzigingen opslaan</button>';
  openOverlay('Accountgegevens',h);
}
async function bewaarAccount(){
  function gekozen(id){return Array.prototype.slice.call(el(id).querySelectorAll('.chip.on')).map(function(c){return c.getAttribute('data-v');});}
  var notif=gekozen('ac-notif');
  var body={naam:el('ac-naam').value.trim(),allergieen:gekozen('ac-allergie'),favorieten:gekozen('ac-fav'),
    notif_bestelling:notif.indexOf('notif_bestelling')>=0,notif_klacht:notif.indexOf('notif_klacht')>=0,
    notif_houdbaarheid:notif.indexOf('notif_houdbaarheid')>=0,notif_aanbeveling:notif.indexOf('notif_aanbeveling')>=0};
  var d=await api('/api/account',body);
  if(d.ok){await laadState();sluitOverlay();toast('Wijzigingen opgeslagen \u2713');if(TAB==='profiel')renderProfiel();}else toast(d.fout||'Opslaan mislukt');
}
function openCollectie(){
  var h='';
  if(STATE.registered.length){
    STATE.registered.forEach(function(p){
      h+='<div class="kaart li" onclick="openProduct(\''+p.code+'\')"><div class="ic">'+prodImg(p)+'</div>'+
        '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+esc(p.herkomst)+' &middot; tot '+esc(p.verloopt)+'</div></div>'+
        '<div class="r"><span class="status '+statusClass(p.status)+'">'+p.status+'</span></div></div>';
    });
  }else{h='<div class="leeg"><span class="e">'+ic("box")+'</span>Nog geen geregistreerde producten.<br>Scan een reep om je collectie te starten.</div>';}
  openOverlay('Mijn collectie',h);
}
function openOrders(){
  var h='';
  if(STATE.orders.length){
    STATE.orders.forEach(function(o){
      h+='<div class="kaart li" onclick="openOrder(\''+o.id+'\')"><div class="ic plain">'+ic("box")+'</div>'+
        '<div class="mid"><div class="t">'+esc(o.id)+'</div><div class="s">'+esc(o.datum)+' &middot; '+o.items.length+' artikel'+(o.items.length===1?'':'en')+'</div></div>'+
        '<div class="r"><div style="font-weight:700;color:var(--bruin)">'+euro(o.totaal)+'</div><span class="status '+statusClass(o.status)+'" style="margin-top:5px">'+o.status+'</span></div></div>';
    });
  }else{h='<div class="leeg"><span class="e">'+ic("bag")+'</span>Nog geen bestellingen.</div>';}
  openOverlay('Mijn bestellingen',h);
}
function openOrder(id){
  var o=STATE.orders.filter(function(x){return x.id===id;})[0];if(!o)return;
  var h='<div class="kaart"><div class="row-between"><div><div style="font-family:Georgia,serif;font-size:19px;color:var(--bruin)">'+esc(o.id)+'</div>'+
    '<div class="muted">'+esc(o.datum)+'</div></div><span class="status '+statusClass(o.status)+'">'+o.status+'</span></div></div>';
  h+='<h2 class="sectie">Producten</h2><div class="kaart">';
  o.items.forEach(function(it){h+='<div class="li" style="padding:10px 0"><div class="mid"><div class="t" style="font-size:14px">'+it.aantal+'\u00D7 '+esc(it.naam)+'</div></div>'+
    '<div class="r" style="font-weight:700;color:var(--bruin)">'+euro(it.prijs*it.aantal)+'</div></div>';});
  h+='<div class="totaal-rij"><span>Totaal</span><span>'+euro(o.totaal)+'</span></div></div>';
  h+='<h2 class="sectie">Bezorgadres</h2><div class="kaart"><div class="val">'+inlineIc("pin")+' '+esc(o.adres)+'</div></div>';
  if(o.status!=='Bezorgd'&&o.status!=='Geannuleerd'){
    h+='<button class="btn rood-licht" style="margin-top:6px" onclick="annuleerOrder(\''+o.id+'\')">Bestelling annuleren</button>';
  }
  openOverlay('Bestelling',h);
}
function openKlachtForm(){
  var h='<label>Product</label><select id="kl-product"><option value="">Kies een product...</option>';
  STATE.products.forEach(function(p){h+='<option>'+esc(p.naam)+'</option>';});
  h+='</select><label>Categorie</label><select id="kl-cat">';
  ['Smaak','Verpakking','Levering','Kwaliteit','Allergenen','Anders'].forEach(function(c){h+='<option>'+c+'</option>';});
  h+='</select><label>Omschrijving</label><textarea id="kl-oms" placeholder="Beschrijf je klacht zo duidelijk mogelijk..."></textarea>'+
    '<label>Foto toevoegen (optioneel)</label>'+
    '<input type="file" id="kl-foto" accept="image/*" onchange="this.nextElementSibling.textContent=this.files.length?(\'Bijlage: \'+this.files[0].name):\'\'" style="padding:10px">'+
    '<div class="muted" style="margin-top:5px"></div>'+
    '<button class="btn goud" style="margin-top:22px" onclick="verstuurKlacht()">Klacht verzenden</button>';
  openOverlay('Klacht indienen',h);
}
async function verstuurKlacht(){
  var product=el('kl-product').value,cat=el('kl-cat').value,oms=el('kl-oms').value.trim(),fi=el('kl-foto');
  var foto=(fi&&fi.files.length)?fi.files[0].name:'';
  if(!product){toast('Kies een product');return;} if(!oms){toast('Vul een omschrijving in');return;}
  var d=await api('/api/complaint',{product:product,categorie:cat,omschrijving:oms,foto:foto});
  if(!d.ok){toast(d.fout);return;}
  await laadState(); var c=d.complaint;
  var h='<div style="text-align:center;padding:24px 6px"><div class="big-ic">'+ic("mail")+'</div>'+
    '<h2 style="font-family:Georgia,serif;color:var(--bruin);font-size:23px;margin:12px 0 6px">Klacht ontvangen</h2>'+
    '<div class="muted">Je klacht <b>'+esc(c.id)+'</b> is geregistreerd.<br>Status: <b>Ontvangen</b>.<br>We nemen zo snel mogelijk contact op.</div></div>'+
    '<button class="btn" onclick="openKlachten()">Bekijk mijn klachten</button>'+
    '<button class="btn licht" style="margin-top:10px" onclick="sluitOverlay();gaNaar(\'profiel\')">Sluiten</button>';
  openOverlay('Bevestiging',h);
}
function openKlachten(){
  var h='';
  if(STATE.complaints.length){
    STATE.complaints.forEach(function(c){
      h+='<div class="kaart li" onclick="openKlacht(\''+c.id+'\')"><div class="ic plain">'+ic("doc")+'</div>'+
        '<div class="mid"><div class="t">'+esc(c.product)+'</div><div class="s">'+esc(c.datum)+' &middot; '+esc(c.categorie)+'</div></div>'+
        '<div class="r"><span class="status '+statusClass(c.status)+'">'+c.status+'</span></div></div>';
    });
  }else{h='<div class="leeg"><span class="e">'+ic("clipboard")+'</span>Je hebt nog geen klachten ingediend.</div>';}
  openOverlay('Mijn klachten',h);
}
function openKlacht(id){
  var c=STATE.complaints.filter(function(x){return x.id===id;})[0];if(!c)return;
  var h='<div class="kaart"><div class="row-between"><div style="font-family:Georgia,serif;font-size:18px;color:var(--bruin)">'+esc(c.id)+'</div>'+
    '<span class="status '+statusClass(c.status)+'">'+c.status+'</span></div><div class="divider"></div>'+
    '<div class="info-rij" style="padding-top:0"><div class="lbl">Product</div><div class="val">'+esc(c.product)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Categorie</div><div class="val">'+esc(c.categorie)+'</div></div>'+
    '<div class="info-rij"><div class="lbl">Datum</div><div class="val">'+esc(c.datum)+'</div></div>'+
    '<div class="info-rij"'+(c.foto?'':' style="border:none"')+'><div class="lbl">Omschrijving</div><div class="val">'+esc(c.omschrijving)+'</div></div>';
  if(c.foto){h+='<div class="info-rij" style="border:none"><div class="lbl">Bijlage</div><div class="val">'+inlineIc("clip")+' '+esc(c.foto)+'</div></div>';}
  h+='</div><h2 class="sectie">Status wijzigen (demo)</h2><div class="chips">';
  ['Ontvangen','In behandeling','Opgelost'].forEach(function(st){
    h+='<div class="chip '+(c.status===st?'on':'')+'" onclick="wijzigKlachtStatus(\''+c.id+'\',\''+st+'\')">'+st+'</div>';});
  h+='</div><div class="muted" style="margin-top:10px">Bij een statuswijziging ontvang je automatisch een notificatie.</div>';
  openOverlay('Klacht '+esc(c.id),h);
}
async function wijzigKlachtStatus(id,status){var d=await api('/api/complaint/status',{id:id,status:status});
  if(d.ok){await laadState();toast('Status: '+status);openKlacht(id);}else toast(d.fout);}
async function uitloggen(){await api('/api/logout',{});location.href='/';}

async function verwijderUitCollectie(code){
  var d=await api('/api/unregister-product',{code:code});
  if(d.ok){toast('Verwijderd uit je collectie');await laadState();openProduct(code);}else toast(d.fout);
}
async function annuleerOrder(id){
  var d=await api('/api/order/cancel',{id:id});
  if(d.ok){toast('Bestelling geannuleerd');await laadState();openOrder(id);}else toast(d.fout);
}
function toggleProductLijst(){
  var c=el('prod-lijst'); if(!c) return;
  if(c.style.display==='none'){
    var h='';
    STATE.products.forEach(function(p){
      var inC=STATE.registered.some(function(r){return r.code===p.code;});
      h+='<div class="kaart li" onclick="openProduct(\''+p.code+'\')"><div class="ic">'+prodImg(p)+'</div>'+
         '<div class="mid"><div class="t">'+esc(p.naam)+'</div><div class="s">'+esc(p.code)+' \u00B7 '+esc(p.categorie)+'</div></div>'+
         '<div class="r">'+(inC?'<span class="status st-goed">In collectie</span>':ic('chevR'))+'</div></div>';
    });
    c.innerHTML=h; c.style.display='block';
  } else { c.style.display='none'; }
}

/* ============== START ============== */
function sizeDevice(){var d=document.querySelector('.device');if(!d)return;var r=9/16;var mh=window.innerHeight*0.97,mw=window.innerWidth*0.97;var h=Math.min(mh,940),w=h*r;if(w>mw){w=mw;h=w/r;}d.style.height=Math.round(h)+'px';d.style.width=Math.round(w)+'px';}
sizeDevice(); window.addEventListener('resize',sizeDevice);
klok(); setInterval(klok,10000);
(async function(){await laadState();if(!STATE){location.href='/';return;}gaNaar('home');})();
</script>
</body>
</html>"""

# ===========================================================================
# START VAN DE APPLICATIE
# ===========================================================================

if __name__ == "__main__":
    seed_if_empty()
    print("=" * 60)
    print("  >>> CACAO COMPANY - VERSIE 2 <<<")
    print("  (login-fix, geen demo-tekst, annuleren, collectie")
    print("   verwijderen, scan-productlijst, ratio 9:16)")
    print("  Open in je browser:  http://127.0.0.1:5050")
    print("  Demo-login: demo@cacao.nl / demo123")
    print("  Stoppen: druk op Ctrl + C")
    print("=" * 60)
    # debug=True zorgt dat de app automatisch herlaadt als je main.py opslaat.
    app.run(host="127.0.0.1", port=5050, debug=True)