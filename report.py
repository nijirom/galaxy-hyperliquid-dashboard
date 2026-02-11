from config import GALAXY_CLUSTER
from engine import get_cluster_state, info

def run_galaxy_audit():
    df = get_cluster_state(GALAXY_CLUSTER)

    if df.empty:
        print("No open positions found. Skipping calculations.")
        return
    

    mids = info.all_mids()
    
    # value calculation for spot and perps
    def calc_usd(row):
        # Handle naming conventions for spot vs perp pricing
        price_key = f"{row['coin']}/USDC" if row['type'] == "SPOT" else row['coin']
        price = float(mids.get(price_key, mids.get(row['coin'], 0)))
        return row['size'] * price

    df['usd_value'] = df.apply(calc_usd, axis=1)
    
    # metrics
    spot_val = df[df['type'] == "SPOT"]['usd_value'].sum()
    perp_val = df[df['type'] == "PERP"]['usd_value'].sum()
    net_delta = spot_val + perp_val # Perp shorts are negative
    
    print("--- GALAXY CLUSTER STATUS ---")
    print(f"Total Spot Exposure: ${spot_val:,.2f}")
    print(f"Total Perp Exposure: ${perp_val:,.2f}")
    print(f"NET CLUSTER DELTA:    ${net_delta:,.2f}")
    
    # success threshold for delta-neutral strategy
    if abs(net_delta) < (spot_val * 0.05):
        print("Status: INSTITUTIONAL BASIS TRADE (Hedged)")
    else:
        print("Status: DIRECTIONAL EXPOSURE (Unhedged)")

if __name__ == "__main__":
    run_galaxy_audit()