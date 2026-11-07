export type OperationType =
  | "create_file"
  | "modify_file"
  | "delete_file"
  | "create_dir"
  | "run_command";

export type RiskLevel = "low" | "medium" | "high";

export type StepStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "running"
  | "success"
  | "failed"
  | "skipped";

export type PlanStatus =
  | "draft"
  | "approved"
  | "executing"
  | "completed"
  | "failed"
  | "repaired";

export interface PlanStep {
  id: string;
  title: string;
  description: string;
  operation: OperationType;
  path?: string | null;
  content?: string | null;
  command?: string | null;
  risk_level: RiskLevel;
  requires_approval: boolean;
  approved: boolean;
  status: StepStatus;
}

export interface ExecutionPlan {
  id: string;
  task: string;
  summary: string;
  steps: PlanStep[];
  status: PlanStatus;
  created_at: string;
  metadata: Record<string, any>;
}

export interface StepResult {
  step_id: string;
  status: StepStatus;
  output: string;
  error?: string | null;
  exit_code?: number | null;
  duration_ms: number;
}

export interface ExecutionResult {
  plan_id: string;
  success: boolean;
  step_results: StepResult[];
  summary: string;
  error?: string | null;
}

export interface SpecialistAgent {
  role: string;
  name: string;
  description: string;
}

export interface TaskHistoryItem {
  task: string;
  plan_id: string;
  success: boolean;
  summary: string;
  files_modified: string[];
  timestamp: string;
}

export interface WorkspaceInfo {
  workspace_root: string;
  project_name: string;
  tech_stack: string[];
  files_count: number;
}
