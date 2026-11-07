import React, { useState } from "react";
import {
  Sparkles,
  Send,
  Cpu,
  Layers,
  MessageSquare,
  ListTodo,
} from "lucide-react";
import type { ExecutionPlan } from "../types";
import { PlanView } from "./PlanView";

interface AIPanelProps {
  currentPlan: ExecutionPlan | null;
  selectedStepIds: Set<string>;
  onToggleStepSelection: (id: string) => void;
  onSelectAllSteps: () => void;
  onDeselectAllSteps: () => void;
  onExecutePlan: (autoApprove: boolean) => void;
  onRejectPlan: () => void;
  onTriggerRepair: (failedStepId: string, errorOutput: string) => void;
  isExecuting: boolean;
  isGeneratingPlan: boolean;
  onGeneratePlan: (task: string, multiAgent: boolean) => void;
  chatMessages: { id: string; sender: "user" | "kodra"; text: string }[];
  onSendChatMessage: (text: string) => void;
}

export const AIPanel: React.FC<AIPanelProps> = ({
  currentPlan,
  selectedStepIds,
  onToggleStepSelection,
  onSelectAllSteps,
  onDeselectAllSteps,
  onExecutePlan,
  onRejectPlan,
  onTriggerRepair,
  isExecuting,
  isGeneratingPlan,
  onGeneratePlan,
  chatMessages,
  onSendChatMessage,
}) => {
  const [activeMode, setActiveMode] = useState<"plan" | "chat">("plan");
  const [multiAgentMode, setMultiAgentMode] = useState<boolean>(true);
  const [inputText, setInputText] = useState("");

  const handleSend = () => {
    const text = inputText.trim();
    if (!text) return;
    setInputText("");

    if (activeMode === "plan") {
      onGeneratePlan(text, multiAgentMode);
    } else {
      onSendChatMessage(text);
    }
  };

  const suggestions = [
    "Build a Python calculator module in calc.py and verify it",
    "Create a modern React card component in src/components/Card.tsx",
    "Run automated test suite to check for errors",
    "Scaffold an authentication service in auth.py with tests",
  ];

  return (
    <aside className="ai-panel">
      <div className="ai-header">
        <div className="ai-header-title">
          <div className="ai-header-icon">
            <Cpu size={16} color="#818cf8" />
          </div>
          <div>
            <strong>KODRA AI</strong>
            <span className="ai-subtitle">LLM Plans • Python Executes</span>
          </div>
        </div>

        <div className="ai-mode-toggles">
          <button
            className={`mode-btn ${activeMode === "plan" ? "active" : ""}`}
            onClick={() => setActiveMode("plan")}
            title="Formulate structured execution plan"
          >
            <ListTodo size={13} />
            <span>Plan & Build</span>
          </button>
          <button
            className={`mode-btn ${activeMode === "chat" ? "active" : ""}`}
            onClick={() => setActiveMode("chat")}
            title="Pair-programming conversation"
          >
            <MessageSquare size={13} />
            <span>Chat</span>
          </button>
        </div>
      </div>

      <div className="ai-subbar">
        <label className="multi-agent-toggle">
          <input
            type="checkbox"
            checked={multiAgentMode}
            onChange={(e) => setMultiAgentMode(e.target.checked)}
          />
          <Layers size={13} color="#818cf8" />
          <span>Multi-Agent Mode (Orchestrator + Specialists)</span>
        </label>
      </div>

      <div className="ai-body">
        {isGeneratingPlan ? (
          <div className="planning-loading-state">
            <div className="pulsing-brain">
              <Sparkles size={28} color="#818cf8" />
            </div>
            <h4>Formulating Execution Plan...</h4>
            <p>
              {multiAgentMode
                ? "Orchestrating research, domain development, tests, and security review..."
                : "Analyzing workspace context and generating structured operation schema..."}
            </p>
          </div>
        ) : activeMode === "plan" && currentPlan ? (
          <PlanView
            plan={currentPlan}
            selectedStepIds={selectedStepIds}
            onToggleStepSelection={onToggleStepSelection}
            onSelectAllSteps={onSelectAllSteps}
            onDeselectAllSteps={onDeselectAllSteps}
            onExecutePlan={onExecutePlan}
            onRejectPlan={onRejectPlan}
            onTriggerRepair={onTriggerRepair}
            isExecuting={isExecuting}
          />
        ) : activeMode === "chat" ? (
          <div className="chat-thread">
            {chatMessages.length === 0 ? (
              <div className="chat-empty-state">
                <MessageSquare size={32} color="#475569" />
                <p>Ask Kodra anything about your architecture, codebase, or tasks.</p>
              </div>
            ) : (
              chatMessages.map((m) => (
                <div key={m.id} className={`chat-bubble ${m.sender}`}>
                  <div className="chat-sender-label">
                    {m.sender === "user" ? "You" : "Kodra AI"}
                  </div>
                  <div className="chat-text">{m.text}</div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="plan-empty-state">
            <div className="big-ai-icon">
              <Sparkles size={24} color="#818cf8" />
            </div>
            <h3>What would you like to build?</h3>
            <p>
              Describe a software engineering task. Kodra will plan the exact filesystem changes and commands, validate security, and execute them upon your approval.
            </p>

            <div className="suggestions-list">
              <span className="suggestions-label">Try an engineering task:</span>
              {suggestions.map((s) => (
                <button
                  key={s}
                  className="suggestion-chip"
                  onClick={() => {
                    setInputText(s);
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="ai-input-area">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={
            activeMode === "plan"
              ? "Describe task (e.g. 'Create a Python calculator in calc.py and run tests')..."
              : "Ask Kodra about your project..."
          }
          rows={3}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />

        <div className="input-bar-footer">
          <span className="input-hint">Shift+Enter for newline</span>
          <button
            className="send-action-btn"
            onClick={handleSend}
            disabled={!inputText.trim() || isGeneratingPlan || isExecuting}
            title="Send (Enter)"
          >
            <Send size={13} />
            <span>{activeMode === "plan" ? "Plan" : "Send"}</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
