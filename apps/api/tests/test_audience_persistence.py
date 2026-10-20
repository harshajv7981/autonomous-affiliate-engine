from sqlalchemy import func, select

from db.models import ConsentRecord, SubscriberModel, SuppressionRecord
from services.seeding import seed_audiences_and_subscribers


def test_audiences_and_subscribers_persist_with_consent_and_suppression(fresh_db):
    first = seed_audiences_and_subscribers(fresh_db)

    assert first["audiences"] == 10
    assert first["subscribers"] == 10000
    assert first["consent_records"] == 10000  # one consent record per subscriber
    assert first["suppression_records"] > 0  # unsubscribed subscribers are suppressed

    # Every suppression maps to an unsubscribed subscriber.
    suppressed_ids = set(fresh_db.scalars(select(SuppressionRecord.subscriber_id)))
    unsubscribed_ids = set(
        fresh_db.scalars(select(SubscriberModel.id).where(SubscriberModel.unsubscribed.is_(True)))
    )
    assert suppressed_ids == unsubscribed_ids


def test_subscriber_seeding_is_idempotent(fresh_db):
    seed_audiences_and_subscribers(fresh_db)
    second = seed_audiences_and_subscribers(fresh_db)

    assert second["subscribers"] == 10000
    assert second["consent_records"] == 10000
    assert fresh_db.scalar(select(func.count()).select_from(ConsentRecord)) == 10000
