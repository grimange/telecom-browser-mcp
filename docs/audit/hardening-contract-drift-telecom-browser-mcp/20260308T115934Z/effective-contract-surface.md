# Effective Contract Surface

## Input
- All registered tools receive explicit inputs with strict validation.
- Unknown/undeclared fields are rejected as `invalid_input`.

## Output
- Registered tools return canonical `ToolResponse` shape via tool service helpers.

## Error
- Error codes sourced from centralized taxonomy (`errors/codes.py`).
- Common mappings include `invalid_input`, `session_not_found`, `session_broken`, and action-specific codes.

## Residual Risk
- Structural drift risk is now primarily around future evolution discipline, not active mismatch.
