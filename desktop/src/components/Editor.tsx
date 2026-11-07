import React, { useEffect } from "react";
import { FileCode2, Save, X, Check } from "lucide-react";

interface EditorProps {
  activeFile: string;
  code: string;
  onChangeCode: (val: string) => void;
  onSaveFile: () => void;
  onCloseFile: () => void;
  isSaving: boolean;
  isDirty: boolean;
}

export const Editor: React.FC<EditorProps> = ({
  activeFile,
  code,
  onChangeCode,
  onSaveFile,
  onCloseFile,
  isSaving,
  isDirty,
}) => {
  const fileName = activeFile ? activeFile.split("/").pop() || activeFile : "";

  // Keyboard shortcut Ctrl+S or Cmd+S to save
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        if (activeFile && isDirty) {
          onSaveFile();
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeFile, isDirty, onSaveFile]);

  const lines = code.split("\n");

  return (
    <main className="editor">
      <div className="editor-tabs">
        {activeFile ? (
          <div className="tab active">
            <FileCode2 size={14} color="#60a5fa" />
            <span className="tab-title">
              {fileName} {isDirty && <span className="dirty-dot">•</span>}
            </span>
            <button
              className="tab-close-btn"
              onClick={(e) => {
                e.stopPropagation();
                onCloseFile();
              }}
              title="Close Tab"
            >
              <X size={12} />
            </button>
          </div>
        ) : (
          <div className="tab inactive">No File Selected</div>
        )}

        <div className="editor-tab-actions">
          {activeFile && (
            <button
              className={`save-btn ${isDirty ? "dirty" : "saved"}`}
              onClick={onSaveFile}
              disabled={isSaving || !isDirty}
              title="Save File (Ctrl+S)"
            >
              {isSaving ? (
                "Saving..."
              ) : isDirty ? (
                <>
                  <Save size={13} />
                  <span>Save</span>
                </>
              ) : (
                <>
                  <Check size={13} />
                  <span>Saved</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      <div className="editor-content">
        {!activeFile ? (
          <div className="editor-empty">
            <div className="editor-empty-icon">
              <FileCode2 size={40} color="#475569" />
            </div>
            <h3>Kodra Workspace Ready</h3>
            <p>Select a file from the Explorer or ask Kodra AI to formulate a plan.</p>
          </div>
        ) : (
          <div className="code-container">
            <div className="line-numbers">
              {lines.map((_, index) => (
                <span key={index}>{index + 1}</span>
              ))}
            </div>
            <textarea
              className="code-textarea"
              value={code}
              onChange={(e) => onChangeCode(e.target.value)}
              spellCheck={false}
              autoCapitalize="off"
              autoComplete="off"
            />
          </div>
        )}
      </div>
    </main>
  );
};
