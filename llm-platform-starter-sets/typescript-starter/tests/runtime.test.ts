/**
 * runtime.test.ts — Integration tests for the TypeScript runtime pipeline.
 */

import { loadClient, loadModuleConfig } from "../src/core/configLoader";
import { routeRequest } from "../src/core/router";
import { buildContext } from "../src/core/contextBuilder";
import { executeRequest } from "../src/core/runtime";

describe("Config Loading", () => {
  it("loads client-alpha config", () => {
    const client = loadClient("client-alpha");
    expect(client.client_id).toBe("client-alpha");
    expect(client.active_modules).toContain("financial-command");
  });

  it("loads financial-command module config", () => {
    const module = loadModuleConfig("financial-command");
    expect(module.name).toBe("financial-command");
    expect(module.output_fields).toBeDefined();
    expect(module.output_fields!.length).toBeGreaterThan(0);
  });

  it("throws on missing client", () => {
    expect(() => loadClient("does-not-exist")).toThrow();
  });
});

describe("Routing", () => {
  it("routes financial keywords to financial-command", () => {
    const client = loadClient("client-alpha");
    const module = routeRequest("Show me overdue invoices and cash flow risk", client);
    expect(module.name).toBe("financial-command");
  });

  it("routes proposal keywords to proposal-command", () => {
    const client = loadClient("client-alpha");
    const module = routeRequest("Generate a proposal for the Command Center Build", client);
    expect(module.name).toBe("proposal-command");
  });

  it("falls back to first active module on no match", () => {
    const client = loadClient("client-alpha");
    const module = routeRequest("something completely unrelated xyz", client);
    expect(client.active_modules).toContain(module.name);
  });
});

describe("Context Builder", () => {
  it("builds context with required fields", () => {
    const client = loadClient("client-alpha");
    const module = loadModuleConfig("financial-command");
    const context = buildContext(client, module, "Test request");
    expect(context.clientId).toBe("client-alpha");
    expect(context.moduleName).toBe("financial-command");
    expect(Array.isArray(context.dataSources)).toBe(true);
    expect(Array.isArray(context.outputFields)).toBe(true);
  });
});

describe("Full Pipeline", () => {
  it("executes request and returns a result", async () => {
    const result = await executeRequest({
      clientId: "client-alpha",
      userInput: "Summarize overdue invoices and cash flow risk.",
    });
    expect(result.moduleName).toBe("financial-command");
    expect(typeof result.success).toBe("boolean");
    expect(typeof result.output).toBe("object");
  });
});
