# Rollback Notes

Manual rollback plan:
1. Revert promoted skill commit to previous known-good revision.
2. Re-run eval plan for restored revision.
3. Record rollback evidence under docs/skill-evolution/rollbacks/.
