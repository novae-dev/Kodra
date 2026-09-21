import {
  Bot,
  ChevronDown,
  ChevronRight,
  Code2,
  FileCode2,
  Folder,
  GitBranch,
  MessageSquare,
  Play,
  Search,
  Settings,
  Terminal,
  X,
  Zap,
} from "lucide-react";
import { useState } from "react";
import "./App.css";

const files = [
  { name: "src", type: "folder", open: true },
  { name: "App.tsx", type: "file", active: true },
  { name: "main.tsx", type: "file" },
  { name: "App.css", type: "file" },
  { name: "index.css", type: "file" },
  { name: "package.json", type: "file" },
  { name: "vite.config.ts", type: "file" },
];

const code = [
  "import { useState } from 'react';",
  "",
  "function App() {",
  "  const [count, setCount] = useState(0);",
  "",
  "  return (",
  "    <main>",
  "      <h1>Hello Kodra</h1>",
  "      <button onClick={() => setCount(count + 1)}>",
  "        Count: {count}",
  "      </button>",
  "    </main>",
  "  );",
  "}",
  "",
  "export default App;",
];

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState<string[]>([]);

  const sendMessage = () => {
    if (!message.trim()) return;

    setChat((current) => [
      ...current,
      `You: ${message}`,
      "Kodra: I’m analyzing your project...",
    ]);
    setMessage("");
  };

  return (
    <div className="kodra">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <Code2 size={18} />
          </div>
          <span>KODRA</span>
        </div>

        <div className="project">
          <GitBranch size={14} />
          <span>main</span>
          <ChevronDown size={14} />
        </div>

        <div className="connection">
          <span className="status-dot" />
          Connected
        </div>
      </header>

      <div className="workspace">
        <aside className="activitybar">
          <Code2 />
          <Search />
          <GitBranch />
          <MessageSquare />
          <div className="activity-spacer" />
          <Settings />
        </aside>

        <aside className="sidebar">
          <div className="sidebar-title">EXPLORER</div>

          <div className="tree-root">
            <ChevronDown size={14} />
            <Folder size={15} />
            <span>KODRA</span>
          </div>

          <div className="tree">
            {files.map((file) => (
              <div
                key={file.name}
                className={`tree-item ${file.active ? "active" : ""}`}
              >
                {file.type === "folder" ? (
                  <>
                    <ChevronDown size={14} />
                    <Folder size={15} />
                  </>
                ) : (
                  <>
                    <span className="tree-indent" />
                    <FileCode2 size={14} />
                  </>
                )}
                <span>{file.name}</span>
              </div>
            ))}
          </div>
        </aside>

        <main className="editor">
          <div className="editor-tabs">
            <div className="tab active">
              <FileCode2 size={14} />
              App.tsx
              <X size={13} />
            </div>
          </div>

          <div className="editor-content">
            <div className="line-numbers">
              {code.map((_, index) => (
                <span key={index}>{index + 1}</span>
              ))}
            </div>

            <pre className="code">
              {code.map((line, index) => (
                <div key={index} className="code-line">
                  {line || " "}
                </div>
              ))}
            </pre>
          </div>

          <div className="terminal">
            <div className="terminal-header">
              <div>
                <Terminal size={14} />
                TERMINAL
              </div>
              <X size={14} />
            </div>

            <div className="terminal-body">
              <div>
                <span className="prompt">$</span> npm run dev
              </div>
              <div className="terminal-muted">
                VITE ready — local development server running
              </div>
              <div>
                <span className="prompt">$</span>{" "}
                <span className="cursor">_</span>
              </div>
            </div>
          </div>
        </main>

        <aside className="ai-panel">
          <div className="ai-header">
            <div className="ai-title">
              <div className="ai-icon">
                <Bot size={16} />
              </div>
              <div>
                <strong>Kodra AI</strong>
                <span>AI coding agent</span>
              </div>
            </div>

            <Zap size={16} />
          </div>

          <div className="chat">
            {chat.length === 0 ? (
              <div className="empty-chat">
                <div className="big-ai-icon">
                  <Bot size={25} />
                </div>
                <h2>Build with Kodra</h2>
                <p>
                  Ask Kodra to understand your project, write code, fix bugs, or
                  make changes.
                </p>

                <div className="suggestions">
                  <button onClick={() => setMessage("Explain this project")}>
                    Explain this project
                  </button>
                  <button onClick={() => setMessage("Find bugs in this file")}>
                    Find bugs in this file
                  </button>
                  <button onClick={() => setMessage("Build a new feature")}>
                    Build a new feature
                  </button>
                </div>
              </div>
            ) : (
              chat.map((item, index) => (
                <div
                  key={index}
                  className={item.startsWith("You:") ? "user-msg" : "ai-msg"}
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
              placeholder="Ask Kodra anything..."
            />

            <div className="input-footer">
              <span>Enter to send</span>
              <button onClick={sendMessage}>
                <Play size={14} />
              </button>
            </div>
          </div>
        </aside>
      </div>

      <footer className="statusbar">
        <div>
          <GitBranch size={13} />
          main
        </div>
        <div>TypeScript React</div>
        <div>Kodra MVP</div>
      </footer>
    </div>
  );
}

export default App;
