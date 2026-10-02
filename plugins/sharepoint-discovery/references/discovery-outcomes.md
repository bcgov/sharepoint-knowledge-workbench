# Discovery outcome statuses

## Contents

- [Statuses](#statuses)
- [Rules](#rules)

Shared by the discovery analysis skills, which are read-only and consume an export you supply.

## Statuses

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:

- `OBSERVED`: the input was read and analysed.
- `EMPTY`: the input was valid but held nothing to analyse. Never a pass.
- `PARTIAL`: some of the input was usable.
- `UNAVAILABLE`: a required input file is missing. No output directory is created.
- `FORBIDDEN`: access to the input was denied.
- `FAILED`: the input is the wrong shape (for example a JSON array where an object is expected).

## Rules

- Report the status as returned. Don't turn `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN` or
  `FAILED` into a success.
- Helpers live in `scripts/discovery_inputs.py`: `DiscoveryStatus`, `DiscoveryOutcome`,
  `load_json_input`, `require_output_dir`.
