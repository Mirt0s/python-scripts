"""
PoE Trade API - Prueba de concepto
Sin dependencias externas, solo librería estándar de Python 3.x
"""

import urllib.request
import urllib.error
import json

# ── Configuración ──────────────────────────────────────────────────────────────

LEAGUE = "Mirage"   # Liga activa de PoE 1. Cambia a "Standard" si quieres
ITEM   = "Fulgurite Tincture"     # Ítem a buscar

BASE_URL = "https://www.pathofexile.com/api/trade"

# GGG exige un User-Agent no vacío, de lo contrario devuelve 403
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent":   "poe-discord-bot-poc/0.1 (contact: prueba@mirtos.com)",
}

# ── Step 1: POST /search — obtener search ID y lista de IDs de listings ────────

def search(league: str, item_name: str) -> dict:
    url = f"{BASE_URL}/search/{league}"

    payload = {
        "query": {
            "type":   item_name,
            "status": {"option": "online"},
            "filters": {}
        },
        "sort": {"price": "asc"}
    }

    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")

    print(f"[1/2] POST {url}")
    print(f"      Body: {json.dumps(payload, indent=6)}\n")

    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    print(f"      → Search ID : {result['id']}")
    print(f"      → Listings  : {len(result['result'])} encontrados\n")
    return result


# ── Step 2: GET /fetch — obtener detalle de los primeros listings ──────────────

def fetch_listings(item_ids: list, query_id: str) -> dict:
    # La API permite máximo 10 IDs por llamada
    ids_param = ",".join(item_ids[:10])
    url       = f"{BASE_URL}/fetch/{ids_param}?query={query_id}"

    req = urllib.request.Request(url, headers=HEADERS, method="GET")

    print(f"[2/2] GET {url}\n")

    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Helpers de presentación ────────────────────────────────────────────────────

def format_price(listing: dict) -> str:
    try:
        price = listing["listing"]["price"]
        return f"{price['amount']} {price['currency']}"
    except (KeyError, TypeError):
        return "sin precio"


def print_results(data: dict, league: str, search_id: str) -> None:
    results = data.get("result", [])
    if not results:
        print("Sin resultados.")
        return

    print(f"{'─' * 55}")
    print(f"  Top {len(results)} listings de '{ITEM}' en {league}")
    print(f"{'─' * 55}")

    for i, entry in enumerate(results, 1):
        item    = entry.get("item", {})
        listing = entry.get("listing", {})
        name    = item.get("name") or item.get("typeLine", "desconocido")
        seller  = listing.get("account", {}).get("name", "?")
        price   = format_price(entry)
        ilvl    = item.get("ilvl", "—")

        print(f"  {i:>2}. {name:<28} {price:<20} ilvl:{ilvl}  seller:{seller}")

    trade_url = f"https://www.pathofexile.com/trade/search/{league}/{search_id}"
    print(f"\n  Ver en browser → {trade_url}")
    print(f"{'─' * 55}\n")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'═' * 55}")
    print(f"  PoE Trade API — Prueba de concepto")
    print(f"  Ítem: {ITEM}  |  Liga: {LEAGUE}")
    print(f"{'═' * 55}\n")

    try:
        search_result = search(LEAGUE, ITEM)
        search_id     = search_result["id"]
        listing_ids   = search_result["result"]

        if not listing_ids:
            print("La búsqueda no devolvió listings.")
            return

        fetch_result = fetch_listings(listing_ids, search_id)

        print("  Respuesta raw (primeros 2 listings):")
        preview = {"result": fetch_result.get("result", [])[:2]}
        print(json.dumps(preview, indent=4, ensure_ascii=False))
        print()

        print_results(fetch_result, LEAGUE, search_id)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {e.reason}")
        print(f"Respuesta: {body}")

    except urllib.error.URLError as e:
        print(f"Error de red: {e.reason}")


if __name__ == "__main__":
    main()