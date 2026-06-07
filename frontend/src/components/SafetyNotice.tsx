import type { SafetyPayload } from "../types";

interface SafetyNoticeProps {
  safety: SafetyPayload | null;
}

export function SafetyNotice({ safety }: SafetyNoticeProps) {
  if (!safety || safety.state === "none") {
    return null;
  }

  return (
    <section className={`safety-notice safety-${safety.state}`} aria-live="polite">
      <p className="eyebrow">低打扰提醒</p>
      <h2>系统注意到你现在可能需要缓一下</h2>
      <p>{safety.message || "先深呼吸一下，把下一步缩小到更容易开始的一件事。"}</p>
    </section>
  );
}
