/**
 * proposalTools.ts — Tool adapters for proposal generation workflows.
 */

export async function buildProposalDocument(args: {
  clientName: string;
  deliverables: string[];
  timeline: string;
  templateId?: string;
}): Promise<{ document_url: string; document_id: string; note?: string }> {
  console.log(`[STUB] buildProposalDocument — client=${args.clientName}`);
  return {
    document_url: "",
    document_id: "",
    note: "[STUB] Real document generation not yet connected",
  };
}

export async function logProposalToTracker(args: {
  clientName: string;
  proposalSummary: string;
  spreadsheetId?: string;
}): Promise<{ row_added: boolean; note?: string }> {
  console.log(`[STUB] logProposalToTracker — client=${args.clientName}`);
  return {
    row_added: false,
    note: "[STUB] Real tracking log not yet connected",
  };
}

export async function sendProposalEmail(args: {
  recipientEmail: string;
  proposalUrl: string;
  clientName: string;
}): Promise<{ sent: boolean; note?: string }> {
  // NOTE: recipientEmail intentionally not logged here
  console.log(`[STUB] sendProposalEmail — client=${args.clientName}`);
  return {
    sent: false,
    note: "[STUB] Real email send not yet connected",
  };
}
