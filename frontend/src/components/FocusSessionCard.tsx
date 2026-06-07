import type { FocusRecommendation, FocusSession, TaskItem } from "../types";

interface FocusSessionCardProps {
  focus: FocusRecommendation | null;
  tasks: TaskItem[];
  activeSession: FocusSession | null;
  starting: boolean;
  onStartFocus: (taskId: number) => void;
}

export function FocusSessionCard({
  focus,
  tasks,
  activeSession,
  starting,
  onStartFocus,
}: FocusSessionCardProps) {
  const recommendedTask = tasks.find((task) => task.id === focus?.recommended_task_id) ?? null;

  return (
    <section className="panel focus-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">专注</p>
          <h2>专注模式</h2>
        </div>
        <span className="pill">25 分钟</span>
      </div>

      {recommendedTask ? (
        <>
          <p className="focus-title">{recommendedTask.title}</p>
          <p className="focus-summary">
            {focus?.summary || "先从这一件开始，把范围收小，尽量一口气推进完。"}
          </p>
          <button type="button" onClick={() => onStartFocus(recommendedTask.id)} disabled={starting}>
            {starting ? "启动中..." : "开始专注"}
          </button>
          {activeSession ? (
            <p className="focus-session-state">
              当前专注状态：{activeSession.status}，时长 {activeSession.duration_minutes} 分钟。
            </p>
          ) : null}
        </>
      ) : (
        <div className="empty-state">
          <p>还没有推荐的专注任务。</p>
          <span>发送下一条消息后，我会帮你选出最适合先开始的一项。</span>
        </div>
      )}
    </section>
  );
}
