# Proposal Templates

This folder contains proposal template references for the proposal-command module.

## What goes here

- Google Doc template IDs (stored in dependencies.yaml, not hardcoded)
- Sample proposal markdown stubs
- Pricing range reference documents
- Scope-of-work section templates

## How proposal-command uses these

The `proposal_generator` tool adapter calls an Apps Script web app
that merges client data into the Google Doc template and saves the output
to the PROPOSALS_FOLDER_ID Drive folder.

The LLM runtime uses these templates as:
- Output format reference (what a good proposal looks like)
- Retrieval source for "what should be included in a proposal" questions
- Validation reference for required sections

## Template IDs

Store template document IDs in your environment, not here:

```
PROPOSAL_TEMPLATE_ID=1abc...xyz
PROPOSALS_FOLDER_ID=1def...uvw
PROPOSAL_SPREADSHEET_ID=1ghi...rst
```

Never commit real document IDs or spreadsheet IDs to source control.
