# Tool Contract Guidelines

1. Register tools with signatures matching implementation callables.
2. Avoid exposing `**kwargs` wrappers as public tool schemas.
3. Keep additive contract changes only; do not rename/remove fields.
4. Provide at least one deterministic no-arg tool for first-contact smoke (`health`).
5. Provide one low-risk optional-arg tool for compatibility checks (`capabilities`).
6. Keep session-bound tools explicit about required `session_id`.
7. Preserve structured envelope format for success and failures.
8. Treat sandbox transport failures separately from product contract failures.
