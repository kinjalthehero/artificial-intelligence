import type { AgentStep } from '../../types';

const AGENTS = ['planner', 'retriever', 'reasoning', 'response', 'verification'] as const;

const AGENT_LABELS: Record<string, string> = {
  planner: 'Plan',
  retriever: 'Retrieve',
  reasoning: 'Reason',
  response: 'Respond',
  verification: 'Verify',
};

interface AgentWorkflowProps {
  steps: AgentStep[];
  currentAgent: string | null;
}

export function AgentWorkflow({ steps, currentAgent }: AgentWorkflowProps) {
  if (steps.length === 0 && !currentAgent) return null;

  return (
    <div
      className="flex flex-wrap items-center gap-1.5 px-3 py-2 rounded-lg text-xs mb-2"
      style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
    >
      <span className="font-medium mr-1" style={{ color: 'var(--color-text-secondary)' }}>
        Agents:
      </span>
      {AGENTS.map((agent, idx) => {
        const step = steps.find((s) => s.agent === agent);
        const isCurrent = currentAgent === agent;
        const isDone = !!step;

        return (
          <span key={agent} className="flex items-center gap-1">
            {idx > 0 && (
              <span style={{ color: 'var(--color-text-tertiary)' }}>&rarr;</span>
            )}
            <span
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium"
              style={{
                backgroundColor: isDone
                  ? 'var(--color-accent)'
                  : isCurrent
                  ? 'var(--color-bg-tertiary)'
                  : 'transparent',
                color: isDone
                  ? 'var(--color-text-on-primary)'
                  : isCurrent
                  ? 'var(--color-text-primary)'
                  : 'var(--color-text-tertiary)',
                border: isCurrent && !isDone ? '1px solid var(--color-accent)' : 'none',
              }}
            >
              {isDone && <CheckIcon />}
              {isCurrent && !isDone && <span className="agent-pulse">●</span>}
              {AGENT_LABELS[agent]}
              {isDone && step && (
                <span style={{ opacity: 0.8, fontSize: '0.65rem' }}>
                  {step.duration_ms}ms
                </span>
              )}
            </span>
          </span>
        );
      })}
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
