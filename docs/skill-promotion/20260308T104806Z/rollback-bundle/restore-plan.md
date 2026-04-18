# Rollback Conditions

- Trigger rollback on post-promotion regression or safety-policy violation.

# Restore Steps
1. Restore previous live SKILL.md from VCS backup.
2. Re-run eval harness against restored live skill.
3. Record rollback evidence under docs/skill-promotion/rollback/.

# Validation Checklist
- [ ] Live skill restored
- [ ] Harness rerun complete
- [ ] Regression cleared
