import { useState, useEffect, useCallback } from "react";
import { TopBar } from "./components/TopBar";
import { Sidebar } from "./components/Sidebar";
import { Editor } from "./components/Editor";
import { TerminalPanel } from "./components/TerminalPanel";
import type { LogEntry } from "./components/TerminalPanel";
import { AIPanel } from "./components/AIPanel";
import { WorkspaceModal } from "./components/WorkspaceModal";
import { SettingsModal } from "./components/SettingsModal";
import { KodraApi } from "./services/api";
import type {
  ExecutionPlan,
  SpecialistAgent,
  TaskHistoryItem,
  WorkspaceInfo,
} from "./types";
import "./App.css";

export function App() {
  // Project & Workspace state
  const [workspace, setWorkspace] = useState<WorkspaceInfo | null>(null);
  const [files, setFiles] = useState<string[]>([]);
  const [activeFile, setActiveFile] = useState<string>("");
  const [code, setCode] = useState<string>("");
  const [savedCode, setSavedCode] = useState<string>("");
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [connected, setConnected] = useState<boolean>(false);
  const [activeProvider, setActiveProvider] = useState<string>("mock");

  // Navigation & Side panels
  const [activeTab, setActiveTab] = useState<"explorer" | "agents" | "history">("explorer");
  const [agents, setAgents] = useState<SpecialistAgent[]>([]);
  const [history, setHistory] = useState<TaskHistoryItem[]>([]);

  // Terminal & Logs
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: "log-init",
      type: "info",
      text: "Kodra Autonomous AI Coding Agent initialized. Engine: Python.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [terminalOpen, setTerminalOpen] = useState<boolean>(true);

  // AI & Plan state
  const [currentPlan, setCurrentPlan] = useState<ExecutionPlan | null>(null);
  const [selectedStepIds, setSelectedStepIds] = useState<Set<string>>(new Set());
  const [isGeneratingPlan, setIsGeneratingPlan] = useState<boolean>(false);
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<{ id: string; sender: "user" | "kodra"; text: string }[]>([]);

  // Modals
  const [workspaceModalOpen, setWorkspaceModalOpen] = useState<boolean>(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState<boolean>(false);

  const addLog = useCallback(
    (type: "command" | "stdout" | "stderr" | "info" | "success" | "error", text: string) => {
      setLogs((prev) => [
        ...prev,
        {
          id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          type,
          text,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    },
    []
  );

  // Open file handler
  const openFile = useCallback(async (path: string) => {
    try {
      const content = await KodraApi.readFile(path);
      setActiveFile(path);
      setCode(content);
      setSavedCode(content);
      addLog("info", `Opened ${path}`);
    } catch (err: any) {
      addLog("error", `Cannot open ${path}: ${err.message}`);
    }
  }, [addLog]);

  // Load project workspace info, files, agents, history
  const loadWorkspace = useCallback(async () => {
    try {
      const isHealthy = await KodraApi.checkHealth();
      setConnected(isHealthy);
      if (!isHealthy) return;

      const [wsInfo, projData, agentList, taskHistory, cfg] = await Promise.all([
        KodraApi.getWorkspace(),
        KodraApi.getProject(),
        KodraApi.getAgents(),
        KodraApi.getHistory(),
        KodraApi.getConfig(),
      ]);

      setWorkspace(wsInfo);
      setFiles(projData.files || []);
      setAgents(agentList);
      setHistory(taskHistory);
      if (cfg.provider) {
        setActiveProvider(cfg.provider);
      }

      // If activeFile is empty or not in files, pick first code file
      if (!activeFile && projData.files?.length > 0) {
        const preferred = projData.files.find(
          (f: string) => f.endsWith(".py") || f.endsWith(".tsx") || f.endsWith(".ts") || f.endsWith(".js")
        ) || projData.files[0];
        if (preferred) {
          void openFile(preferred);
        }
      }
    } catch (err: any) {
      setConnected(false);
      addLog("error", `Failed to connect to backend: ${err.message}`);
    }
  }, [activeFile, addLog, openFile]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  // Save active file handler
  const handleSaveFile = async () => {
    if (!activeFile) return;
    setIsSaving(true);
    try {
      await KodraApi.writeFile(activeFile, code);
      setSavedCode(code);
      addLog("success", `Saved changes to ${activeFile}`);
    } catch (err: any) {
      addLog("error", `Save failed for ${activeFile}: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Close active file
  const handleCloseFile = () => {
    setActiveFile("");
    setCode("");
    setSavedCode("");
  };

  // Switch workspace
  const handleSwitchWorkspace = async (path: string) => {
    const newWs = await KodraApi.switchWorkspace(path);
    setWorkspace(newWs);
    addLog("info", `Switched workspace root to: ${newWs.workspace_root}`);
    await loadWorkspace();
  };

  // Generate Execution Plan
  const handleGeneratePlan = async (task: string, multiAgent: boolean) => {
    setIsGeneratingPlan(true);
    addLog("command", `Generate Plan (${multiAgent ? "Multi-Agent Orchestration" : activeProvider}): "${task}"`);
    try {
      const plan = await KodraApi.generatePlan(task, multiAgent, {
        currentFile: activeFile,
        code,
      });

      setCurrentPlan(plan);
      // Select all steps by default
      setSelectedStepIds(new Set(plan.steps.map((s) => s.id)));
      addLog("success", `Plan formulated: ${plan.summary} (${plan.steps.length} operations)`);

      if (plan.metadata?.validation_warnings?.length > 0) {
        addLog("stderr", `Policy notice: ${plan.metadata.validation_warnings.join("; ")}`);
      }
    } catch (err: any) {
      addLog("error", `Planning failed: ${err.message}`);
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  // Execute Execution Plan
  const handleExecutePlan = async (autoApprove: boolean) => {
    if (!currentPlan) return;
    setIsExecuting(true);
    addLog("command", `Executing plan: "${currentPlan.task}" (Auto-approve: ${autoApprove})`);

    try {
      const approvedIds = autoApprove ? currentPlan.steps.map((s) => s.id) : Array.from(selectedStepIds);
      const { plan: updatedPlan, result } = await KodraApi.executePlan(
        currentPlan,
        approvedIds,
        autoApprove
      );

      setCurrentPlan(updatedPlan);

      // Stream each step outcome to the terminal
      result.step_results.forEach((sr) => {
        const matchingStep = updatedPlan.steps.find((s) => s.id === sr.step_id);
        const title = matchingStep?.title || sr.step_id;
        if (sr.status === "success") {
          addLog("success", `[${title}] ${sr.output || "Success"} (${sr.duration_ms}ms)`);
        } else if (sr.status === "failed") {
          addLog("error", `[${title}] FAILED: ${sr.error || sr.output} (${sr.duration_ms}ms)`);
        } else if (sr.status === "skipped") {
          addLog("info", `[${title}] Skipped: User approval required`);
        }
      });

      if (result.success) {
        addLog("success", `Task Completed: ${result.summary}`);
      } else {
        addLog("error", `Execution halted: ${result.error || result.summary}`);
      }

      // Refresh workspace file list and memory history
      await loadWorkspace();

      // If activeFile was modified by plan, reload it
      if (activeFile) {
        try {
          const fresh = await KodraApi.readFile(activeFile);
          setCode(fresh);
          setSavedCode(fresh);
        } catch {
          // File may have been deleted or moved
        }
      }
    } catch (err: any) {
      addLog("error", `Execution engine error: ${err.message}`);
    } finally {
      setIsExecuting(false);
    }
  };

  // Self-Healing: Trigger Repair Plan
  const handleTriggerRepair = async (failedStepId: string, errorOutput: string) => {
    if (!currentPlan) return;
    setIsGeneratingPlan(true);
    addLog("command", `Diagnostic Self-Healing triggered for failed step: ${failedStepId}`);
    try {
      const repairPlan = await KodraApi.repairPlan(currentPlan, failedStepId, errorOutput);
      setCurrentPlan(repairPlan);
      setSelectedStepIds(new Set(repairPlan.steps.map((s) => s.id)));
      addLog("success", `Self-healing plan generated: ${repairPlan.summary}`);
    } catch (err: any) {
      addLog("error", `Self-healing analysis failed: ${err.message}`);
    } finally {
      setIsGeneratingPlan(false);
    }
  };

  // Chat message sender
  const handleSendChatMessage = async (text: string) => {
    const userMsgId = `msg-${Date.now()}`;
    setChatMessages((prev) => [...prev, { id: userMsgId, sender: "user", text }]);
    addLog("command", `User Prompt: ${text}`);

    try {
      const reply = await KodraApi.sendChat(text, {
        currentFile: activeFile,
        code,
      });
      setChatMessages((prev) => [
        ...prev,
        { id: `msg-${Date.now()}-ai`, sender: "kodra", text: reply },
      ]);
      addLog("info", `Kodra AI Reply received.`);
    } catch (err: any) {
      addLog("error", `Chat failed: ${err.message}`);
    }
  };

  const isDirty = code !== savedCode;

  return (
    <div className="kodra">
      <TopBar
        workspace={workspace}
        activeFile={activeFile}
        connected={connected}
        activeProvider={activeProvider}
        onOpenWorkspaceModal={() => setWorkspaceModalOpen(true)}
        onOpenSettingsModal={() => setSettingsModalOpen(true)}
        onRefresh={() => void loadWorkspace()}
      />

      <div className="workspace">
        <Sidebar
          files={files}
          activeFile={activeFile}
          onSelectFile={(path) => void openFile(path)}
          onCreateFilePrompt={() => {
            const name = window.prompt("Enter new file relative path (e.g. src/app.py):");
            if (name) {
              void (async () => {
                await KodraApi.writeFile(name, "");
                await loadWorkspace();
                await openFile(name);
              })();
            }
          }}
          agents={agents}
          history={history}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        <div className="editor-and-terminal-wrapper">
          <Editor
            activeFile={activeFile}
            code={code}
            onChangeCode={setCode}
            onSaveFile={() => void handleSaveFile()}
            onCloseFile={handleCloseFile}
            isSaving={isSaving}
            isDirty={isDirty}
          />

          <TerminalPanel
            logs={logs}
            onClear={() => setLogs([])}
            isOpen={terminalOpen}
            onToggle={() => setTerminalOpen(!terminalOpen)}
          />
        </div>

        <AIPanel
          currentPlan={currentPlan}
          selectedStepIds={selectedStepIds}
          onToggleStepSelection={(id) => {
            const next = new Set(selectedStepIds);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            setSelectedStepIds(next);
          }}
          onSelectAllSteps={() => {
            if (currentPlan) {
              setSelectedStepIds(new Set(currentPlan.steps.map((s) => s.id)));
            }
          }}
          onDeselectAllSteps={() => setSelectedStepIds(new Set())}
          onExecutePlan={(autoApprove) => void handleExecutePlan(autoApprove)}
          onRejectPlan={() => {
            setCurrentPlan(null);
            addLog("info", "Plan dismissed by user.");
          }}
          onTriggerRepair={(failedStepId, errorOutput) =>
            void handleTriggerRepair(failedStepId, errorOutput)
          }
          isExecuting={isExecuting}
          isGeneratingPlan={isGeneratingPlan}
          onGeneratePlan={(task, multiAgent) => void handleGeneratePlan(task, multiAgent)}
          chatMessages={chatMessages}
          onSendChatMessage={(text) => void handleSendChatMessage(text)}
        />
      </div>

      <footer className="statusbar">
        <div className="status-left">
          <span>{activeFile || "No active file"}</span>
          <span>{code.split("\n").length} lines</span>
          <span>UTF-8</span>
          {isDirty && <span className="status-unsaved">● Unsaved edits</span>}
        </div>
        <div className="status-right">
          <span>Provider: {activeProvider.toUpperCase()}</span>
          <span>Kodra 0.2.0</span>
        </div>
      </footer>

      {/* Modals */}
      <WorkspaceModal
        isOpen={workspaceModalOpen}
        onClose={() => setWorkspaceModalOpen(false)}
        currentRoot={workspace?.workspace_root || ""}
        onSwitchWorkspace={handleSwitchWorkspace}
      />

      <SettingsModal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        activeProvider={activeProvider}
        onProviderChanged={(newP) => {
          setActiveProvider(newP);
          addLog("info", `Active provider switched to: ${newP}`);
        }}
      />
    </div>
  );
}

export default App;
