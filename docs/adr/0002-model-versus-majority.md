# ADR 0002: Keep the logistic model only if it clears a frozen bar

## Status

Accepted before the measurement. The constants in `lakehouse_poc.decision` were not edited after the score.

## Decision

Train `LogisticRegression(C=1.0)` with no class weight. Score the refund class on orders `n >= 181` at probability 0.5. Recommend `logistic` only when its F1 is at least 0.05 above the majority baseline and its false-positive rate is at most 0.20. Otherwise recommend `majority`.

The baseline predicts the training majority. On this set that label is non-refund, so baseline refund F1 is 0 unless that changes.

## Consequences

A weak score stays a weak score. The acceptance check is that the published recommendation matches `choose`, not that the model wins.

## Result

`benchmarks/latest.json` records majority F1 0.0, logistic F1 0.0, logistic false-positive rate 0.0, and recommendation `majority`. The constants were not edited after that run.
