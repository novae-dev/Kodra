import React, { useRef, useEffect } from "react";
import { Terminal, Trash2, ChevronUp, ChevronDown } from "lucide-react";

export interface LogEntry {
  id: string;
  type: "command" | "stdout" | "stderr" | "info" | "success" | "error";
  text: string;
  timestamp: string;
}

interface TerminalPanelProps {
  logs: LogEntry[];
  onClear: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export const TerminalPanel: React.FC<TerminalPanelProps> = ({
  logs,
  onClear,
  isOpen,
  onToggle,
}) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, isOpen]);

  return (
    <div className={`terminal-panel ${isOpen ? "open" : "collapsed"}`}>
      <div className="terminal-header" onClick={onToggle}>
        <div className="terminal-title">
          <Terminal size={13} color="#818cf8" />
          <span>KODRA EXECUTION ENGINE TERMINAL</span>
          <span className="log-count">({logs.length} logs)</span>
        </div>

        <div className="terminal-controls" onClick={(e) => e.stopPropagation()}>
          <button className="icon-mini-btn" onClick={onClear} title="Clear Terminal">
            <Trash2 size={13} />
          </button>
          <button className="icon-mini-btn" onClick={onToggle} title={isOpen ? "Minimize" : "Expand"}>
            {isOpen ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="terminal-body">
          {logs.length === 0 ? (
            <div className="terminal-empty">Execution output will stream here in real time...</div>
          ) : (
            logs.map((log) => {
              let colorClass = "log-info";
              let prefix = "ℹ ";
              if (log.type === "command") {
                colorClass = "log-command";
                prefix = "$ ";
              } else if (log.type === "success") {
                colorClass = "log-success";
                prefix = "✔ ";
              } else if (log.type === "error" || log.type === "stderr") {
                colorClass = "log-error";
                prefix = "✖ ";
              } else if (log.type === "stdout") {
                colorClass = "log-stdout";
                prefix = "  ";
              }

              return (
                <div key={log.id} className={`terminal-line ${colorClass}`}>
                  <span className="log-time">[{log.timestamp}]</span>
                  <span className="log-prefix">{prefix}</span>
                  <span className="log-text">{log.text}</span>
                </div>
              );
            })
          )}
          <div ref={terminalEndRef} />
        </div>
      )}
    </div>
  );
};
