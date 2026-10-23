from simulator.events import SimulationRates, simulate_campaign_outcome


class _Offer:
    conversion_rate = 0.05
    payout = 30.0


def test_funnel_is_monotonic_and_deterministic():
    offer = _Offer()
    first = simulate_campaign_outcome(1000, offer)
    second = simulate_campaign_outcome(1000, offer)

    assert first == second  # deterministic
    assert first["sent"] >= first["delivered"] >= first["clicks"] >= first["conversions"]
    assert first["conversions"] > 0
    assert first["commission"] == round(first["conversions"] * offer.payout, 2)
    assert first["bounces"] == first["sent"] - first["delivered"]
    assert first["unsubscribes"] >= 0 and first["complaints"] >= 0
    assert first["is_simulated"] is True


def test_rates_are_configurable():
    offer = _Offer()
    low = simulate_campaign_outcome(1000, offer, SimulationRates(click_rate=0.0))

    assert low["clicks"] == 0
    assert low["conversions"] == 0
    assert low["commission"] == 0.0
