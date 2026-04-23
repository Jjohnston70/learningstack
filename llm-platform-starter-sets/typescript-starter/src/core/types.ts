/**
 * types.ts — Shared interfaces for the modular LLM platform.
 *
 * These types define the contracts between runtime layers.
 * Both the Python and TypeScript starters use the same conceptual types —
 * this file is the TypeScript expression of that shared contract.
 */

export interface ClientConfig {
  client_id: string;
  name: string;
  active_modules: string[];
  module_versions?: Record<string, string>;
  branding?: {
    company_name?: string;
    tone?: string;
  };
  data_sources?: string[];
  permissions?: Record<string, string[]>;
  model_preferences?: {
    default_model?: string;
    reasoning_model?: string;
  };
}

export interface ModuleConfig {
  name: string;
  version: string;
  description?: string;
  required_tools?: string[];
  required_permissions?: string[];
  output_mode?: "structured" | "freeform";
  output_fields?: string[];
  keywords?: string[];
}

export interface ExecutionRequest {
  clientId: string;
  userInput: string;
  metadata?: Record<string, unknown>;
}

export interface ExecutionContext {
  clientId: string;
  clientName: string;
  tone: string;
  moduleName: string;
  moduleVersion: string;
  userRequest: string;
  dataSources: string[];
  permissions: string[];
  outputFields: string[];
}

export interface ExecutionResult {
  success: boolean;
  output: Record<string, unknown>;
  errors: string[];
  moduleName: string;
}

export interface LogEvent {
  event_type: string;
  client_id: string;
  module_name: string;
  module_version: string;
  user_request: string;
  data_sources: string;
  output_valid: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}
