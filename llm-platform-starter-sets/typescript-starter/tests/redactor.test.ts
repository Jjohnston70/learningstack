/**
 * redactor.test.ts — Tests for the TypeScript redaction utility.
 *
 * Run: npm test
 */

import { redactText, redactRecord } from "../src/core/redactor";

describe("redactText", () => {
  it("redacts email addresses", () => {
    const result = redactText("Contact jacob@truenorthstrategyops.com for details.");
    expect(result).toContain("[REDACTED_EMAIL]");
    expect(result).not.toContain("jacob@truenorthstrategyops.com");
  });

  it("redacts phone numbers with dashes", () => {
    const result = redactText("Call 719-204-6365 today.");
    expect(result).toContain("[REDACTED_PHONE]");
    expect(result).not.toContain("719-204-6365");
  });

  it("redacts phone numbers with parentheses", () => {
    const result = redactText("Reach us at (719) 204-6365.");
    expect(result).toContain("[REDACTED_PHONE]");
  });

  it("passes clean text through unchanged", () => {
    const text = "The invoice total is $1,200 for the Command Center Build.";
    expect(redactText(text)).toBe(text);
  });

  it("redacts multiple emails", () => {
    const result = redactText("Send to alice@example.com and bob@company.org");
    expect((result.match(/\[REDACTED_EMAIL\]/g) || []).length).toBe(2);
  });

  it("handles empty string", () => {
    expect(redactText("")).toBe("");
  });
});

describe("redactRecord", () => {
  it("redacts email in string values", () => {
    const data = {
      user_request: "Email me at jacob@truenorthstrategyops.com",
      client_id: "client-alpha",
    };
    const result = redactRecord(data);
    expect(result["user_request"]).toContain("[REDACTED_EMAIL]");
    expect(result["client_id"]).toBe("client-alpha");
  });

  it("passes non-string values through unchanged", () => {
    const data = { count: 42, flags: [true, false], score: 3.14 };
    const result = redactRecord(data);
    expect(result["count"]).toBe(42);
    expect(result["flags"]).toEqual([true, false]);
  });

  it("handles empty object", () => {
    expect(redactRecord({})).toEqual({});
  });
});
