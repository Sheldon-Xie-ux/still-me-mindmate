import { useEffect, useMemo, useState } from "react";

import {
  getResearchBrief,
  getResearchEvidence,
  getResearchHypotheses,
  getResearchQuestions,
  startResearchRun,
} from "../lib/api";
import type {
  EvidenceCard,
  Hypothesis,
  ResearchBrief,
  ResearchQuestion,
  ResearchRunCreateResponse,
} from "../types";

export function ResearchLab() {
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState<number | null>(null);
  const [runResult, setRunResult] = useState<ResearchRunCreateResponse | null>(null);
  const [evidence, setEvidence] = useState<EvidenceCard[]>([]);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [brief, setBrief] = useState<ResearchBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadResearchLab() {
      try {
        const questionPayload = await getResearchQuestions();
        if (!active) {
          return;
        }
        setQuestions(questionPayload.questions);
        setSelectedQuestionId(questionPayload.questions[0]?.id ?? null);
      } catch {
        if (active) {
          setError("研究问题队列暂时无法加载。");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadResearchLab();

    return () => {
      active = false;
    };
  }, []);

  const selectedQuestion = useMemo(
    () => questions.find((question) => question.id === selectedQuestionId) ?? questions[0] ?? null,
    [questions, selectedQuestionId],
  );

  async function handleRunResearch() {
    if (!selectedQuestion) {
      return;
    }

    setRunning(true);
    setError("");

    try {
      const result = await startResearchRun(selectedQuestion.id);
      const [evidencePayload, hypothesesPayload, briefPayload] = await Promise.all([
        getResearchEvidence(selectedQuestion.id),
        getResearchHypotheses(),
        getResearchBrief(),
      ]);
      setRunResult(result);
      setEvidence(evidencePayload.evidence);
      setHypotheses(hypothesesPayload.hypotheses);
      setBrief(briefPayload);
    } catch {
      setError("这次研究循环没有跑通，请稍后再试。");
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="research-lab">
      <div className="research-header panel">
        <div>
          <p className="eyebrow">MindMate AutoResearch</p>
          <h2>Research Lab</h2>
          <p>
            自动提出问题、整理证据、保留高价值假设；只把高敏感或低可信结论交给人类判断。
          </p>
        </div>
        <button type="button" onClick={handleRunResearch} disabled={loading || running || !selectedQuestion}>
          {running ? "研究中..." : "运行研究"}
        </button>
      </div>

      {error ? <section className="inline-error">{error}</section> : null}

      {runResult ? (
        <section className="research-run-summary panel" aria-live="polite">
          <span>运行 #{runResult.run_id}</span>
          <strong>状态：{runResult.status}</strong>
          <span>本次新增证据 {runResult.evidence_created} 条</span>
          <span>新增假设 {runResult.hypotheses_created} 条</span>
        </section>
      ) : null}

      <div className="research-grid">
        <section className="panel research-queue">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Queue</p>
              <h2>研究问题队列</h2>
            </div>
            <span className="pill">{questions.length} 个问题</span>
          </div>

          <div className="research-question-list">
            {questions.map((question) => (
              <button
                className={`question-row ${question.id === selectedQuestion?.id ? "question-row-active" : ""}`}
                key={question.id}
                type="button"
                onClick={() => setSelectedQuestionId(question.id)}
              >
                <strong>{question.title}</strong>
                <span>{question.theme} · priority {question.priority}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="panel evidence-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Evidence</p>
              <h2>证据卡片</h2>
            </div>
            <span className="pill">{evidence.length} 条</span>
          </div>

          {evidence.length ? (
            <div className="evidence-list">
              {evidence.map((card) => (
                <article className="evidence-card" key={card.id}>
                  <div className="card-topline">
                    <span>{card.source.source_type}</span>
                    <span>{card.stance}</span>
                  </div>
                  <h3>{card.claim}</h3>
                  <p>{card.summary}</p>
                  <p className="card-meta">
                    强度 {card.evidence_strength} · 相关性 {card.relevance_score} · {card.risk_domain}
                  </p>
                  <a href={card.source.url}>{card.source.title}</a>
                  <p className="limitations">{card.limitations}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>还没有证据卡片。</p>
              <span>运行一次研究后，这里会显示来源、立场、强度和限制。</span>
            </div>
          )}
        </section>

        <section className="panel hypothesis-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Hypotheses</p>
              <h2>高分假设</h2>
            </div>
            <span className="pill">{hypotheses.length} 条</span>
          </div>

          {hypotheses.length ? (
            <div className="hypothesis-list">
              {hypotheses.map((hypothesis) => (
                <article className="hypothesis-card" key={hypothesis.id}>
                  <div className="score-ring">{hypothesis.overall_score}</div>
                  <div>
                    <h3>{hypothesis.title}</h3>
                    <p>{hypothesis.statement}</p>
                    <p className="card-meta">
                      {hypothesis.status} · 证据 {hypothesis.evidence_score} · 产品价值{" "}
                      {hypothesis.product_value_score} · 可实现{" "}
                      {hypothesis.engineering_feasibility_score}
                    </p>
                    <p className="limitations">{hypothesis.rationale}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>还没有形成假设。</p>
              <span>研究循环会把证据沉淀成可产品化的认知保护原则。</span>
            </div>
          )}
        </section>

        <section className="panel brief-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Brief</p>
              <h2>关键报告</h2>
            </div>
          </div>

          {brief ? (
            <>
              <h3>{brief.title}</h3>
              <p>{brief.summary}</p>
              <div className="brief-columns">
                <BriefList title="设计启发" items={brief.design_implications} />
                <BriefList title="需要人类复核" items={brief.expert_review_queue} />
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>关键报告等待生成。</p>
              <span>每次研究完成后，我会把关键变化整理成可读摘要。</span>
            </div>
          )}
        </section>
      </div>
    </section>
  );
}

function BriefList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
