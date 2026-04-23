/**
 * contextBuilder.ts — Builds the structured ExecutionContext object.
 *
 * Structure beats chaos. This is the canonical object passed through
 * all runtime layers. Never pass raw strings between components.
 */

import { ClientConfig, ModuleConfig, ExecutionContext } from "./types";
import { getClientTone, getClientPermissions } from "./configLoader";

export function buildContext(
  client: ClientConfig,
  module: ModuleConfig,
  userRequest: string
): ExecutionContext {
  return {
    clientId: client.client_id,
    clientName: client.name,
    tone: getClientTone(client),
    moduleName: module.name,
    moduleVersion: module.version,
    userRequest,
    dataSources: client.data_sources ?? [],
    permissions: getClientPermissions(client, module.name),
    outputFields: module.output_fields ?? [],
  };
}
