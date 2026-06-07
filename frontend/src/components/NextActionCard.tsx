import type { FocusRecommendation, FocusSession, NextActionPayload, TaskItem } from "../types";

interface NextActionCardProps {
  focus: FocusRecommendation | null;
  nextAction: NextActionPayload | null;
  tasks: TaskItem[];
  activeSession: FocusSession | null;
  starting: boolean;
  onStartFocus: (taskId: number) => void;
}

export function NextActionCard({
  focus,
  nextAction,
  tasks,
  activeSession,
  starting,
  onStartFocus,
}: NextActionCardProps) {
  const recommendedTask =
    tasks.find((task) => task.id === focus?.recommended_task_id) ?? tasks[0] ?? null;
  const title = nextAction?.label ?? recommendedTask?.title ?? null;
  const detail = nextAction?.detail ?? focus?.summary ?? "先动起来，不再继续扩展范围。";

  return (
    <section className="panel judgment-card judgment-card-action">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">行动</p>
          <h2>现在就开始</h2>
        </div>
        <span className="pill">25 分钟</span>
      </div>

      {title ? (
        <>
          <p className="judgment-kicker">先把动作缩到一个可以马上起步的切口。</p>
          <h3 className="judgment-title">{title}</h3>
          <p className="judgment-summary">{detail}</p>
          {recommendedTask ? (
            <button type="button" onClick={() => onStartFocus(recommendedTask.id)} disabled={starting}>
              {starting ? "启动中..." : "开始专注"}
            </button>
          ) : null}
          {activeSession ? (
            <p className="focus-session-state">
              当前专注状态：{activeSession.status}，时长 {activeSession.duration_minutes} 分钟。
            </p>
          ) : null}
        </>
      ) : (
        <div className="empty-state">
          <p>还没有可执行的下一步。</p>
          <span>一旦收到上下文，我会把建议收敛成一个可以立刻开始的动作。</span>
        </div>
      )}
    </section>
  );
}
