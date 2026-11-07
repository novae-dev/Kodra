import React, { useState } from "react";
import {
  FileCode2,
  FileText,
  Folder,
  Layers,
  Clock,
  Plus,
  CheckCircle2,
  XCircle,
  Search,
} from "lucide-react";
import type { SpecialistAgent, TaskHistoryItem } from "../types";

interface SidebarProps {
  files: string[];
  activeFile: string;
  onSelectFile: (path: string) => void;
  onCreateFilePrompt: () => void;
  agents: SpecialistAgent[];
  history: TaskHistoryItem[];
  activeTab: "explorer" | "agents" | "history";
  setActiveTab: (tab: "explorer" | "agents" | "history") => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  files,
  activeFile,
  onSelectFile,
  onCreateFilePrompt,
  agents,
  history,
  activeTab,
  setActiveTab,
}) => {
  const [fileFilter, setFileFilter] = useState("");

  const filteredFiles = files.filter((f) =>
    f.toLowerCase().includes(fileFilter.toLowerCase())
  );

  const getFileIcon = (path: string) => {
    if (path.endsWith(".ts") || path.endsWith(".tsx") || path.endsWith(".js") || path.endsWith(".jsx")) {
      return <FileCode2 size={14} color="#60a5fa" />;
    }
    if (path.endsWith(".py")) {
      return <FileCode2 size={14} color="#facc15" />;
    }
    if (path.endsWith(".json")) {
      return <FileText size={14} color="#a3e635" />;
    }
    return <FileText size={14} color="#94a3b8" />;
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-tabs">
        <button
          className={`sidebar-tab ${activeTab === "explorer" ? "active" : ""}`}
          onClick={() => setActiveTab("explorer")}
        >
          <Folder size={13} />
          <span>Files</span>
        </button>
        <button
          className={`sidebar-tab ${activeTab === "agents" ? "active" : ""}`}
          onClick={() => setActiveTab("agents")}
        >
          <Layers size={13} />
          <span>Agents ({agents.length})</span>
        </button>
        <button
          className={`sidebar-tab ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          <Clock size={13} />
          <span>History</span>
        </button>
      </div>

      {activeTab === "explorer" && (
        <div className="sidebar-content">
          <div className="sidebar-header-row">
            <span className="sidebar-title">PROJECT EXPLORER</span>
            <button
              className="icon-mini-btn"
              onClick={onCreateFilePrompt}
              title="New File"
            >
              <Plus size={13} />
            </button>
          </div>

          <div className="sidebar-search">
            <Search size={12} color="#64748b" />
            <input
              type="text"
              placeholder="Filter files..."
              value={fileFilter}
              onChange={(e) => setFileFilter(e.target.value)}
            />
          </div>

          <div className="tree">
            {filteredFiles.length === 0 ? (
              <div className="tree-empty">No matching files</div>
            ) : (
              filteredFiles.map((path) => {
                const isActive = activeFile === path;
                const fileName = path.split("/").pop() || path;
                return (
                  <button
                    key={path}
                    className={`tree-item ${isActive ? "active" : ""}`}
                    onClick={() => onSelectFile(path)}
                    title={path}
                  >
                    {getFileIcon(path)}
                    <span className="file-name">{fileName}</span>
                    {path.includes("/") && (
                      <span className="file-dir-hint">
                        {path.substring(0, path.lastIndexOf("/"))}
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>
      )}

      {activeTab === "agents" && (
        <div className="sidebar-content">
          <div className="sidebar-header-row">
            <span className="sidebar-title">KODRA SPECIALISTS</span>
          </div>
          <div className="agents-list">
            {agents.map((agent) => (
              <div key={agent.role} className="agent-card">
                <div className="agent-card-header">
                  <div className="agent-role-badge">{agent.role.toUpperCase()}</div>
                  <span className="agent-status-online">READY</span>
                </div>
                <div className="agent-name">{agent.name}</div>
                <div className="agent-desc">{agent.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "history" && (
        <div className="sidebar-content">
          <div className="sidebar-header-row">
            <span className="sidebar-title">TASK HISTORY (kodra.json)</span>
          </div>
          <div className="history-list">
            {history.length === 0 ? (
              <div className="tree-empty">No previous tasks recorded</div>
            ) : (
              history.map((item, idx) => (
                <div key={idx} className="history-card">
                  <div className="history-header">
                    {item.success ? (
                      <CheckCircle2 size={13} color="#4ade80" />
                    ) : (
                      <XCircle size={13} color="#f87171" />
                    )}
                    <span className="history-task" title={item.task}>
                      {item.task}
                    </span>
                  </div>
                  <p className="history-summary">{item.summary}</p>
                  {item.files_modified && item.files_modified.length > 0 && (
                    <div className="history-files">
                      {item.files_modified.map((f) => (
                        <span key={f} className="history-file-tag">
                          {f}
                        </span>
                      ))}
                    </div>
                  )}
                  <span className="history-time">
                    {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </aside>
  );
};
