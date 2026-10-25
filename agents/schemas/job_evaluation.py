from pydantic import BaseModel, Field

from agents.schemas.grouped_job_analysis import GroupedJobAnalysis
from agents.schemas.job import JobPosting


class JobEvaluationCase(BaseModel):
    name: str = Field(min_length=1)
    job: JobPosting
    expected: GroupedJobAnalysis


class JobEvaluationResult(BaseModel):
    case_name: str

    expected_count: int
    predicted_count: int

    matched_count: int
    missing_count: int
    unexpected_count: int

    precision: float
    recall: float
    f1: float
