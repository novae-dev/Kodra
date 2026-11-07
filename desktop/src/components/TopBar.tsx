import React from "react";
import { Folder, Settings as SettingsIcon, Cpu, RefreshCw } from "lucide-react";
import type { WorkspaceInfo } from "../types";

interface TopBarProps {
  workspace: WorkspaceInfo | null;
  activeFile: string;
  connected: boolean;
  activeProvider: string;
  onOpenWorkspaceModal: () => void;
  onOpenSettingsModal: () => void;
  onRefresh: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  workspace,
  activeFile,
  connected,
  activeProvider,
  onOpenWorkspaceModal,
  onOpenSettingsModal,
  onRefresh,
}) => {
  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <Cpu size={15} color="#818cf8" />
        </div>
        <span>KODRA</span>
      </div>

      <div className="topbar-center">
        <button
          className="workspace-selector-btn"
          onClick={onOpenWorkspaceModal}
          title="Click to switch workspace root"
        >
          <Folder size={14} className="icon-folder" />
          <span className="workspace-name">{workspace?.project_name || "Workspace"}</span>
          <span className="workspace-path">({workspace?.workspace_root || "Loading..."})</span>
        </button>

        {activeFile && (
          <>
            <span className="separator">/</span>
            <span className="active-file-indicator">{activeFile}</span>
          </>
        )}
      </div>

      <div className="topbar-actions">
        {workspace?.tech_stack && workspace.tech_stack.length > 0 && (
          <div className="tech-stack-badges">
            {workspace.tech_stack.map((tech) => (
              <span key={tech} className="tech-badge">
                {tech}
              </span>
            ))}
          </div>
        )}

        <button
          className="provider-badge-btn"
          onClick={onOpenSettingsModal}
          title="Configure AI Provider & Model"
        >
          <span className="provider-dot" />
          <span className="provider-name">{activeProvider.toUpperCase()}</span>
          <SettingsIcon size={13} />
        </button>

        <button className="icon-action-btn" onClick={onRefresh} title="Refresh workspace and status">
          <RefreshCw size={13} />
        </button>

        <div className={`connection-status ${connected ? "online" : "offline"}`}>
          <span className="status-dot" />
          <span>{connected ? "Connected" : "Disconnected"}</span>
        </div>
      </div>
    </header>
  );
};
