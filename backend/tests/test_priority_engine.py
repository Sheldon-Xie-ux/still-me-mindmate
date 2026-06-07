from app.services.priority_engine import score_task


def test_score_task_marks_urgent_and_high_priority():
    score, label, reason = score_task(
        urgency=5,
        importance=5,
        estimated_minutes=30,
    )

    assert score > 0
    assert label == "high"
    assert "urgent" in reason.lower()
