import asyncio

from deepeval.metrics import BaseMetric
from deepeval.metrics.indicator import metric_progress_indicator
from deepeval.metrics.utils import (
    a_generate_with_schema_and_extract,
    check_llm_test_case_params,
    construct_verbose_logs,
    generate_with_schema_and_extract,
    initialize_model,
)
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, SingleTurnParams
from deepeval.utils import get_or_create_event_loop, prettify_list

from .schema import Answers, CoverageScoreReason, CoverageVerdict, Questions
from .template import CoverageTemplate


class CoverageMetric(BaseMetric):
    _required_params: list[SingleTurnParams] = [
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
    ]

    def __init__(
        self,
        threshold: float = 0.5,
        n: int = 5,
        model: str | DeepEvalBaseLLM | None = None,
        assessment_questions: list[str] | None = None,
        include_reason: bool = True,
        async_mode: bool = True,
        strict_mode: bool = False,
        verbose_mode: bool = False,
    ):
        self.threshold = 1 if strict_mode else threshold
        self.model, self.using_native_model = initialize_model(model)
        self.evaluation_model = self.model.get_model_name()
        self.n = n
        if assessment_questions is not None and len(assessment_questions) == 0:
            self.assessment_questions = None
        else:
            self.assessment_questions = assessment_questions
        self.include_reason = include_reason
        self.async_mode = async_mode
        self.strict_mode = strict_mode
        self.verbose_mode = verbose_mode

    def _calculate_score(self) -> float:
        if self.assessment_questions is None:
            return 1
        total = sum(1 for v in self.verdicts if v.original_verdict.strip().lower() == "yes")
        if total == 0:
            return 0
        covered = sum(1 for v in self.verdicts if v.original_verdict.strip().lower() == "yes" and v.summary_verdict.strip().lower() == "yes")
        score = covered / total
        return 0 if self.strict_mode and score < self.threshold else score

    def _generate_reason(self) -> str | None:
        if not self.include_reason:
            return None
        uncovered = [v.question for v in self.verdicts if v.original_verdict.strip().lower() == "yes" and v.summary_verdict.strip().lower() == "no"]
        prompt = CoverageTemplate.generate_reason(
            questions=uncovered,
            score=format(self.score, ".2f"),
        )
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=CoverageScoreReason,
            extract_schema=lambda s: s.reason,
            extract_json=lambda data: data["reason"],
        )

    def _generate_assessment_questions(self, text: str) -> list[str]:
        prompt = CoverageTemplate.generate_questions(text=text, n=self.n)
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Questions,
            extract_schema=lambda s: s.questions,
            extract_json=lambda data: data["questions"],
        )

    def _generate_answers(self, text: str) -> list[str]:
        prompt = CoverageTemplate.generate_answers(questions=self.assessment_questions, text=text)
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Answers,
            extract_schema=lambda s: s.answers,
            extract_json=lambda data: data["answers"],
        )

    def _generate_verdicts(self, test_case: LLMTestCase) -> list[CoverageVerdict]:
        if self.assessment_questions is None:
            self.assessment_questions = self._generate_assessment_questions(test_case.input)
        original_answers = self._generate_answers(test_case.input)
        assert test_case.actual_output is not None
        summary_answers = self._generate_answers(test_case.actual_output)
        if len(original_answers) != len(summary_answers):
            raise ValueError("Number of answers generated does not match number of questions.")
        return [
            CoverageVerdict(
                summary_verdict=summary_answers[i],
                original_verdict=original_answers[i],
                question=self.assessment_questions[i],
            )
            for i in range(len(original_answers))
        ]

    def measure(
        self,
        test_case: LLMTestCase,
        _show_indicator: bool = True,
        _in_component: bool = False,
        _log_metric_to_confident: bool = True,
    ) -> float:
        check_llm_test_case_params(test_case, self._required_params, None, None, self, self.model, test_case.multimodal)
        self.evaluation_cost = 0 if self.using_native_model else None
        with metric_progress_indicator(self, _show_indicator=_show_indicator, _in_component=_in_component):
            if self.async_mode:
                loop = get_or_create_event_loop()
                loop.run_until_complete(
                    self.a_measure(
                        test_case,
                        _show_indicator=False,
                        _in_component=_in_component,
                        _log_metric_to_confident=_log_metric_to_confident,
                    )
                )
            else:
                self.verdicts: list[CoverageVerdict] = self._generate_verdicts(test_case)
                self.score = self._calculate_score()
                self.reason = self._generate_reason()
                self.success = self.score >= self.threshold
                self.verbose_logs = construct_verbose_logs(
                    self,
                    steps=[
                        f"Assessment Questions:\n{prettify_list(self.assessment_questions)}",  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
                        f"Coverage Verdicts:\n{prettify_list(self.verdicts)}",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
        assert self.score is not None
        return self.score

    async def _a_generate_reason(self) -> str | None:
        if not self.include_reason:
            return None
        uncovered = [v.question for v in self.verdicts if v.original_verdict.strip().lower() == "yes" and v.summary_verdict.strip().lower() == "no"]
        prompt = CoverageTemplate.generate_reason(
            questions=uncovered,
            score=format(self.score, ".2f"),
        )
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=CoverageScoreReason,
            extract_schema=lambda s: s.reason,
            extract_json=lambda data: data["reason"],
        )

    async def _a_generate_assessment_questions(self, text: str) -> list[str]:
        prompt = CoverageTemplate.generate_questions(text=text, n=self.n)
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Questions,
            extract_schema=lambda s: s.questions,
            extract_json=lambda data: data["questions"],
        )

    async def _a_generate_answers(self, text: str) -> list[str]:
        prompt = CoverageTemplate.generate_answers(questions=self.assessment_questions, text=text)
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Answers,
            extract_schema=lambda s: s.answers,
            extract_json=lambda data: data["answers"],
        )

    async def _a_generate_verdicts(self, test_case: LLMTestCase) -> list[CoverageVerdict]:
        if self.assessment_questions is None:
            self.assessment_questions = await self._a_generate_assessment_questions(test_case.input)
        assert test_case.actual_output is not None
        original_answers, summary_answers = await asyncio.gather(
            self._a_generate_answers(test_case.input),
            self._a_generate_answers(test_case.actual_output),
        )
        if len(original_answers) != len(summary_answers):
            raise ValueError("Number of answers generated does not match number of questions.")
        return [
            CoverageVerdict(
                summary_verdict=summary_answers[i],
                original_verdict=original_answers[i],
                question=self.assessment_questions[i],
            )
            for i in range(len(original_answers))
        ]

    async def a_measure(
        self,
        test_case: LLMTestCase,
        _show_indicator: bool = True,
        _in_component: bool = False,
        _log_metric_to_confident: bool = True,
    ) -> float:
        check_llm_test_case_params(test_case, self._required_params, None, None, self, self.model, test_case.multimodal)
        self.evaluation_cost = 0 if self.using_native_model else None
        with metric_progress_indicator(self, async_mode=True, _show_indicator=_show_indicator, _in_component=_in_component):
            self.verdicts = await self._a_generate_verdicts(test_case)
            self.score = self._calculate_score()
            self.reason = await self._a_generate_reason()
            self.success = self.score >= self.threshold
            self.verbose_logs = construct_verbose_logs(
                self,
                steps=[
                    f"Assessment Questions:\n{prettify_list(self.assessment_questions)}",  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]
                    f"Coverage Verdicts:\n{prettify_list(self.verdicts)}",
                    f"Score: {self.score}\nReason: {self.reason}",
                ],
            )
        return self.score

    def is_successful(self) -> bool:
        if self.error is not None:
            self.success = False
        else:
            try:
                assert self.score is not None
                self.success = self.score >= self.threshold
            except TypeError:
                self.success = False
        return self.success

    @property
    def __name__(self):  # type: ignore[override]
        return "Coverage"
