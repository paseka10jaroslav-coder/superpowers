"""
Uphold–Notion Kontrola
======================
Fetches live portfolio data from the Uphold API and syncs it into a Notion
database, performing a set of validation checks (kontrola) on each balance.

Requirements:
    pip install requests python-dotenv

Environment variables (see .env.example):
    UPHOLD_CLIENT_ID       – Uphold OAuth2 client ID
    UPHOLD_CLIENT_SECRET   – Uphold OAuth2 client secret
    NOTION_API_KEY         – Notion integration secret
    NOTION_DATABASE_ID     – ID of the target Notion database

Usage:
    python uphold_notion_kontrola.py
"""

import os
import sys
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

UPHOLD_API_BASE = "https://api.uphold.com/v0"
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_API_VERSION = "2022-06-28"

# Kontrola thresholds
LOW_BALANCE_THRESHOLD_USD = 10.0   # warn when balance < $10
STALE_DAYS_THRESHOLD = 7           # warn when last tx is older than 7 days


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class UpholdCard:
    """Represents a single Uphold card (account/balance)."""
    id: str
    label: str
    currency: str
    balance: float
    available: float
    last_transaction_at: Optional[datetime] = None
    alerts: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Uphold client
# ---------------------------------------------------------------------------

class UpholdClient:
    """Minimal Uphold API v0 client using Personal Access Token (PAT)."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._auth = (client_id, client_secret)

    def _get(self, path: str) -> dict | list:
        url = f"{UPHOLD_API_BASE}{path}"
        resp = requests.get(url, auth=self._auth, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_cards(self) -> list[UpholdCard]:
        raw_cards = self._get("/me/cards")
        cards: list[UpholdCard] = []
        for c in raw_cards:
            last_tx = None
            raw_ts = c.get("lastTransactionAt")
            if raw_ts:
                try:
                    last_tx = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                except ValueError:
                    pass

            cards.append(
                UpholdCard(
                    id=c["id"],
                    label=c.get("label") or c["currency"],
                    currency=c["currency"],
                    balance=float(c.get("balance", 0)),
                    available=float(c.get("available", 0)),
                    last_transaction_at=last_tx,
                )
            )
        return cards


# ---------------------------------------------------------------------------
# Kontrola (validation checks)
# ---------------------------------------------------------------------------

def run_kontrola(card: UpholdCard) -> None:
    """Run all validation checks on a card and populate card.alerts."""
    now = datetime.now(timezone.utc)

    if card.balance < LOW_BALANCE_THRESHOLD_USD and card.currency == "USD":
        card.alerts.append(
            f"Low balance: ${card.balance:.2f} is below ${LOW_BALANCE_THRESHOLD_USD:.2f}"
        )

    if card.available < card.balance:
        card.alerts.append(
            f"Funds on hold: available ${card.available:.2f} < balance ${card.balance:.2f}"
        )

    if card.last_transaction_at:
        age_days = (now - card.last_transaction_at).days
        if age_days > STALE_DAYS_THRESHOLD:
            card.alerts.append(
                f"Stale account: last transaction was {age_days} days ago"
            )

    if card.alerts:
        log.warning("Card '%s' (%s) — %d alert(s):", card.label, card.currency, len(card.alerts))
        for alert in card.alerts:
            log.warning("  • %s", alert)
    else:
        log.info("Card '%s' (%s) — OK", card.label, card.currency)


# ---------------------------------------------------------------------------
# Notion client
# ---------------------------------------------------------------------------

class NotionClient:
    """Minimal Notion API client for database page creation/updating."""

    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        }

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{NOTION_API_BASE}{path}"
        resp = requests.post(url, headers=self._headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, path: str, payload: dict) -> dict:
        url = f"{NOTION_API_BASE}{path}"
        resp = requests.patch(url, headers=self._headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def query_database(self, database_id: str, filter_payload: dict | None = None) -> list[dict]:
        url = f"{NOTION_API_BASE}/databases/{database_id}/query"
        payload = filter_payload or {}
        resp = requests.post(url, headers=self._headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [])

    def upsert_card(self, database_id: str, card: UpholdCard) -> None:
        """Create or update a Notion page for the given card."""
        status = "Alert" if card.alerts else "OK"
        alert_text = " | ".join(card.alerts) if card.alerts else ""
        synced_at = datetime.now(timezone.utc).isoformat()

        properties = {
            "Name": {"title": [{"text": {"content": card.label}}]},
            "Card ID": {"rich_text": [{"text": {"content": card.id}}]},
            "Currency": {"select": {"name": card.currency}},
            "Balance": {"number": card.balance},
            "Available": {"number": card.available},
            "Status": {"select": {"name": status}},
            "Alerts": {"rich_text": [{"text": {"content": alert_text}}]},
            "Synced At": {"date": {"start": synced_at}},
        }

        # Check if a page already exists for this card
        existing = self.query_database(
            database_id,
            {
                "filter": {
                    "property": "Card ID",
                    "rich_text": {"equals": card.id},
                }
            },
        )

        if existing:
            page_id = existing[0]["id"]
            self._patch(f"/pages/{page_id}", {"properties": properties})
            log.info("  Notion page updated — '%s'", card.label)
        else:
            self._post(
                "/pages",
                {"parent": {"database_id": database_id}, "properties": properties},
            )
            log.info("  Notion page created — '%s'", card.label)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    client_id = os.getenv("UPHOLD_CLIENT_ID", "")
    client_secret = os.getenv("UPHOLD_CLIENT_SECRET", "")
    notion_key = os.getenv("NOTION_API_KEY", "")
    notion_db = os.getenv("NOTION_DATABASE_ID", "")

    missing = [
        name
        for name, val in [
            ("UPHOLD_CLIENT_ID", client_id),
            ("UPHOLD_CLIENT_SECRET", client_secret),
            ("NOTION_API_KEY", notion_key),
            ("NOTION_DATABASE_ID", notion_db),
        ]
        if not val
    ]
    if missing:
        log.error("Missing required environment variables: %s", ", ".join(missing))
        log.error("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    log.info("=== Uphold–Notion Kontrola starting ===")

    # 1. Fetch cards from Uphold
    log.info("Fetching cards from Uphold API…")
    uphold = UpholdClient(client_id, client_secret)
    cards = uphold.get_cards()
    log.info("Found %d card(s).", len(cards))

    # 2. Run kontrola checks
    log.info("Running kontrola checks…")
    for card in cards:
        run_kontrola(card)

    # 3. Sync to Notion
    log.info("Syncing to Notion database %s…", notion_db)
    notion = NotionClient(notion_key)
    for card in cards:
        notion.upsert_card(notion_db, card)

    # 4. Summary
    alerts_total = sum(len(c.alerts) for c in cards)
    log.info("=== Done. Cards: %d | Alerts: %d ===", len(cards), alerts_total)

    if alerts_total:
        sys.exit(2)  # non-zero exit so CI/cron jobs can detect issues


if __name__ == "__main__":
    main()
