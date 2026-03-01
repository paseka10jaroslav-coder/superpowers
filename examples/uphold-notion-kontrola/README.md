# Uphold–Notion Kontrola

A Python utility that fetches live portfolio data from the **Uphold API**,
runs a set of validation checks (*kontrola* — Czech for "check/verification"),
and syncs the results into a **Notion database**.

Useful for portfolio owners who manage their crypto/fiat balances in Uphold and
want a live, alerting dashboard in Notion — with no manual copy-paste required.

---

## What it does

```
Uphold API  ──►  kontrola checks  ──►  Notion database
```

1. **Fetch** — pulls all Uphold cards (accounts) via the Uphold v0 REST API.
2. **Kontrola** — runs validation checks on each card:
   - Low USD balance (< $10 by default)
   - Funds on hold (available < balance)
   - Stale account (no transactions in the last 7 days)
3. **Sync** — upserts a Notion page per card with live balance, status, and
   any alert messages. Existing pages are updated in place (no duplicates).

---

## Notion database schema

Create a Notion database with these properties:

| Property   | Type        | Notes                        |
|------------|-------------|------------------------------|
| Name       | Title       | Card label                   |
| Card ID    | Text        | Uphold internal card UUID    |
| Currency   | Select      | e.g. BTC, ETH, USD           |
| Balance    | Number      | Current balance              |
| Available  | Number      | Available (non-held) balance |
| Status     | Select      | `OK` or `Alert`              |
| Alerts     | Text        | Pipe-separated alert messages|
| Synced At  | Date        | Last sync timestamp (UTC)    |

Share the database with your Notion integration (click **Connect to** in the
database settings).

---

## Setup

```bash
# 1. Clone / navigate to this directory
cd examples/uphold-notion-kontrola

# 2. Install dependencies
pip install requests python-dotenv

# 3. Configure credentials
cp .env.example .env
$EDITOR .env          # fill in your keys

# 4. Run
python uphold_notion_kontrola.py
```

---

## Credentials

### Uphold

1. Log in at [uphold.com](https://uphold.com)
2. Go to **Profile → API Keys**
3. Create a Personal Access Token — use the **Client ID** and **Client Secret**

### Notion

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a new integration and copy the **Internal Integration Secret**
3. Open your database → **…** menu → **Connect to** → select your integration
4. Copy the **Database ID** from the database URL:
   `https://notion.so/<workspace>/<DATABASE_ID>?v=...`

---

## Automation

Run on a schedule with cron:

```cron
# Every 30 minutes
*/30 * * * *  cd /path/to/uphold-notion-kontrola && python uphold_notion_kontrola.py >> kontrola.log 2>&1
```

Or with GitHub Actions (store credentials as repository secrets):

```yaml
name: Uphold–Notion Kontrola

on:
  schedule:
    - cron: "*/30 * * * *"
  workflow_dispatch:

jobs:
  kontrola:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install requests python-dotenv
      - run: python examples/uphold-notion-kontrola/uphold_notion_kontrola.py
        env:
          UPHOLD_CLIENT_ID: ${{ secrets.UPHOLD_CLIENT_ID }}
          UPHOLD_CLIENT_SECRET: ${{ secrets.UPHOLD_CLIENT_SECRET }}
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
```

The script exits with code `2` when any alerts are found, so your scheduler
can send notifications on failure.

---

## Configuration

Edit the threshold constants near the top of `uphold_notion_kontrola.py`:

| Constant                    | Default | Description                        |
|-----------------------------|---------|------------------------------------|
| `LOW_BALANCE_THRESHOLD_USD` | `10.0`  | USD low-balance warning threshold  |
| `STALE_DAYS_THRESHOLD`      | `7`     | Days since last tx before warning  |

---

## Tech stack

- **Python 3.10+**
- [requests](https://docs.python-requests.org/) — HTTP client
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/) — `.env` loading
- [Uphold API v0](https://uphold.com/en/developer/api/documentation/)
- [Notion API](https://developers.notion.com/)
