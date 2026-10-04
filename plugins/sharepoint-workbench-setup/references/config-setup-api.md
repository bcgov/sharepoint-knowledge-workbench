# Workbench config setup API

## Contents

- [Public interface](#public-interface)
- [Validation, overwrite and connection test](#validation-overwrite-and-connection-test)
- [Connection test connector](#connection-test-connector)

## Public interface

```python
from config_setup import validate_connection_answers, write_config, test_connection

issues = validate_connection_answers(connection, authentication)  # [] means valid
output_path = write_config(repo_root, connection, authentication, defaults)
# repo_root / "config.psd1"

# Explicit, opt-in only -- never called by write_config:
test_connection(connection, connector=my_live_connector)  # raises NotImplementedError without one
```

## Validation, overwrite and connection test

`write_config` validates first (raises `ConfigSetupError` and writes nothing on failure)
and refuses to silently overwrite an existing `config.psd1` unless `overwrite=True` is
passed explicitly.

`test_connection` requires an injected `connector` callable. This module ships no live
SharePoint SDK/PnP connector itself, so calling it without one raises
`NotImplementedError` rather than silently no-op'ing or faking success.

## Connection test connector

The `workbench-validate-sharepoint-connection` skill provides
`make_device_code_connector(http_client)`, a real connector (device-code auth plus an
`_api/contextinfo` smoke test). Wiring it in is always an explicit, opt-in caller choice,
never a default. To run a connection test, invoke that skill and have it supply the
connector; do not import its scripts from this skill.

Design provenance (source repository only; not needed at runtime):
`docs/superpowers/specs/2026-08-02-multi-document-destination-configuration-design.md`, Section 1.
