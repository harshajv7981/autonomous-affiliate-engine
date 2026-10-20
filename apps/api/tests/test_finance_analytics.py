from services.analytics import build_overview, calculate_metrics, calculate_rates


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


def test_rates_and_contribution_per_thousand():
    funnel = {
        "sent": 10000, "delivered": 9700, "bounces": 300, "clicks": 380,
        "conversions": 14, "unsubscribes": 20, "complaints": 2,
    }
    rates = calculate_rates(funnel, revenue=420.0, net=210.0)

    assert rates["ctr"] == round(380 / 9700, 4)
    assert rates["cvr"] == round(14 / 380, 4)
    assert rates["epc"] == round(420 / 380, 4)
    assert rates["bounce_rate"] == 0.03
    assert rates["net_contribution_per_1000"] == 21.0
    assert rates["complaint_rate"] == round(2 / 9700, 5)


def test_rates_handle_empty_funnel():
    rates = calculate_rates({}, revenue=0.0, net=0.0)
    assert all(value == 0.0 for value in rates.values())

