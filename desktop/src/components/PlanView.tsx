import React from "react";
import {
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  FilePlus,
  FileEdit,
  Trash2,
  Terminal,
  FolderPlus,
  Wrench,
  AlertTriangle,
} from "lucide-react";
import type { ExecutionPlan, OperationType, StepStatus } from "../types";

interface PlanViewProps {
  plan: ExecutionPlan;
  selectedStepIds: Set<string>;
  onToggleStepSelection: (id: string) => void;
  onSelectAllSteps: () => void;
  onDeselectAllSteps: () => void;
  onExecutePlan: (autoApprove: boolean) => void;
  onRejectPlan: () => void;
  onTriggerRepair: (failedStepId: string, errorOutput: string) => void;
  isExecuting: boolean;
}

export const PlanView: React.FC<PlanViewProps> = ({
  plan,
  selectedStepIds,
  onToggleStepSelection,
  onSelectAllSteps,
  onDeselectAllSteps,
  onExecutePlan,
  onRejectPlan,
  onTriggerRepair,
  isExecuting,
}) => {
  const getOpIcon = (op: OperationType) => {
    switch (op) {
      case "create_file":
        return <FilePlus size={13} color="#4ade80" />;
      case "modify_file":
        return <FileEdit size={13} color="#60a5fa" />;
      case "delete_file":
        return <Trash2 size={13} color="#f87171" />;
      case "create_dir":
        return <FolderPlus size={13} color="#fbbf24" />;
      case "run_command":
        return <Terminal size={13} color="#c084fc" />;
      default:
        return <Wrench size={13} color="#94a3b8" />;
    }
  };

  const getStatusIcon = (status: StepStatus) => {
    switch (status) {
      case "success":
        return <CheckCircle2 size={15} color="#4ade80" />;
      case "failed":
        return <XCircle size={15} color="#f87171" />;
      case "running":
        return <div className="spinner-mini" />;
      case "skipped":
        return <span className="status-badge skipped">SKIPPED</span>;
      default:
        return <Clock size={15} color="#64748b" />;
    }
  };

  const failedStep = plan.steps.find((s) => s.status === "failed");

  return (
    <div className="plan-view-container">
      <div className="plan-header-card">
        <div className="plan-badge-row">
          <span className="plan-type-badge">
            {plan.metadata?.is_repair ? "SELF-HEALING REPAIR PLAN" : "STRUCTURED EXECUTION PLAN"}
          </span>
          <span className={`plan-status-badge ${plan.status}`}>
            {plan.status.toUpperCase()}
          </span>
          {plan.metadata?.orchestration && (
            <span className="plan-orchestration-badge">MULTI-AGENT COLLABORATION</span>
          )}
        </div>

        <h4 className="plan-task-title">{plan.task}</h4>
        <p className="plan-summary">{plan.summary}</p>

        {plan.metadata?.diagnosis && (
          <div className="diagnosis-box">
            <AlertTriangle size={14} color="#f59e0b" />
            <span>{plan.metadata.diagnosis}</span>
          </div>
        )}

        <div className="plan-policy-indicator">
          <Shield size={13} color="#22c55e" />
          <span>Security Policy: Workspace Containment Verified</span>
        </div>
      </div>

      <div className="plan-steps-list">
        <div className="steps-list-header">
          <span>PROPOSED OPERATIONS ({plan.steps.length})</span>
          {plan.status === "draft" && !isExecuting && (
            <div className="steps-select-controls">
              <button className="text-btn" onClick={onSelectAllSteps}>
                Select All
              </button>
              <span className="sep">•</span>
              <button className="text-btn" onClick={onDeselectAllSteps}>
                Clear
              </button>
            </div>
          )}
        </div>

        {plan.steps.map((step, idx) => {
          const isSelected = selectedStepIds.has(step.id);

          return (
            <div
              key={step.id}
              className={`step-item ${step.status} ${isSelected ? "selected" : ""}`}
            >
              <div className="step-item-main">
                {plan.status === "draft" && !isExecuting ? (
                  <input
                    type="checkbox"
                    className="step-checkbox"
                    checked={isSelected}
                    onChange={() => onToggleStepSelection(step.id)}
                  />
                ) : (
                  <div className="step-status-icon">{getStatusIcon(step.status)}</div>
                )}

                <div className="step-index">#{idx + 1}</div>

                <div className="step-details">
                  <div className="step-title-row">
                    <span className="step-title">{step.title}</span>
                    <span className={`step-risk ${step.risk_level}`}>
                      {step.risk_level.toUpperCase()} RISK
                    </span>
                  </div>

                  <div className="step-op-row">
                    <span className="step-op-badge">
                      {getOpIcon(step.operation)}
                      <span>{step.operation}</span>
                    </span>
                    <span className="step-target">
                      {step.path || step.command || "N/A"}
                    </span>
                  </div>

                  {step.description && (
                    <p className="step-desc">{step.description}</p>
                  )}

                  {step.content && (
                    <details className="step-code-preview">
                      <summary>Preview payload ({step.content.length} chars)</summary>
                      <pre>{step.content.slice(0, 500)}{step.content.length > 500 ? "..." : ""}</pre>
                    </details>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Failure & Self-Healing Action Prompt */}
      {failedStep && plan.status === "failed" && (
        <div className="healer-trigger-card">
          <div className="healer-title">
            <AlertTriangle size={15} color="#ef4444" />
            <span>Failure Detected on #{failedStep.title}</span>
          </div>
          <p className="healer-desc">
            Kodra can analyze this execution error, diagnose the root cause, and propose a self-healing repair plan.
          </p>
          <button
            className="healer-btn"
            onClick={() => onTriggerRepair(failedStep.id, plan.metadata?.error || "Step execution error")}
          >
            <Wrench size={14} />
            <span>Generate Self-Healing Repair Plan</span>
          </button>
        </div>
      )}

      {/* Plan Approval & Execution Action Bar */}
      {plan.status === "draft" && !isExecuting && (
        <div className="plan-actions-bar">
          <button
            className="action-btn primary"
            onClick={() => onExecutePlan(true)}
            title="Approve all operations and execute plan"
          >
            <Play size={14} />
            <span>Approve & Execute All</span>
          </button>

          {selectedStepIds.size > 0 && selectedStepIds.size < plan.steps.length && (
            <button
              className="action-btn secondary"
              onClick={() => onExecutePlan(false)}
              title="Execute only selected approved operations"
            >
              <Play size={14} />
              <span>Execute Selected ({selectedStepIds.size})</span>
            </button>
          )}

          <button className="action-btn danger" onClick={onRejectPlan}>
            <span>Reject Plan</span>
          </button>
        </div>
      )}
    </div>
  );
};
