# Adapter Developer Notes

## Purpose

Adapters isolate app-specific logic from shared MCP/browser lifecycle code.

## Current adapters

- `apntalk`: scaffold adapter, intended first real implementation target
- `generic_sipjs`: generic SIP.js scaffold
- `generic_jssip`: generic JsSIP scaffold
- `harness`: deterministic fake dialer adapter for tests

## Contract summary

Adapters must implement telecom-intent methods only (open/login/ready/registration/incoming/answer/hangup/snapshots).

## Assumptions must be explicit

Document adapter assumptions for:

- selectors used
- runtime global paths
- store hooks
- readiness gates
- compatibility version notes

## Rules

- keep adapter-specific selectors in adapter files
- do not create browser contexts from adapters
- return normalized model shapes from adapter APIs
- if unknown, return explicit `available=false` and `reason`
