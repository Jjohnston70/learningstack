/**
 * logger.ts — Creates safe structured execution log events.
 */

import { ExecutionContext, LogEvent } from "./types";
import { redactRecord } from "./redactor";

export function buildLogEvent(
  eventType: string,
  context: ExecutionContext,
  outputValid: boolean
): Record<string, unknown> {
  const rawEvent: LogEvent = {
    event_type: eventType,
    client_id: context.clientId,
    module_name: context.moduleName,
    module_version: context.moduleVersion,
    user_request: context.userRequest,   // will be redacted
    data_sources: context.dataSources.join(", "),
    output_valid: String(outputValid),
  };

  return redactRecord(rawEvent as unknown as Record<string, unknown>);
}
