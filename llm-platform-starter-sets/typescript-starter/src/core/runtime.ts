/**
 * runtime.ts — Main orchestration engine for the TypeScript starter.
 *
 * Coordinates: load config → route → build context → build prompt
 *              → execute module → validate → log → return
 */

import { ExecutionRequest, ExecutionResult, ExecutionContext } from "./types";
import { loadClient, loadModuleConfig } from "./configLoader";
import { routeRequest } from "./router";
import { buildContext } from "./contextBuilder";
import { buildPrompt, loadModuleInstructions } from "./promptBuilder";
import { validateOutput } from "./validator";
import { buildLogEvent } from "./logger";

export async function executeRequest(request: ExecutionRequest): Promise<ExecutionResult> {
  // Step 1 — Load client config
  const client = loadClient(request.clientId);

  // Step 2 — Route to module
  const module = routeRequest(request.userInput, client);

  // Step 3 — Build execution context
  const context = buildContext(client, module, request.userInput);

  // Step 4 — Load module instructions
  const instructions = loadModuleInstructions(module.name);

  // Step 5 — Build final prompt
  const prompt = buildPrompt({
    clientName: context.clientName,
    tone: context.tone,
    moduleName: context.moduleName,
    moduleInstructions: instructions,
    userRequest: context.userRequest,
    dataSources: context.dataSources,
    outputFields: context.outputFields,
  });

  // Step 6 — Execute module (stub in Phase 1/2; real LLM call in Phase 7)
  const output = callModuleStub(module.name, prompt, context);

  // Step 7 — Validate output
  const { isValid, errors } = validateOutput(output, module.output_fields ?? []);

  // Step 8 — Log safely
  const logEvent = buildLogEvent("request_completed", context, isValid);
  emitLog(logEvent);

  // Step 9 — Return result
  return {
    success: isValid,
    output,
    errors,
    moduleName: module.name,
  };
}

function callModuleStub(
  moduleName: string,
  prompt: string,
  context: ExecutionContext
): Record<string, unknown> {
  /**
   * Stub executor. Replace in Phase 7 with:
   *   const response = await llmProvider.complete(prompt);
   *   return parseStructuredOutput(response);
   */
  console.log(`\n[STUB] Would call LLM with module: ${moduleName}`);
  console.log(`[STUB] Prompt length: ${prompt.length} chars`);
  console.log(`[STUB] Client: ${context.clientId}`);
  console.log(`[STUB] Data sources: ${context.dataSources.join(", ")}`);

  return {
    summary: `[STUB] Response from ${moduleName} for: ${context.userRequest.slice(0, 50)}`,
    risks: ["[STUB] Risk item 1", "[STUB] Risk item 2"],
    recommended_actions: ["[STUB] Action item 1"],
  };
}

function emitLog(logEvent: Record<string, unknown>): void {
  // Replace with real logging in Phase 7/8 (Datadog, CloudWatch, etc.)
  console.log("\n[LOG]", JSON.stringify(logEvent, null, 2));
}
