from agents.optimizer_agent.graph import decide


def test_scale_on_strong_cvr_and_positive_contribution():
    assert decide({"cvr": 0.05, "conversions": 5, "clicks": 100}, 42.0)["action"] == "SCALE"


def test_pause_on_negative_contribution():
    assert decide({"cvr": 0.04, "conversions": 2, "clicks": 100}, -5.0)["action"] == "PAUSE"


def test_kill_when_no_conversions():
    assert decide({"cvr": 0.0, "conversions": 0, "clicks": 50}, -1.0)["action"] == "KILL"


def test_retry_when_no_clicks():
    assert decide({"cvr": 0.0, "conversions": 0, "clicks": 0}, 0.0)["action"] == "RETRY"


def test_test_when_positive_but_weak_cvr():
    assert decide({"cvr": 0.01, "conversions": 1, "clicks": 100}, 3.0)["action"] == "TEST"


def test_high_complaints_pause_even_when_profitable():
    result = decide({"cvr": 0.05, "conversions": 5, "clicks": 100, "complaint_rate": 0.002}, 50.0)
    assert (result["action"], result["reason"]) == ("PAUSE", "COMPLAINT_RATE_HIGH")


def test_high_unsubscribes_reduce_volume():
    result = decide({"cvr": 0.05, "conversions": 5, "clicks": 100, "unsubscribe_rate": 0.01}, 50.0)
    assert result["action"] == "REDUCE"


def test_decisions_are_recommendations_only():
    result = decide({"cvr": 0.05, "conversions": 5, "clicks": 100}, 42.0)
    assert result["mode"] == "recommendation"
    assert result["applied"] is False
