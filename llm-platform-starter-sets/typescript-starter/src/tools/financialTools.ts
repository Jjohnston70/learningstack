/**
 * financialTools.ts — Tool adapters for financial analysis operations.
 */

export interface InvoiceSummary {
  overdue_count: number;
  overdue_amount: number;
  pending_count: number;
  pending_amount: number;
  invoices: Array<{ id: string; client: string; amount: number; days_overdue: number }>;
  note?: string;
}

export async function getInvoiceSummary(
  spreadsheetId = "",
  sheetName = "Invoices"
): Promise<InvoiceSummary> {
  console.log(`[STUB] getInvoiceSummary — sheet=${sheetName}`);
  return {
    overdue_count: 0,
    overdue_amount: 0,
    pending_count: 0,
    pending_amount: 0,
    invoices: [],
    note: "[STUB] Real Sheets read not yet connected",
  };
}

export async function getCashflowData(
  spreadsheetId = "",
  weeksAhead = 4
): Promise<{
  inflow_projected: number;
  outflow_projected: number;
  net_position: number;
  weeks: string[];
  note?: string;
}> {
  console.log(`[STUB] getCashflowData — weeksAhead=${weeksAhead}`);
  return {
    inflow_projected: 0,
    outflow_projected: 0,
    net_position: 0,
    weeks: [],
    note: "[STUB] Real cash flow data not yet connected",
  };
}

export function calculateMargin(
  revenue: number,
  costs: number
): { gross_margin: number; margin_percent: number } {
  if (revenue === 0) return { gross_margin: 0, margin_percent: 0 };
  const gross_margin = revenue - costs;
  const margin_percent = (gross_margin / revenue) * 100;
  return {
    gross_margin: Math.round(gross_margin * 100) / 100,
    margin_percent: Math.round(margin_percent * 100) / 100,
  };
}
