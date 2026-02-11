import time
from engine import info

def calculate_cluster_funding(cluster, days=1):
    start_time = int((time.time() - (days * 86400)) * 1000)
    total_funding = 0
    
    for label, address in cluster.items():
        # Correct SDK method for user-specific funding
        history = info.user_funding_history(address, start_time)
        
        # Funding events use 'usdc' for the dollar value
        account_total = sum(float(event.get('usdc', 0)) for event in history)
        total_funding += account_total
        print(f"{label} Realized Funding: ${account_total:,.2f}")
        
    print(f"--- TOTAL CLUSTER YIELD ({days}d): ${total_funding:,.2f} ---")