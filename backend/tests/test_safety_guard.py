from app.services.safety_guard import evaluate_safety_state


def test_crisis_language_returns_safe_interrupt():
    result = evaluate_safety_state("我不想活了，别再规划任务了", uninterrupted_minutes=10)

    assert result["state"] == "safe_interrupt"


def test_overload_language_returns_gentle_nudge():
    result = evaluate_safety_state(
        "我压力很大，已经连续忙了很久",
        uninterrupted_minutes=20,
    )

    assert result["state"] == "gentle_nudge"


def test_long_uninterrupted_time_alone_returns_gentle_nudge():
    result = evaluate_safety_state(
        "继续做事吧",
        uninterrupted_minutes=75,
    )

    assert result["state"] == "gentle_nudge"
