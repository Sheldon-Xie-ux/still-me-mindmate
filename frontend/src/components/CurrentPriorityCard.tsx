import type { CurrentPriorityPayload, FocusRecommendation, TaskItem } from "../types";

interface CurrentPriorityCardProps {
  currentPriority: CurrentPriorityPayload | null;
  tasks: TaskItem[];
  focus: FocusRecommendation | null;
}

export function CurrentPriorityCard({ currentPriority, tasks, focus }: CurrentPriorityCardProps) {
  const prioritizedTask =
    tasks.find((task) => task.id === focus?.recommended_task_id) ?? tasks[0] ?? null;
  const title = currentPriority?.title ?? prioritizedTask?.title ?? null;
  const summary = currentPriority ? null : prioritizedTask?.description ?? null;
  const reason = currentPriority?.reason ?? prioritizedTask?.priority_reason ?? null;

  return (
    <section className="panel judgment-card judgment-card-priority">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">判断</p>
          <h2>当前最重要的一件事</h2>
        </div>
        <span className="pill">{tasks.length} 条线索</span>
      </div>

      {title ? (
        <>
          <h3 className="judgment-title">{title}</h3>
          {summary ? (
            <p className="judgment-summary">{summary}</p>
          ) : null}
          {reason ? <p className="judgment-reason">{reason}</p> : null}
        </>
      ) : (
        <div className="empty-state">
          <p>判断入口已经准备好。</p>
          <span>告诉我你眼下的情况后，我会先指出最值得抓住的一件事。</span>
        </div>
      )}
    </section>
  );
}
