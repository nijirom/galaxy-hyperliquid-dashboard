import os
import time
import threading
from flask import Flask, jsonify, render_template
from engine import get_cluster_state, info
from funding import calculate_cluster_funding
from config import GALAXY_CLUSTER, TRACKED_COINS

app = Flask(__name__)

# Start background data fetcher on import (needed for gunicorn)
_bg_started = False

# ── Cached data store (refreshed in background) ─────────────────────────────
cache = {
    "positions": [],
    "summary": {},
    "by_coin": [],
    "by_account": [],
    "funding": [],
    "last_updated": None,
}
cache_lock = threading.Lock()

REFRESH_INTERVAL = 30  # seconds


def refresh_data():
    """Fetch fresh data from Hyperliquid and update the cache."""
    while True:
        try:
            df = get_cluster_state(GALAXY_CLUSTER)
            mids = info.all_mids()

            positions = []
            by_coin = {}
            by_account = {}

            if not df.empty:
                # Calculate USD values
                for _, row in df.iterrows():
                    price_key = (
                        f"{row['coin']}/USDC"
                        if row["type"] == "SPOT"
                        else row["coin"]
                    )
                    price = float(mids.get(price_key, mids.get(row["coin"], 0)))
                    usd = row["size"] * price

                    positions.append(
                        {
                            "account": row["account"],
                            "coin": row["coin"],
                            "size": round(row["size"], 4),
                            "type": row["type"],
                            "price": round(price, 2),
                            "usd_value": round(usd, 2),
                        }
                    )

                    # Aggregate by coin
                    coin = row["coin"]
                    if coin not in by_coin:
                        by_coin[coin] = {"spot": 0, "perp": 0}
                    if row["type"] == "SPOT":
                        by_coin[coin]["spot"] += usd
                    else:
                        by_coin[coin]["perp"] += usd

                    # Aggregate by account
                    acct = row["account"]
                    if acct not in by_account:
                        by_account[acct] = {"spot": 0, "perp": 0}
                    if row["type"] == "SPOT":
                        by_account[acct]["spot"] += usd
                    else:
                        by_account[acct]["perp"] += usd

            spot_val = sum(p["usd_value"] for p in positions if p["type"] == "SPOT")
            perp_val = sum(p["usd_value"] for p in positions if p["type"] == "PERP")
            net_delta = spot_val + perp_val

            if spot_val != 0:
                hedged = abs(net_delta) < abs(spot_val) * 0.05
            else:
                hedged = abs(net_delta) < 1000

            # Funding (last 24h)
            funding_data = []
            start_time = int((time.time() - 86400) * 1000)
            for label, address in GALAXY_CLUSTER.items():
                try:
                    history = info.user_funding_history(address, start_time)
                    total = sum(float(e.get("usdc", 0)) for e in history)
                    funding_data.append({"account": label, "funding_24h": round(total, 2)})
                except Exception:
                    funding_data.append({"account": label, "funding_24h": 0})

            total_funding = sum(f["funding_24h"] for f in funding_data)

            # Sort by_coin list for chart
            coin_list = [
                {"coin": c, "spot": round(v["spot"], 2), "perp": round(v["perp"], 2)}
                for c, v in sorted(by_coin.items(), key=lambda x: abs(x[1]["spot"]) + abs(x[1]["perp"]), reverse=True)
            ]

            account_list = [
                {"account": a, "spot": round(v["spot"], 2), "perp": round(v["perp"], 2)}
                for a, v in by_account.items()
            ]

            with cache_lock:
                cache["positions"] = positions
                cache["summary"] = {
                    "spot_exposure": round(spot_val, 2),
                    "perp_exposure": round(perp_val, 2),
                    "net_delta": round(net_delta, 2),
                    "hedged": hedged,
                    "total_funding_24h": round(total_funding, 2),
                    "num_positions": len(positions),
                }
                cache["by_coin"] = coin_list
                cache["by_account"] = account_list
                cache["funding"] = funding_data
                cache["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

            print(f"[{cache['last_updated']}] Data refreshed — {len(positions)} positions")

        except Exception as e:
            print(f"Error refreshing data: {e}")

        time.sleep(REFRESH_INTERVAL)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/data")
def api_data():
    with cache_lock:
        return jsonify(cache)


# ── Background thread launcher ────────────────────────────────────────────────

def start_background():
    global _bg_started
    if _bg_started:
        return
    _bg_started = True
    t = threading.Thread(target=refresh_data, daemon=True)
    t.start()


# Auto-start when imported by gunicorn
start_background()


# ── Local dev entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching initial data from Hyperliquid...")
    while cache["last_updated"] is None:
        time.sleep(0.5)

    port = int(os.environ.get("PORT", 5000))
    print(f"Dashboard ready at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
