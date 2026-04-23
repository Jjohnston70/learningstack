# integration-notes.md — [your-module-name]

## What This Module Does

One paragraph plain-English summary of the module's purpose and what business workflow it serves.

---

## Setup Steps

In order, the steps required before this module is production-ready:

### 1. Deploy Apps Script web app (if applicable)

If this module calls an Apps Script project:

1. Open the script in Google Apps Script editor
2. Click Deploy → New deployment → Web app
3. Set "Who has access" to "Anyone" (or service account)
4. Copy the deployment URL
5. Add to environment: `YOUR_SCRIPT_URL=https://script.google.com/macros/s/SCRIPT_ID/exec`

### 2. Set required environment variables

```bash
# Required
YOUR_MODULE_RESOURCE_ID=...
ANTHROPIC_API_KEY=...

# Optional
YOUR_OPTIONAL_RESOURCE_ID=...
```

### 3. Verify tool adapters

Run a smoke test to confirm tool stubs respond:

```bash
python -c "from app.tools.your_tools import get_data_example; print(get_data_example())"
```

### 4. Run module tests

```bash
python -m pytest module-template/tests/test_module.py -v
```

---

## Integration Risks and Gotchas

Document gotchas discovered during integration here.

| Risk | Severity | Mitigation |
|------|----------|------------|
| Apps Script active-sheet dependency | Medium | Deploy as web app, not UI-bound |
| Missing resource IDs cause silent failures | Medium | Validate env vars at startup |
| LLM may fabricate data not in context | High | instructions.md must say "do not invent" |

---

## Known Limitations

- List anything the module can't currently do that users might expect
- List anything that requires manual intervention

---

## Rollout Notes

- Stage 1: Deploy in knowledge-only mode, validate retrieval quality
- Stage 2: Enable read tools after confirming data sources are accessible
- Stage 3: Enable write tools only after explicit approval gate is tested
- Stage 4: Promote to production after 1 week of staging validation

---

## Testing Checklist

Before marking this module production-ready:

- [ ] `test_module.py` passes
- [ ] Output schema fields validated
- [ ] Redaction verified (no PII in log output)
- [ ] Tool stubs replaced with real adapters (Phase 5+)
- [ ] Permission checks tested (denied path works)
- [ ] One complete end-to-end request traced from input to log
- [ ] instructions.md reviewed and matches actual behavior

---

## Migration Notes

_Fill this in if this module replaces or upgrades an existing system._

| Previous system | How this module replaces it |
|---|---|
| (old Apps Script project) | Wrapped as tool adapter in adapters/python/module.py |
