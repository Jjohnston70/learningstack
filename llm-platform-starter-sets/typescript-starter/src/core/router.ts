/**
 * router.ts — Maps user input to the correct module using keyword matching.
 */

import { ClientConfig, ModuleConfig } from "./types";
import { loadModuleConfig } from "./configLoader";

export function routeRequest(userInput: string, client: ClientConfig): ModuleConfig {
  const inputLower = userInput.toLowerCase();

  for (const moduleName of client.active_modules) {
    const module = loadModuleConfig(moduleName);
    for (const keyword of module.keywords ?? []) {
      if (inputLower.includes(keyword.toLowerCase())) {
        return module;
      }
    }
  }

  // Fallback: first active module
  if (client.active_modules.length > 0) {
    return loadModuleConfig(client.active_modules[0]);
  }

  throw new Error(`No modules available for client: ${client.client_id}`);
}
