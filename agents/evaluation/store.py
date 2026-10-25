import json
from pathlib import Path

from agents.schemas.grouped_job_analysis import GroupedJobAnalysis


class EvaluationStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        name: str,
        predictions: dict[str, GroupedJobAnalysis],
    ) -> Path:
        if not name or not name.replace("-", "_").replace("_", "").isalnum():
            raise ValueError("Invalid evaluation name")

        path = self.directory / f"{name}.json"

        data = {
            job_id: analysis.model_dump(mode="json")
            for job_id, analysis in predictions.items()
        }

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return path

    def load(
        self,
        name: str,
    ) -> dict[str, GroupedJobAnalysis]:
        if not name or not name.replace("-", "_").replace("_", "").isalnum():
            raise ValueError("Invalid evaluation name")

        path = self.directory / f"{name}.json"

        data = json.loads(path.read_text(encoding="utf-8"))

        return {
            job_id: GroupedJobAnalysis.model_validate(value)
            for job_id, value in data.items()
        }
