import type { TaskItem } from "../types";

interface TodayTasksProps {
  tasks: TaskItem[];
}

export function TodayTasks({ tasks }: TodayTasksProps) {
  return (
    <section className="panel supporting-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">辅助视图</p>
          <h2>任务全貌</h2>
        </div>
        <span className="pill">{tasks.length} 项</span>
      </div>

      <p className="supporting-copy">作为判断依据保留，方便你随时核对。</p>

      {tasks.length === 0 ? (
        <div className="empty-state">
          <p>这里会保留系统拆出来的任务线索。</p>
          <span>它不再主导界面，但会继续作为判断依据陪在旁边。</span>
        </div>
      ) : (
        <div className="task-list">
          {tasks.map((task) => (
            <article key={task.id} className="task-card">
              <div className="task-card-top">
                <h3>{task.title}</h3>
                <span className={`priority-chip priority-${task.priority_label.toLowerCase()}`}>
                  {task.priority_label.toUpperCase()}
                </span>
              </div>
              {task.description ? <p className="task-description">{task.description}</p> : null}
              <p className="task-reason">{task.priority_reason}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
