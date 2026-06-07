import type { RhythmPayload } from "../types";

interface DailyRhythmCardProps {
  rhythm: RhythmPayload | null;
}

export function DailyRhythmCard({ rhythm }: DailyRhythmCardProps) {
  return (
    <section className="panel rhythm-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">节奏</p>
          <h2>今日节奏</h2>
        </div>
      </div>

      {rhythm ? (
        <>
          <p className="rhythm-suggestion">{rhythm.suggestion}</p>
          <div className="rhythm-stats">
            <article>
              <strong>{rhythm.focus_minutes_today} 分钟</strong>
              <span>今日专注时长</span>
            </article>
            <article>
              <strong>{rhythm.completed_tasks_today}</strong>
              <span>今日完成任务</span>
            </article>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>还没有今日节奏摘要。</p>
          <span>收到第一条后端响应后，这里会显示你今天的推进状态。</span>
        </div>
      )}
    </section>
  );
}
