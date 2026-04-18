# 13 No Regression Guards

## Guard G-01
- Assert registered tool set equals canonical contract map tool set.

## Guard G-02
- Assert every registered tool response validates against canonical response envelope model.

## Guard G-03
- Add lifecycle state-machine tests for `ready/degraded/broken/closing/closed` transitions.

## Guard G-04
- Add artifact redaction tests for token/password/cookie/SIP-id patterns.

## Guard G-05
- Update stdio integration smoke to fail unknown exceptions instead of skipping.
