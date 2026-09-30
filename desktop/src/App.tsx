import { ChevronDown, FileCode2, FileText, Folder, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import "./App.css";

const getFileName = (path: string) =>
  path.split("/").filter(Boolean).pop() || path;

function App() {
  const [files, setFiles] = useState<string[]>([]);
  const [activeFile, setActiveFile] = useState("");
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<string[]>([]);
  const [loadingFile, setLoadingFile] = useState(false);
  const [projectLoading, setProjectLoading] = useState(true);

  const openFile = useCallback(async (path: string) => {
    setActiveFile(path);
    setLoadingFile(true);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/file?path=${encodeURIComponent(path)}`,
      );

      if (!response.ok) {
        throw new Error("Failed to read file");
      }

      const data = await response.json();
      setCode(data.content);
    } catch {
      setCode("// Unable to read this file.");
    } finally {
      setLoadingFile(false);
    }
  }, []);

  const loadProject = useCallback(async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/project");

      if (!response.ok) {
        throw new Error("Failed to load project");
      }

      const data = await response.json();
      const projectFiles: string[] = data.files || [];

      setFiles(projectFiles);

      const firstFile = projectFiles.find(
        (file) =>
          file.endsWith(".tsx") ||
          file.endsWith(".ts") ||
          file.endsWith(".jsx") ||
          file.endsWith(".js"),
      );

      if (firstFile) {
        await openFile(firstFile);
      }
    } catch {
      setChat([
        "Kodra: I can't load the project. Make sure the Python agent is running.",
      ]);
    } finally {
      setProjectLoading(false);
    }
  }, [openFile]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadProject();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [loadProject]);

  const sendMessage = async () => {
    const text = message.trim();

    if (!text) return;

    setChat((current) => [...current, `You: ${text}`]);
    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          context: {
            currentFile: activeFile,
            projectFiles: files,
            code,
          },
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setChat((current) => [...current, `Kodra: ${data.reply}`]);
    } catch {
      setChat((current) => [
        ...current,
        "Kodra: I can't reach the Kodra agent. Make sure the backend is running.",
      ]);
    }
  };

  return (
    <div className="kodra">
      <header className="topbar">
        <div className="brand">KODRA</div>

        <div className="topbar-center">
          <span className="project-name">Kodra</span>
          <span className="separator">/</span>
          <span>{activeFile || "No file selected"}</span>
        </div>

        <div className="topbar-status">
          <span className="status-dot" />
          Connected
        </div>
      </header>

      <div className="workspace">
        <aside className="activitybar">
          <button className="activity-button active" title="Explorer">
            <FileCode2 size={19} />
          </button>

          <button className="activity-button" title="Search">
            <span>⌕</span>
          </button>

          <button className="activity-button" title="Terminal">
            <span>›_</span>
          </button>

          <div className="activity-spacer" />

          <button className="activity-button" title="Settings">
            <span>⚙</span>
          </button>
        </aside>

        <aside className="sidebar">
          <div className="sidebar-title">EXPLORER</div>

          <div className="tree-root">
            <ChevronDown size={14} />
            <Folder size={15} />
            <span>KODRA</span>
          </div>

          <div className="tree">
            {projectLoading ? (
              <div className="tree-item">
                <span>Loading project...</span>
              </div>
            ) : files.length === 0 ? (
              <div className="tree-item">
                <span>No files found</span>
              </div>
            ) : (
              files.map((path) => {
                const isActive = activeFile === path;

                return (
                  <button
                    key={path}
                    className={`tree-item ${isActive ? "active" : ""}`}
                    onClick={() => openFile(path)}
                    title={path}
                  >
                    <span className="tree-indent" />

                    {path.includes("/") ? (
                      <FileCode2 size={14} />
                    ) : (
                      <FileText size={14} />
                    )}

                    <span>{getFileName(path)}</span>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        <main className="editor">
          <div className="editor-tabs">
            {activeFile && (
              <div className="tab active">
                <FileCode2 size={14} />
                <span>{getFileName(activeFile)}</span>
                <X size={13} />
              </div>
            )}
          </div>

          <div className="editor-content">
            {loadingFile ? (
              <div className="code-loading">Loading file...</div>
            ) : (
              <>
                <div className="line-numbers">
                  {code.split("\n").map((_, index) => (
                    <span key={index}>{index + 1}</span>
                  ))}
                </div>

                <pre className="code">
                  {code.split("\n").map((line, index) => (
                    <div key={index} className="code-line">
                      {line || " "}
                    </div>
                  ))}
                </pre>
              </>
            )}
          </div>
        </main>

        <aside className="ai-panel">
          <div className="ai-header">
            <span>KODRA AI</span>
            <span className="ai-online">ONLINE</span>
          </div>

          <div className="chat">
            {chat.length === 0 ? (
              <div className="chat-empty">
                <strong>Kodra AI</strong>
                <p>Ask me to understand, modify, or improve your project.</p>
              </div>
            ) : (
              chat.map((item, index) => (
                <div
                  key={`${item}-${index}`}
                  className={
                    item.startsWith("You:")
                      ? "chat-message user"
                      : "chat-message"
                  }
                >
                  {item}
                </div>
              ))
            )}
          </div>

          <div className="chat-input">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Ask Kodra..."
            />

            <button onClick={sendMessage}>Send</button>
          </div>
        </aside>
      </div>

      <footer className="statusbar">
        <span>{activeFile || "Kodra"}</span>
        <span>{code.split("\n").length} lines</span>
        <span>UTF-8</span>
        <span>TypeScript</span>
      </footer>
    </div>
  );
}

export default App;
