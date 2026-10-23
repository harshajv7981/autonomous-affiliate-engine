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


def calculate_rates(funnel: dict, revenue: float, net: float) -> dict:
    """CTR/CVR/EPC, delivery-health rates, and the primary KPI:
    net contribution per 1,000 eligible recipients."""
    sent = funnel.get("sent", 0)
    delivered = funnel.get("delivered", 0)
    clicks = funnel.get("clicks", 0)

    def ratio(numerator: float, denominator: float, digits: int = 4) -> float:
        return round(numerator / denominator, digits) if denominator else 0.0

    return {
        "ctr": ratio(clicks, delivered),
        "cvr": ratio(funnel.get("conversions", 0), clicks),
        "epc": ratio(revenue, clicks),
        "bounce_rate": ratio(funnel.get("bounces", 0), sent),
        "unsubscribe_rate": ratio(funnel.get("unsubscribes", 0), delivered),
        "complaint_rate": ratio(funnel.get("complaints", 0), delivered, 5),
        "net_contribution_per_1000": round(net / sent * 1000, 2) if sent else 0.0,
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
