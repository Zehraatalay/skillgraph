from collections import Counter
import json
from pathlib import Path

from app.jobs.skill_registry import is_known_skill

DATASET = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "curated_jobs"
    / "job_postings.json"
)

jobs = json.loads(DATASET.read_text())

missing = Counter()

for job in jobs:
    for skill in (
        job["required_skills"]
        + job["preferred_skills"]
    ):
        name = skill["name"]

        if not is_known_skill(name):
            missing[name] += 1

print("=" * 60)
print("Missing skills:", len(missing))
print("=" * 60)

for skill, count in sorted(missing.items()):
    print(f"{skill:<35} {count}")