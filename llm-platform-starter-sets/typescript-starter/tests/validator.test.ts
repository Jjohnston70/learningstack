/**
 * validator.test.ts — Tests for the TypeScript output validation utility.
 */

import { validateOutput } from "../src/core/validator";

describe("validateOutput", () => {
  const requiredFields = ["summary", "risks", "recommended_actions"];

  it("passes valid output", () => {
    const output = {
      summary: "Three invoices are overdue.",
      risks: ["Cash flow pressure increasing"],
      recommended_actions: ["Follow up with top debtor today"],
    };
    const { isValid, errors } = validateOutput(output, requiredFields);
    expect(isValid).toBe(true);
    expect(errors).toHaveLength(0);
  });

  it("fails when field is missing", () => {
    const output = { summary: "Summary only" };
    const { isValid, errors } = validateOutput(output, requiredFields);
    expect(isValid).toBe(false);
    expect(errors.some((e) => e.includes("risks"))).toBe(true);
  });

  it("fails when field is null", () => {
    const output = { summary: null, risks: ["Risk"], recommended_actions: ["Action"] };
    const { isValid, errors } = validateOutput(output as any, requiredFields);
    expect(isValid).toBe(false);
    expect(errors.some((e) => e.includes("null"))).toBe(true);
  });

  it("fails when string field is empty", () => {
    const output = { summary: "   ", risks: ["Risk"], recommended_actions: ["Action"] };
    const { isValid, errors } = validateOutput(output, requiredFields);
    expect(isValid).toBe(false);
  });

  it("fails when list field is empty", () => {
    const output = { summary: "Summary", risks: [], recommended_actions: ["Action"] };
    const { isValid, errors } = validateOutput(output, requiredFields);
    expect(isValid).toBe(false);
    expect(errors.some((e) => e.includes("risks"))).toBe(true);
  });

  it("passes with no required fields", () => {
    const { isValid } = validateOutput({ anything: "goes" }, []);
    expect(isValid).toBe(true);
  });

  it("ignores extra fields", () => {
    const output = {
      summary: "Summary",
      risks: ["Risk"],
      recommended_actions: ["Action"],
      extra_field: "This is fine",
    };
    const { isValid } = validateOutput(output, requiredFields);
    expect(isValid).toBe(true);
  });
});
