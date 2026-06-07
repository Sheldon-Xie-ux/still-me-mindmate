from __future__ import annotations

from sqlmodel import Session

from app.schemas import (
    ChatResponse,
    CurrentPriorityPayload,
    FocusRecommendation,
    NextActionPayload,
    RhythmPayload,
    SafetyPayload,
    SystemObservationPayload,
    TaskOut,
)
from app.services.analytics_service import touch_analytics
from app.services.safety_guard import evaluate_safety_state
from app.services.task_service import upsert_tasks_from_message


def build_chat_response(session: Session, message: str) -> ChatResponse:
    analytics = touch_analytics(session)
    safety_result = evaluate_safety_state(message, analytics.uninterrupted_minutes)
    completed_tasks_today = 0

    if safety_result["state"] == "safe_interrupt":
        return ChatResponse(
            reply=safety_result["message"] or "我先陪你停一下。",
            tasks=[],
            focus=FocusRecommendation(
                recommended_task_id=None,
                summary="现在先不安排焦点任务。",
            ),
            rhythm=RhythmPayload(
                focus_minutes_today=analytics.focus_minutes_today,
                completed_tasks_today=completed_tasks_today,
                suggestion="先暂停一下，联系可信任的人或身边支持资源，当前不继续安排任务。",
            ),
            safety=SafetyPayload(
                state="safe_interrupt",
                message=safety_result["message"],
            ),
            current_priority=CurrentPriorityPayload(
                title=None,
                reason="现在最优先的不是继续拆任务，而是先确保你被照顾和支持。",
            ),
            next_action=NextActionPayload(
                label="先联系身边支持",
                detail="请立刻联系一位你信任的人，或尽快联系当地紧急援助与心理支持资源，先不要独自扛着。",
            ),
            system_observation=SystemObservationPayload(
                suggestion="检测到高风险信号，系统已切换为安全优先，不继续安排执行计划。",
                safety_state="safe_interrupt",
                message=safety_result["message"],
            ),
        )

    tasks = upsert_tasks_from_message(session, message)
    recommended_task = tasks[0] if tasks else None

    if recommended_task is None:
        reply = "我先帮你记下来了，但这条消息里还没有拆出明确任务。"
        focus_summary = "暂时没有推荐焦点任务。"
    else:
        reply = f"我先帮你拆成 {len(tasks)} 个任务，并按轻重缓急排好了顺序。"
        focus_summary = f"建议先处理：{recommended_task.title}"

    safety_message = safety_result["message"]
    if safety_result["state"] == "gentle_nudge":
        rhythm_suggestion = "你已经连续忙了一段时间了，先放慢一点，休息几分钟后只推进一件最小任务。"
    else:
        safety_message = "先按一个番茄钟推进，做完再一起看下一步。"
        rhythm_suggestion = "建议先专注一个番茄钟，做完当前最重要的一件事再切换。"

    current_priority = _build_current_priority(recommended_task, tasks)
    next_action = _build_next_action(recommended_task, safety_result["state"])
    system_observation = _build_system_observation(
        safety_state=safety_result["state"],
        safety_message=safety_message,
        rhythm_suggestion=rhythm_suggestion,
    )

    return ChatResponse(
        reply=reply,
        tasks=[TaskOut.model_validate(task, from_attributes=True) for task in tasks],
        focus=FocusRecommendation(
            recommended_task_id=recommended_task.id if recommended_task else None,
            summary=focus_summary,
        ),
        rhythm=RhythmPayload(
            focus_minutes_today=analytics.focus_minutes_today,
            completed_tasks_today=completed_tasks_today,
            suggestion=rhythm_suggestion,
        ),
        safety=SafetyPayload(
            state=safety_result["state"],
            message=safety_message,
        ),
        current_priority=current_priority,
        next_action=next_action,
        system_observation=system_observation,
    )


def _build_current_priority(recommended_task, tasks) -> CurrentPriorityPayload:
    if recommended_task is None:
        return CurrentPriorityPayload(
            title=None,
            reason="我已经先记录你的上下文，但当前还没有识别出足够明确的可执行任务。",
        )

    reason = recommended_task.priority_reason
    if len(tasks) > 1:
        reason = f"{reason}，而且它是当前 {len(tasks)} 个任务里最该先推进的一项。"

    return CurrentPriorityPayload(
        title=recommended_task.title,
        reason=reason,
    )


def _build_next_action(recommended_task, safety_state: str) -> NextActionPayload:
    if recommended_task is None:
        return NextActionPayload(
            label="补一句最想推进的事",
            detail="直接告诉我你现在最想完成的一件事，或给我一个截止时间，我就能继续帮你拆解下一步。",
        )

    if safety_state == "gentle_nudge":
        return NextActionPayload(
            label=f"只启动：{recommended_task.title}",
            detail="先休息几分钟，然后只花 5 分钟把这件事的第一步做出来，不需要一次做完。",
        )

    return NextActionPayload(
        label=f"先推进：{recommended_task.title}",
        detail="先开一个番茄钟，只做这件事的最小可交付动作，完成后再回来决定下一步。",
    )


def _build_system_observation(
    safety_state: str,
    safety_message: str | None,
    rhythm_suggestion: str,
) -> SystemObservationPayload:
    if safety_state == "gentle_nudge":
        suggestion = "我观察到你的节奏已经偏满，接下来更适合减速并缩小动作范围。"
    else:
        suggestion = "当前节奏可继续推进，但最好一次只盯住一件最重要的事。"

    return SystemObservationPayload(
        suggestion=suggestion,
        safety_state=safety_state,
        message=safety_message or rhythm_suggestion,
    )
