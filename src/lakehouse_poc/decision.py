"""Refund-model rule. Written before the workstation measurement.

Do not edit the margin, the cap, the threshold, or MODEL_C to change the recommendation.
"""

F1_MARGIN = 0.05
FPR_CAP = 0.20
THRESHOLD = 0.5
MODEL_C = 1.0


def choose(model_f1: float, baseline_f1: float, model_fpr: float) -> str:
    if model_f1 >= baseline_f1 + F1_MARGIN and model_fpr <= FPR_CAP:
        return "logistic"
    return "majority"
