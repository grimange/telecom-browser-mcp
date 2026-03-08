# Safe Tool Smoke Test

## Sequence

1. `health` with no arguments
2. `capabilities` with no arguments
3. `list_sessions` with no arguments
4. `capabilities` with optional `include_groups=false`

## Expected outcomes

- all calls return structured envelope (`ok`, `message`, `data`, `warnings`)
- no invocation raises `unexpected keyword argument 'kwargs'`
- optional argument path is accepted both directly and via legacy wrapped payload

## Observed

See `smoke-test-results.json` for executed steps and outcomes.
