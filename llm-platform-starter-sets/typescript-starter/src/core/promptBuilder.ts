/**
 * promptBuilder.ts — Assembles the final prompt from structured inputs.
 *
 * Deterministic assembly. No copy-paste prompt soup.
 */

import * as fs from "fs";
import * as path from "path";

const MODULES_DIR = path.resolve(__dirname, "../modules");

export function loadModuleInstructions(moduleName: string): string {
  const folderName = moduleName.replace(/-/g, "_");
  const filePath = path.join(MODULES_DIR, folderName, "instructions.md");
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath, "utf-8");
  }
  return `(No instructions file found for module: ${moduleName})`;
}

export function buildPrompt(args: {
  clientName: string;
  tone: string;
  moduleName: string;
  moduleInstructions: string;
  userRequest: string;
  dataSources: string[];
  outputFields: string[];
}): string {
  const dataSourceText =
    args.dataSources.length > 0 ? args.dataSources.join(", ") : "none provided";
  const outputFieldText =
    args.outputFields.length > 0 ? args.outputFields.join(", ") : "freeform response";

  return `You are operating for client: ${args.clientName}.
Response tone: ${args.tone}.
Selected module: ${args.moduleName}.

Module instructions:
${args.moduleInstructions}

Approved data sources for this request:
${dataSourceText}

User request:
${args.userRequest}

Required output fields:
${outputFieldText}

Rules:
- Do not invent facts not present in the provided context.
- Clearly label any assumptions.
- Return a concise, structured response matching the required output fields.`.trim();
}
