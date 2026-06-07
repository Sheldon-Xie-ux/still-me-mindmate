from __future__ import annotations


CRISIS_PHRASES = ["不想活", "自杀", "伤害自己", "结束自己"]
OVERLOAD_PHRASES = ["压力很大", "撑不住", "太累了", "焦虑", "崩溃"]


def evaluate_safety_state(message: str, uninterrupted_minutes: int) -> dict[str, str | None]:
    if any(phrase in message for phrase in CRISIS_PHRASES):
        return {
            "state": "safe_interrupt",
            "message": "我先不继续帮你规划任务了。你现在值得先被照顾，请立刻联系身边可信任的人，或尽快联系当地紧急援助与心理支持资源。",
        }

    if uninterrupted_minutes >= 75 or any(
        phrase in message for phrase in OVERLOAD_PHRASES
    ):
        return {
            "state": "gentle_nudge",
            "message": "你已经连续撑了很久了，我们先把节奏放慢一点。建议先暂停几分钟，喝口水、活动一下，再只挑一件最小的事继续。",
        }

    return {"state": "none", "message": None}
