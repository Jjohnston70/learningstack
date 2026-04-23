/**
 * module.ts — TypeScript wrapper entrypoint for [your-module-name].
 *
 * This is the thin adapter between the platform runtime and the module's logic.
 * Keep this file clean. Heavy lifting goes in the tool adapters.
 *
 * Usage:
 *   import { run } from "./adapters/typescript/module";
 *   const result = await run(context);
 */

export interface ModuleContext {
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

export interface ModuleOutput {
  summary: string;
  risks: string[];
  recommended_actions: string[];
  [key: string]: unknown; // Allow additional output fields
}

export async function run(context: ModuleContext): Promise<ModuleOutput> {
  /**
   * Main entrypoint for this module.
   *
   * Returns an object matching the fields defined in output_schema.json.
   * At minimum: { summary, risks, recommended_actions }
   */

  const { clientName, userRequest, dataSources, permissions } = context;

  // ── PHASE 2 STUB ──────────────────────────────────────────────────────────
  // Replace this section with real logic in Phase 5+.
  //
  // Phase 5 implementation pattern:
  //
  //   import { getDataExample, createRecordExample } from "../../src/tools/yourTools";
  //
  //   if (!permissions.includes("read")) {
  //     return errorResponse("Insufficient permissions for read");
  //   }
  //
  //   const data = await getDataExample({
  //     sourceId: dataSources[0] ?? "",
  //   });
  //
  //   const summary = deriveSummary(data, userRequest);
  //   const risks = identifyRisks(data);
  //   const actions = recommendActions(risks, permissions);
  //
  //   return { summary, risks, recommended_actions: actions };
  // ─────────────────────────────────────────────────────────────────────────

  return {
    summary: `[STUB] Module processed request for ${clientName}: ${userRequest.slice(0, 50)}`,
    risks: ["[STUB] Risk placeholder — connect real tools in Phase 5"],
    recommended_actions: ["[STUB] Action placeholder — connect real tools in Phase 5"],
  };
}

function errorResponse(message: string): ModuleOutput {
  return {
    summary: `Error: ${message}`,
    risks: ["Unable to process request"],
    recommended_actions: ["Review permissions and retry"],
  };
}
