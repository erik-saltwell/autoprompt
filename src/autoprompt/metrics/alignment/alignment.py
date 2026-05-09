import asyncio

from deepeval.metrics import BaseMetric
from deepeval.metrics.faithfulness.schema import Claims, Truths
from deepeval.metrics.faithfulness.template import FaithfulnessTemplate
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

from .schema import AlignmentScoreReason, AlignmentVerdict, AlignmentVerdicts
from .template import AlignmentTemplate


class AlignmentMetric(BaseMetric):
    _required_params: list[SingleTurnParams] = [
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
    ]

    def __init__(
        self,
        threshold: float = 0.5,
        model: str | DeepEvalBaseLLM | None = None,
        include_reason: bool = True,
        async_mode: bool = True,
        strict_mode: bool = False,
        verbose_mode: bool = False,
        truths_extraction_limit: int | None = None,
    ):
        self.threshold = 1 if strict_mode else threshold
        self.model, self.using_native_model = initialize_model(model)
        self.evaluation_model = self.model.get_model_name()
        self.include_reason = include_reason
        self.async_mode = async_mode
        self.strict_mode = strict_mode
        self.verbose_mode = verbose_mode
        self.truths_extraction_limit = truths_extraction_limit
        if self.truths_extraction_limit is not None:
            self.truths_extraction_limit = max(self.truths_extraction_limit, 0)

    def _calculate_score(self) -> float:
        total = len(self.verdicts)
        if total == 0:
            return 0
        faithful_count = sum(1 for v in self.verdicts if v.verdict.strip().lower() == "yes")
        score = faithful_count / total
        return 0 if self.strict_mode and score < self.threshold else score

    def _generate_reason(self) -> str | None:
        if not self.include_reason:
            return None
        contradictions = [v.reason for v in self.verdicts if v.verdict.strip().lower() == "no"]
        redundancies = [v.reason for v in self.verdicts if v.verdict.strip().lower() == "idk"]
        prompt = AlignmentTemplate.generate_reason(
            contradictions=contradictions,
            redundancies=redundancies,
            score=format(self.score, ".2f"),
        )
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=AlignmentScoreReason,
            extract_schema=lambda s: s.reason,
            extract_json=lambda data: data["reason"],
        )

    def _generate_verdicts(self) -> list[AlignmentVerdict]:
        if len(self.claims) == 0:
            return []
        prompt = AlignmentTemplate.generate_alignment_verdicts(
            summary_claims=self.claims,
            original_text="\n\n".join(self.truths),
        )
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=AlignmentVerdicts,
            extract_schema=lambda s: list(s.verdicts),
            extract_json=lambda data: [AlignmentVerdict(**item) for item in data["verdicts"]],
        )

    def _generate_truths(self, text: str) -> list[str]:
        prompt = FaithfulnessTemplate.generate_truths(
            retrieval_context=text,
            extraction_limit=self.truths_extraction_limit,
        )
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Truths,
            extract_schema=lambda s: s.truths,
            extract_json=lambda data: data["truths"],
        )

    def _generate_claims(self, text: str) -> list[str]:
        prompt = FaithfulnessTemplate.generate_claims(actual_output=text)
        return generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Claims,
            extract_schema=lambda s: s.claims,
            extract_json=lambda data: data["claims"],
        )

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
                self.truths: list[str] = self._generate_truths(test_case.input)
                self.claims: list[str] = self._generate_claims(test_case.actual_output)  # ty: ignore
                self.verdicts: list[AlignmentVerdict] = self._generate_verdicts()
                self.score = self._calculate_score()
                self.reason = self._generate_reason()
                self.success = self.score >= self.threshold
                self.verbose_logs = construct_verbose_logs(
                    self,
                    steps=[
                        f"Truths (limit={self.truths_extraction_limit}):\n{prettify_list(self.truths)}",
                        f"Claims:\n{prettify_list(self.claims)}",
                        f"Alignment Verdicts:\n{prettify_list(self.verdicts)}",
                        f"Score: {self.score}\nReason: {self.reason}",
                    ],
                )
        return self.score  # ty: ignore

    async def _a_generate_reason(self) -> str | None:
        if not self.include_reason:
            return None
        contradictions = [v.reason for v in self.verdicts if v.verdict.strip().lower() == "no"]
        redundancies = [v.reason for v in self.verdicts if v.verdict.strip().lower() == "idk"]
        prompt = AlignmentTemplate.generate_reason(
            contradictions=contradictions,
            redundancies=redundancies,
            score=format(self.score, ".2f"),
        )
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=AlignmentScoreReason,
            extract_schema=lambda s: s.reason,
            extract_json=lambda data: data["reason"],
        )

    async def _a_generate_verdicts(self) -> list[AlignmentVerdict]:
        if len(self.claims) == 0:
            return []
        prompt = AlignmentTemplate.generate_alignment_verdicts(
            summary_claims=self.claims,
            original_text="\n\n".join(self.truths),
        )
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=AlignmentVerdicts,
            extract_schema=lambda s: list(s.verdicts),
            extract_json=lambda data: [AlignmentVerdict(**item) for item in data["verdicts"]],
        )

    async def _a_generate_truths(self, text: str) -> list[str]:
        prompt = FaithfulnessTemplate.generate_truths(
            retrieval_context=text,
            extraction_limit=self.truths_extraction_limit,
        )
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Truths,
            extract_schema=lambda s: s.truths,
            extract_json=lambda data: data["truths"],
        )

    async def _a_generate_claims(self, text: str) -> list[str]:
        prompt = FaithfulnessTemplate.generate_claims(actual_output=text)
        return await a_generate_with_schema_and_extract(
            metric=self,
            prompt=prompt,
            schema_cls=Claims,
            extract_schema=lambda s: s.claims,
            extract_json=lambda data: data["claims"],
        )

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
            self.truths, self.claims = await asyncio.gather(
                self._a_generate_truths(test_case.input),
                self._a_generate_claims(test_case.actual_output),  # ty: ignore
            )
            self.verdicts = await self._a_generate_verdicts()
            self.score = self._calculate_score()
            self.reason = await self._a_generate_reason()
            self.success = self.score >= self.threshold
            self.verbose_logs = construct_verbose_logs(
                self,
                steps=[
                    f"Truths (limit={self.truths_extraction_limit}):\n{prettify_list(self.truths)}",
                    f"Claims:\n{prettify_list(self.claims)}",
                    f"Alignment Verdicts:\n{prettify_list(self.verdicts)}",
                    f"Score: {self.score}\nReason: {self.reason}",
                ],
            )
        return self.score

    def is_successful(self) -> bool:
        if self.error is not None:
            self.success = False
        else:
            try:
                self.success = self.score >= self.threshold  # ty: ignore
            except TypeError:
                self.success = False
        return self.success

    @property
    def __name__(self):
        return "Alignment"
