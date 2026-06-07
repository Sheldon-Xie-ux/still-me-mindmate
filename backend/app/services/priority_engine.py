from __future__ import annotations


def score_task(
    urgency: int,
    importance: int,
    estimated_minutes: int | None = None,
) -> tuple[float, str, str]:
    bounded_minutes = min(estimated_minutes or 0, 180)
    score = (
        urgency * 0.45
        + importance * 0.45
        - (bounded_minutes / 180) * 0.1
    )

    if score >= 3.8:
        label = "high"
        reason = "This rises to the top because it is urgent and important."
    elif score >= 2.6:
        label = "medium"
        reason = "This matters, but it can follow the most time-sensitive work."
    else:
        label = "low"
        reason = "This can wait until the high-impact items are moving."

    return float(score), label, reason
