import csv
from datetime import datetime, timezone
from cookie import *
from pathlib import Path

import requests

print("")
print("-" * 30 + "OBS" + "-" * 30)
print("You may need to be logged in MTGMelee to work")
print("Your cookie may change with time. Renew it.")
print("Round ID is usually the number in the request URL or body.")
print("Cookie authenticates you; round ID selects the match round.")
print("-" * 30 + "---" + "-" * 30)
print("")


# =========================================
# INPUTS
# =========================================

rounds_id = input("Introduce rounds ID (comma-separated, no brackets): ")
ROUND_IDS = [int(x.strip()) for x in rounds_id.split(",") if x.strip()]
DIRECTORY = input("Which folder you want to save the csv at: ")
NAME = input("Name of the file: ")

COOKIE = YOUR_COOKIE

# =========================================
# CONFIG
# =========================================

BASE_URL = "https://melee.gg"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,es;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://melee.gg",
    "priority": "u=1, i",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
    "cookie": COOKIE,
}


# =========================================
# HELPERS
# =========================================

def debug_response(r):
    print("=" * 80)
    print("STATUS:", r.status_code)
    print("FINAL URL:", r.url)
    print("CONTENT-TYPE:", r.headers.get("content-type"))
    print("BODY PREVIEW:")
    print(r.text[:1200])
    print("=" * 80)


def build_payload(draw=1, start=0, length=100):
    return {
        "draw": str(draw),

        "columns[0][data]": "TableNumber",
        "columns[0][name]": "TableNumber",
        "columns[0][searchable]": "true",
        "columns[0][orderable]": "true",
        "columns[0][search][value]": "",
        "columns[0][search][regex]": "false",

        "columns[1][data]": "PodNumber",
        "columns[1][name]": "PodNumber",
        "columns[1][searchable]": "true",
        "columns[1][orderable]": "true",
        "columns[1][search][value]": "",
        "columns[1][search][regex]": "false",

        "columns[2][data]": "Teams",
        "columns[2][name]": "Teams",
        "columns[2][searchable]": "false",
        "columns[2][orderable]": "false",
        "columns[2][search][value]": "",
        "columns[2][search][regex]": "false",

        "columns[3][data]": "Decklists",
        "columns[3][name]": "Decklists",
        "columns[3][searchable]": "false",
        "columns[3][orderable]": "false",
        "columns[3][search][value]": "",
        "columns[3][search][regex]": "false",

        "columns[4][data]": "ResultString",
        "columns[4][name]": "ResultString",
        "columns[4][searchable]": "false",
        "columns[4][orderable]": "false",
        "columns[4][search][value]": "",
        "columns[4][search][regex]": "false",

        "order[0][column]": "0",
        "order[0][dir]": "asc",

        "start": str(start),
        "length": str(length),
        "search[value]": "",
        "search[regex]": "false",
    }


def parse_utc(iso_value):
    if not iso_value:
        return None
    return datetime.fromisoformat(
        iso_value.replace("Z", "+00:00")
    ).astimezone(timezone.utc).isoformat()


def parse_match(match):
    competitors = match.get("Competitors", [])
    p1 = competitors[0] if len(competitors) > 0 else {}
    p2 = competitors[1] if len(competitors) > 1 else {}

    deck1 = None
    deck2 = None

    if p1.get("Decklists"):
        deck1 = p1["Decklists"][0].get("DecklistName")

    if p2.get("Decklists"):
        deck2 = p2["Decklists"][0].get("DecklistName")

    return {
        "match_created_utc": parse_utc(match.get("DateCreated")),
        "user_deck": deck1,
        "oppo_deck": deck2,
        "result_vs_oppo": f"{p1.get("GameWins")}-{p2.get("GameWins")}"
    }


# =========================================
# REQUESTS
# =========================================

session = requests.Session()
session.headers.update(HEADERS)


def fetch_round(round_id, draw=1, start=0, length=100):
    url = f"{BASE_URL}/Match/GetRoundMatches/{round_id}"
    payload = build_payload(draw=draw, start=start, length=length)

    r = session.post(url, data=payload, timeout=30, allow_redirects=True)

    if r.status_code != 200:
        debug_response(r)
        raise RuntimeError(f"HTTP {r.status_code} while fetching round {round_id}")

    ctype = r.headers.get("content-type", "")
    if "json" not in ctype.lower():
        debug_response(r)
        raise RuntimeError(f"Expected JSON for round {round_id}, got {ctype}")

    try:
        data = r.json()
    except requests.exceptions.JSONDecodeError as e:
        debug_response(r)
        raise RuntimeError(f"JSON decode failed for round {round_id}: {e}") from e

    if "data" not in data:
        raise RuntimeError(f"No 'data' key in response for round {round_id}")

    return data


# =========================================
# MAIN
# =========================================

def main():
    if "PASTE_A_FRESH_COOKIE_STRING_HERE" in COOKIE:
        raise RuntimeError("Paste your fresh cookie string into COOKIE first.")

    rows = []

    print("")
    for i, round_id in enumerate(ROUND_IDS, start=1):
        print(f"Fetching round {i}/{len(ROUND_IDS)}: {round_id}")
        data = fetch_round(round_id, draw=i, start=0, length=100)

        for match in data["data"]:
            rows.append(parse_match(match))

    print("")

    out_dir = Path(DIRECTORY)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(f"{out_dir}/{str(NAME)}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["match_created_utc", "user_deck", "oppo_deck", "result_vs_oppo"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {out_dir}/{str(NAME)}.csv")
    print("")


if __name__ == "__main__":
    main()
