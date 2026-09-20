def calculate_profit(revenue: float, costs: float, overhead: float = 0.0) -> float:
    return revenue - costs - overhead


def calculate_metrics(clicks: int, conversions: int, conversion_rate: float, payout: float) -> dict:
    cvr = conversions / clicks if clicks else 0.0
    revenue_per_click = (conversions * payout) / clicks if clicks else 0.0
    return {
        "clicks": clicks,
        "conversions": conversions,
        "cvr": round(cvr, 3),
        "epc": float(payout),
        "revenue_per_click": round(revenue_per_click, 4),
    }


def build_overview(
    revenue: float,
    affiliate_commissions: float,
    traffic_cost: float,
    email_cost: float,
    ai_cost: float,
    infrastructure_cost: float,
    active_campaigns: int,
    clicks: int,
    conversions: int,
) -> dict:
    total_costs = affiliate_commissions + traffic_cost + email_cost + ai_cost + infrastructure_cost
    net_profit = revenue - total_costs
    roi = round(net_profit / total_costs, 2) if total_costs else 0.0
    return {
        "revenue": revenue,
        "affiliate_commissions": affiliate_commissions,
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
