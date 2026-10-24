# Deployment Decision Principles

1. Topological dependency ordering must precede execution.
2. Every tenant mutation requires dry-run validation and an explicit execution token.
3. Waves execute sequentially with verification gates between waves.
