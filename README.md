# Galaxy Digital — Hyperliquid Cluster Analysis

Live dashboard and CLI tools for tracking Galaxy Digital's on-chain positions on [Hyperliquid L1](https://hyperliquid.xyz).

Monitors 4 verified cluster wallets in real time — spot holdings, perpetual positions, net delta exposure, hedge status, and 24h funding yield.

![Python](https://img.shields.io/badge/python-3.10+-333?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-333)

---

## Live Dashboard

A static site that calls the Hyperliquid API directly from the browser. No backend required.

**Deploy to Netlify:**

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/nijirom/galaxy-hyperliquid-dashboard)

Or run locally:

```bash
# Flask dev server (Python)
pip install -r requirements.txt
python app.py
# → http://localhost:5000

# Or just open the static file
open public/index.html
```

### What it shows

| Metric | Description |
|---|---|
| **Spot Exposure** | Total USD value of spot holdings |
| **Perp Exposure** | Total USD value of perpetual positions |
| **Net Delta** | Spot + Perp (shorts are negative) |
| **Hedge Status** | `DELTA NEUTRAL` if net delta < 5% of spot, else `DIRECTIONAL` |
| **24h Funding** | Cumulative funding payments received in last 24 hours |

Plus an exposure-by-coin bar chart, account allocation breakdown, and a full positions table.

---

## CLI Tools

### `report.py` — Cluster audit

Prints a snapshot of Galaxy's current exposure and hedge status.

```bash
python report.py
```

```
--- GALAXY CLUSTER STATUS ---
Total Spot Exposure: $6,448,188.75
Total Perp Exposure: $-28,231,689.59
NET CLUSTER DELTA:    $-21,783,500.83
Status: DIRECTIONAL EXPOSURE (Unhedged)
```

### `funding.py` — Funding yield

Calculates realized funding across all cluster accounts.

```python
from config import GALAXY_CLUSTER
from funding import calculate_cluster_funding

calculate_cluster_funding(GALAXY_CLUSTER, days=7)
```

---

## Project Structure

```
├── public/
│   └── index.html        # Static dashboard (Netlify deploy target)
├── templates/
│   └── dashboard.html    # Flask-served dashboard template
├── app.py                # Flask backend with background data refresh
├── engine.py             # Core data fetcher (perp + spot positions)
├── config.py             # Cluster wallet addresses & tracked coins
├── funding.py            # Funding yield calculator
├── report.py             # CLI audit script
├── requirements.txt      # Python dependencies
├── netlify.toml          # Netlify deploy config
└── update_data.yml       # GitHub Actions workflow (daily cron)
```

---

## Tracked Wallets

| Label | Address |
|---|---|
| Master_Trading | `0xcaC19662Ec88d23Fa1c81aC0e8570B0cf2FF26b3` |
| Agent_1 | `0x69cc3ae720efdff1cd2a8edec79a7a3fac6e14fd` |
| Agent_2 | `0xc75a3fc98b0e1af7a95b6a720adf2e23806d2c7b` |
| Agent_3 | `0x62bc1fe6009388219dd84f9dca37930f6fb6fa22` |

---

## Dependencies

```
hyperliquid-python-sdk
pandas
flask
gunicorn
```

Install with:

```bash
pip install -r requirements.txt
```

---

## License

MIT
