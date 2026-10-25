import json
from pathlib import Path

from agents.services.skill_relationship_resolver import (
    SkillRelationshipResolver,
)

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "skill_matching.json"


def load_dataset() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_metrics(
    true_positives: int,
    false_positives: int,
    false_negatives: int,
    true_negatives: int,
) -> dict[str, float]:

    total = true_positives + false_positives + false_negatives + true_negatives

    accuracy = (true_positives + true_negatives) / total if total else 0.0

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )

    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )

    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def evaluate() -> None:
    dataset = load_dataset()
    resolver = SkillRelationshipResolver()

    tp = fp = fn = tn = 0
    errors = []

    for example in dataset:
        candidate_skill = example["candidate_skill"]
        required_skill = example["required_skill"]
        expected = example["expected_match"]

        match_type = resolver.resolve(
            candidate_skill=candidate_skill,
            required_skill=required_skill,
        )

        predicted = match_type is not None

        if predicted and expected:
            tp += 1
        elif predicted and not expected:
            fp += 1
        elif not predicted and expected:
            fn += 1
        else:
            tn += 1

        if predicted != expected:
            errors.append(
                {
                    "candidate_skill": candidate_skill,
                    "required_skill": required_skill,
                    "expected": expected,
                    "predicted": predicted,
                    "category": example["category"],
                }
            )

    metrics = calculate_metrics(
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        true_negatives=tn,
    )

    print("\n=== SkillGraph Matching Evaluation ===")
    print(f"Total examples: {len(dataset)}")

    print("\nConfusion Matrix")
    print(f"TP: {tp}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"TN: {tn}")

    print("\nMetrics")

    for name, value in metrics.items():
        print(f"{name.capitalize()}: {value:.3f}")

    print("\nIncorrect Predictions")

    if not errors:
        print("None")
    else:
        for error in errors:
            print(
                f"[{error['category']}] "
                f"{error['candidate_skill']} → "
                f"{error['required_skill']} | "
                f"expected={error['expected']}, "
                f"predicted={error['predicted']}"
            )


if __name__ == "__main__":
    evaluate()
