import type {
  ExecutionPlan,
  ExecutionResult,
  SpecialistAgent,
  TaskHistoryItem,
  WorkspaceInfo,
} from "../types";

const BASE_URL = "http://127.0.0.1:8000";

export class KodraApi {
  static async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      return res.ok;
    } catch {
      return false;
    }
  }

  static async getWorkspace(): Promise<WorkspaceInfo> {
    const res = await fetch(`${BASE_URL}/workspace`);
    if (!res.ok) throw new Error("Failed to load workspace info");
    return res.json();
  }

  static async switchWorkspace(path: string): Promise<WorkspaceInfo> {
    const res = await fetch(`${BASE_URL}/workspace`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to switch workspace" }));
      throw new Error(err.detail || "Failed to switch workspace");
    }
    return res.json();
  }

  static async getProject(): Promise<{ project: string; files: string[]; tech_stack: string[]; guidelines: string[] }> {
    const res = await fetch(`${BASE_URL}/project`);
    if (!res.ok) throw new Error("Failed to load project files");
    return res.json();
  }

  static async readFile(path: string): Promise<string> {
    const res = await fetch(`${BASE_URL}/file?path=${encodeURIComponent(path)}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to read file" }));
      throw new Error(err.detail || "Failed to read file");
    }
    const data = await res.json();
    return data.content;
  }

  static async writeFile(path: string, content: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/file`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path, content }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to write file" }));
      throw new Error(err.detail || "Failed to write file");
    }
  }

  static async generatePlan(task: string, multiAgent = false, context: Record<string, any> = {}): Promise<ExecutionPlan> {
    const res = await fetch(`${BASE_URL}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task, multi_agent: multiAgent, context }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to generate plan" }));
      throw new Error(err.detail || "Failed to generate plan");
    }
    return res.json();
  }

  static async validatePlan(plan: ExecutionPlan): Promise<{ valid: boolean; violations: string[] }> {
    const res = await fetch(`${BASE_URL}/plan/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(plan),
    });
    if (!res.ok) throw new Error("Failed to validate plan");
    return res.json();
  }

  static async executePlan(
    plan: ExecutionPlan,
    approvedStepIds?: string[],
    autoApprove = false
  ): Promise<{ plan: ExecutionPlan; result: ExecutionResult }> {
    const res = await fetch(`${BASE_URL}/plan/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        plan,
        approved_step_ids: approvedStepIds,
        auto_approve: autoApprove,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to execute plan" }));
      throw new Error(err.detail || "Failed to execute plan");
    }
    return res.json();
  }

  static async repairPlan(
    originalPlan: ExecutionPlan,
    failedStepId: string,
    errorOutput: string
  ): Promise<ExecutionPlan> {
    const res = await fetch(`${BASE_URL}/plan/repair`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        original_plan: originalPlan,
        failed_step_id: failedStepId,
        error_output: errorOutput,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to repair plan" }));
      throw new Error(err.detail || "Failed to repair plan");
    }
    return res.json();
  }

  static async getHistory(): Promise<TaskHistoryItem[]> {
    const res = await fetch(`${BASE_URL}/history`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.history || [];
  }

  static async getAgents(): Promise<SpecialistAgent[]> {
    const res = await fetch(`${BASE_URL}/agents`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.agents || [];
  }

  static async getConfig(): Promise<Record<string, any>> {
    const res = await fetch(`${BASE_URL}/config`);
    if (!res.ok) throw new Error("Failed to fetch config");
    return res.json();
  }

  static async updateConfig(payload: Record<string, any>): Promise<void> {
    const res = await fetch(`${BASE_URL}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to update config");
  }

  static async sendChat(message: string, context: Record<string, any> = {}): Promise<string> {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, context }),
    });
    if (!res.ok) throw new Error("Backend chat request failed");
    const data = await res.json();
    return data.reply;
  }
}
