# {Site Name} — Wave Deployment Guide

> **DESIGN SCAFFOLD — example shape only.** `generate-sharepoint-wave-scripts` reads this as a
> style reference and produces a NEW guide per migration, using real wave/object names from that
> run's `dependency-matrix.json`. Nothing in `{braces}` below is real content.

## Prerequisites

- `config.psd1` at the repository root, with a populated `Connection` block (see
  `workbench-setup`'s `initialize-workbench-config` skill).
- The dependency matrix for this migration: `{path to dependency-matrix.json}`.

## How to use this guide

Run **one wave at a time**. Never run every wave unattended in one pass — see
`../rules/test-driven-wave-deployment.md` for why. For each wave:

1. Run the wave's validation check — expect it to fail (the objects don't exist yet).
2. Deploy the wave (dry-run first, then for real, per `sharepoint-provisioning`'s existing
   three-gate write safety — injected executor, confirmation token).
3. Re-run the validation check — confirm it now passes.
4. Only then move to the next wave.

## Wave {N} — {short description}

**Objects in this wave:** {list of object names, from the matrix}

```bash
# validation (expect FAIL before deploying)
python3 -m plan_wave_{n} --check

# deploy (dry-run first)
python3 -m plan_wave_{n} --dry-run
python3 -m plan_wave_{n} --confirm {token}

# validation (expect PASS after deploying)
python3 -m plan_wave_{n} --check
```

Stop here and confirm this wave's validation passes before continuing.

---

*(One section like the above per computed wave, in dependency order.)*
