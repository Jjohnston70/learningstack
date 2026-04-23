/**
 * main.ts — Local runner for testing the TypeScript platform starter.
 *
 * Run: npx ts-node src/main.ts
 */

import { executeRequest } from "./core/runtime";
import { ExecutionRequest } from "./core/types";

async function main(): Promise<void> {
  console.log("=== Modular LLM Platform Starter (TypeScript) ===\n");

  // Example request — financial analysis
  const request: ExecutionRequest = {
    clientId: "client-alpha",
    userInput: "Summarize overdue invoices and identify top cash flow risks.",
  };

  console.log(`Client: ${request.clientId}`);
  console.log(`Request: ${request.userInput}\n`);

  const result = await executeRequest(request);

  console.log("\n=== Result ===");
  console.log(`Module: ${result.moduleName}`);
  console.log(`Success: ${result.success}`);
  if (result.errors.length > 0) {
    console.log("Errors:", result.errors);
  }
  console.log("Output:", JSON.stringify(result.output, null, 2));
}

main().catch(console.error);
