# shortcut: money is float (0.1 + 0.2 != 0.3); switch to Decimal when amounts are persisted.

def calculate_metrics(clicks: int, conversions: int, payout: float) -> dict:
    cvr = conversions / clicks if clicks else 0.0
    epc = (conversions * payout) / clicks if clicks else 0.0
    return {
        "clicks": clicks,
        "conversions": conversions,
        "cvr": round(cvr, 3),
        "epc": round(epc, 4),
    }


def build_overview(
    revenue: float,
    traffic_cost: float,
    email_cost: float,
    ai_cost: float,
    infrastructure_cost: float,
    active_campaigns: int,
    clicks: int,
    conversions: int,
) -> dict:
    total_costs = traffic_cost + email_cost + ai_cost + infrastructure_cost
    net_profit = revenue - total_costs
    roi = round(net_profit / total_costs, 2) if total_costs else 0.0
    return {
        "revenue": revenue,
        "traffic_cost": traffic_cost,
        "email_cost": email_cost,
        "ai_cost": ai_cost,
        "infrastructure_cost": infrastructure_cost,
        "net_profit": net_profit,
        "roi": roi,
        "active_campaigns": active_campaigns,
        "clicks": clicks,
        "conversions": conversions,
    }
