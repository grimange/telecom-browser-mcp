# Manual Vs Automated Probe Comparison

Manual probe:
- initialize request sent
- no initialize response observed
- raw stdout preview empty
- stderr tail empty
- classification: `transport_deadlock`

Automated probe:
- initialize request sent (captured transcript)
- no initialize response observed
- no tools/list phase reached
- classification: `handshake_timeout`

Conclusion:
- both manual and automated probes fail at the same boundary (no initialize response).
- this reduces likelihood of probe formatting-only defects.
