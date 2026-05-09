from __future__ import annotations

from deepeval.test_case import LLMTestCase

from ..data import PromptData
from ..helpers import completions_manager
from ..metrics.alignment import AlignmentMetric
from ..metrics.coverage import CoverageMetric
from .base_command import BaseCommand


class TestCommand(BaseCommand):
    def name(self) -> str:
        return "Test Command"

    def execute_command(self) -> None:
        settings = self.settings
        prompt: PromptData = PromptData(system_prompt=settings.paths.prompt.read_text(), user_prompt=settings.paths.input.read_text())
        if settings.paths.output.exists():
            output_text = settings.paths.output.read_text()
        else:
            output_text: str = completions_manager.get_completion(prompt, settings.prompt_generation.model, settings.prompt_generation.effort, self.tracer)
            settings.paths.output.write_text(output_text)

        test_case: LLMTestCase = LLMTestCase(input=prompt.user_prompt, actual_output=output_text)

        alignment = AlignmentMetric(threshold=0.95, include_reason=True, async_mode=False, strict_mode=False, verbose_mode=False)
        alignment.measure(test_case)
        self.tracer.add_context("alignment_score", alignment.score)
        self.logger.report_message(f"Alignment score: {alignment.score} (threshold {alignment.threshold}) - {alignment.reason}")

        coverage = CoverageMetric(threshold=0.95, n=5, include_reason=True, async_mode=False, strict_mode=False, verbose_mode=False)
        coverage.measure(test_case)
        self.tracer.add_context("coverage_score", coverage.score)
        self.logger.report_message(f"Coverage score: {coverage.score} (threshold {coverage.threshold}) - {coverage.reason}")
