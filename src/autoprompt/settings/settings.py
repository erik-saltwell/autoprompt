from __future__ import annotations

from pathlib import Path
from typing import Annotated

import yaml
from pydantic import BaseModel, Field

from ..data import ModelEffort, ModelString


class LlmCallSettings(BaseModel, frozen=True):
    """Model configuration for a single LLM call site."""

    model: Annotated[
        ModelString,
        Field(description="Model identifier passed to LiteLLM for this LLM call."),
    ]
    effort: Annotated[
        ModelEffort,
        Field(description="Reasoning effort passed to LiteLLM for this LLM call."),
    ]


class PathSettings(BaseModel):
    prompt: Path
    output: Path
    input: Path


class Settings(BaseModel):
    paths: PathSettings
    prompt_generation: LlmCallSettings

    @classmethod
    def load(cls, settingsfilepath: Path) -> Settings:
        with open(settingsfilepath) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
