from hyperliquid.info import Info
from hyperliquid.utils import constants
import pandas as pd

info = Info(constants.MAINNET_API_URL, skip_ws=True)

def get_cluster_state(cluster):
    all_data = []
    for label, address in cluster.items():
        state = info.user_state(address)
        
        # 1. PERPS: Access 'assetPositions' and use 'szi' for size
        for pos in state.get('assetPositions', []):
            p = pos.get('position', {})
            if float(p.get('szi', 0)) != 0:
                all_data.append({
                    "account": label, "coin": p.get('coin'),
                    "size": float(p.get('szi')), "type": "PERP"
                })
            
        # 2. SPOT: Use separate spot_user_state endpoint for spot balances
        spot_state = info.spot_user_state(address)
        balances = spot_state.get('balances', [])
        
        for s in balances:
            # Use 'total' for spot amounts
            if float(s.get('total', 0)) > 0:
                all_data.append({
                    "account": label, "coin": s.get('coin'),
                    "size": float(s.get('total', 0)), "type": "SPOT"
                })
                
    return pd.DataFrame(all_data)