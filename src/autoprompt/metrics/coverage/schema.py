from pydantic import BaseModel, Field


class CoverageVerdict(BaseModel):
    summary_verdict: str
    original_verdict: str
    question: str | None = Field(default=None)


class Questions(BaseModel):
    questions: list[str]


class Answers(BaseModel):
    answers: list[str]


class CoverageScoreReason(BaseModel):
    reason: str
