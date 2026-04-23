/**
 * validator.ts — Validates that module output matches the expected schema.
 */

import { ValidationResult } from "./types";

export function validateOutput(
  output: Record<string, unknown>,
  requiredFields: string[]
): ValidationResult {
  const errors: string[] = [];

  for (const field of requiredFields) {
    if (!(field in output)) {
      errors.push(`Missing required field: ${field}`);
      continue;
    }

    const value = output[field];

    if (value === null || value === undefined) {
      errors.push(`Field is null or undefined: ${field}`);
    } else if (typeof value === "string" && value.trim().length === 0) {
      errors.push(`Field is empty string: ${field}`);
    } else if (Array.isArray(value) && value.length === 0) {
      errors.push(`Field is empty list: ${field}`);
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}
