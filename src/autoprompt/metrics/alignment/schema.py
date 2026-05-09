from typing import Literal

from pydantic import BaseModel, Field


class AlignmentVerdict(BaseModel):
    verdict: Literal["yes", "no", "idk"]
    reason: str | None = Field(default=None)


class AlignmentVerdicts(BaseModel):
    verdicts: list[AlignmentVerdict]


class AlignmentScoreReason(BaseModel):
    reason: str
