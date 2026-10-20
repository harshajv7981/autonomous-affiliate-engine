from services.analytics import build_overview, calculate_metrics


def test_finance_calculations_are_correct():
    overview = build_overview(
        revenue=250.0,
        traffic_cost=30.0,
        email_cost=15.0,
        ai_cost=10.0,
        infrastructure_cost=20.0,
        active_campaigns=4,
        clicks=400,
        conversions=18,
    )

    assert overview["revenue"] == 250.0
    assert overview["net_profit"] == 175.0
    assert overview["roi"] == 2.33
    assert overview["active_campaigns"] == 4


def test_performance_metrics_are_computed():
    metrics = calculate_metrics(400, 18, 15.0)

    assert metrics["cvr"] == 0.045
    assert metrics["epc"] == 0.675

