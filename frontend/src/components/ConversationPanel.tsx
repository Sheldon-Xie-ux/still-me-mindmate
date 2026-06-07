interface ConversationPanelProps {
  draft: string;
  reply: string;
  loading: boolean;
  onDraftChange: (value: string) => void;
  onSubmit: () => void;
}

export function ConversationPanel({
  draft,
  reply,
  loading,
  onDraftChange,
  onSubmit,
}: ConversationPanelProps) {
  return (
    <section className="panel panel-conversation">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">上下文入口</p>
          <h2>告诉我现在发生了什么</h2>
        </div>
      </div>

      <div className="assistant-reply" aria-live="polite">
        <p className="assistant-label">判断回声</p>
        <p>
          {reply ||
            "你可以把最近的情况、想推进的目标、现实限制，或者卡住你的地方一起告诉我。我会先判断什么最重要，再给出当下最值得开始的一步。"}
        </p>
      </div>

      <label className="composer">
        <span className="sr-only">当前情况</span>
        <textarea
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="最近发生的情况、你想推进的目标、不能忽略的限制、眼下的阻碍，都可以直接说给我。"
          rows={6}
        />
      </label>

      <div className="composer-actions">
        <p className="composer-hint">不必先整理成任务清单，混合信息也可以。我会替你收束判断。</p>
        <button type="button" onClick={onSubmit} disabled={loading || draft.trim().length === 0}>
          {loading ? "判断中..." : "开始判断"}
        </button>
      </div>
    </section>
  );
}
