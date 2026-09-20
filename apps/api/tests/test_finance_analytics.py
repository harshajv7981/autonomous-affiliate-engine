from services.analytics import build_overview, calculate_metrics, calculate_profit


def test_finance_calculations_are_correct():
    overview = build_overview(
        revenue=250.0,
        affiliate_commissions=80.0,
        traffic_cost=30.0,
        email_cost=15.0,
        ai_cost=10.0,
        infrastructure_cost=20.0,
        active_campaigns=4,
        clicks=400,
        conversions=18,
    )

    assert overview["revenue"] == 250.0
    assert overview["net_profit"] == 95.0
    assert overview["roi"] == 0.61
    assert overview["active_campaigns"] == 4


def test_performance_metrics_are_computed():
    metrics = calculate_metrics(400, 18, 0.04, 15.0)

    assert metrics["cvr"] == 0.045
    assert metrics["epc"] == 15.0
    assert metrics["revenue_per_click"] == 0.675


def test_profit_calculation_handles_negative_profit():
    profit = calculate_profit(100.0, 75.0, 40.0)

    assert profit == -15.0
