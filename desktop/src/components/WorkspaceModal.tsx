import React, { useState } from "react";
import { Folder, X } from "lucide-react";

interface WorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentRoot: string;
  onSwitchWorkspace: (path: string) => Promise<void>;
}

export const WorkspaceModal: React.FC<WorkspaceModalProps> = ({
  isOpen,
  onClose,
  currentRoot,
  onSwitchWorkspace,
}) => {
  const [pathInput, setPathInput] = useState(currentRoot);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pathInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await onSwitchWorkspace(pathInput.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to switch workspace");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <Folder size={16} color="#818cf8" />
            <span>Select Project Workspace</span>
          </div>
          <button className="icon-mini-btn" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <p className="modal-desc">
            All AI operations, file modifications, and commands will be strictly sandboxed to this project directory.
          </p>

          <label className="input-label">Workspace Root Absolute Directory:</label>
          <input
            type="text"
            className="text-input"
            value={pathInput}
            onChange={(e) => setPathInput(e.target.value)}
            placeholder="C:/Users/name/my-project"
          />

          {error && <div className="modal-error">{error}</div>}

          <div className="modal-footer">
            <button type="button" className="btn secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn primary" disabled={loading}>
              {loading ? "Switching..." : "Switch Workspace"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
