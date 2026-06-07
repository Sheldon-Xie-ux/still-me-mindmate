import type { RhythmPayload, SystemObservationPayload } from "../types";

interface SystemObservationCardProps {
  systemObservation: SystemObservationPayload | null;
  rhythm: RhythmPayload | null;
}

function getSafetyStateLabel(safetyState: string | null | undefined) {
  switch (safetyState) {
    case "safe_interrupt":
      return "安全中断";
    case "gentle_nudge":
      return "轻提醒";
    case "none":
      return "状态稳定";
    default:
      return "系统信号";
  }
}

export function SystemObservationCard({
  systemObservation,
  rhythm,
}: SystemObservationCardProps) {
  const suggestion = systemObservation?.suggestion ?? rhythm?.suggestion ?? null;
  const message = systemObservation?.message ?? null;
  const safetyStateLabel = systemObservation ? getSafetyStateLabel(systemObservation.safety_state) : null;

  return (
    <section className="panel judgment-card judgment-card-observation">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">观察</p>
          <h2>系统观察</h2>
        </div>
        {safetyStateLabel ? <span className="pill">{safetyStateLabel}</span> : null}
      </div>

      {suggestion ? (
        <>
          <p className="judgment-summary">{suggestion}</p>
          {message ? <p className="judgment-reason">{message}</p> : null}
          <div className="rhythm-stats">
            <article>
              <strong>{rhythm?.focus_minutes_today ?? 0} 分钟</strong>
              <span>今日专注时长</span>
            </article>
            <article>
              <strong>{rhythm?.completed_tasks_today ?? 0}</strong>
              <span>今日完成任务</span>
            </article>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>系统还在等待更多信号。</p>
          <span>开始一次判断后，这里会显示我对你节奏和推进状态的观察。</span>
        </div>
      )}
    </section>
  );
}
