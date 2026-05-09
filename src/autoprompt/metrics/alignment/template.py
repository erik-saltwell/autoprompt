multimodal_rules = """
    --- MULTIMODAL INPUT RULES ---
    - Treat image content as factual evidence.
    - Only reference visual details that are explicitly and clearly visible.
    - Do not infer or guess objects, text, or details not visibly present.
    - If an image is unclear or ambiguous, mark uncertainty explicitly.
"""


class AlignmentTemplate:
    @staticmethod
    def generate_reason(contradictions, redundancies, score):
        return f"""You will be given: 1) information in the summary contradicting the original text, and 2) extra information in the summary not mentioned in the original text. Your task is to explain the alignment score.
Given the alignment score, which is a 0-1 score indicating how well the summary's claims align with the original text (higher the better), CONCISELY summarize the provided information to justify the score.

{multimodal_rules}

**
IMPORTANT: Please make sure to only return in JSON format, with the 'reason' key providing the reason.
Example JSON:
{{
    "reason": "The score is <alignment_score> because <your_reason>."
}}

For 'None' values in contradictions or extra information, DON'T mention anything and instead offer some praise.
Be sure in your reason, as if you know what the summary and original text is.
**

Alignment Score:
{score}

Contradicting Information in the original text:
{contradictions}

Extra Information not mentioned in the original text:
{redundancies}

JSON:
"""

    @staticmethod
    def generate_alignment_verdicts(original_text, summary_claims):
        return f"""Based on the given summary claims, which is a list of strings, generate a list of JSON objects to indicate whether EACH piece of info contradicts any facts in the original text. The JSON will have 2 fields: 'verdict' and 'reason'.

{multimodal_rules}

The 'verdict' key should STRICTLY be either 'yes', 'no', or 'idk', which states whether the given summary claim agrees with the original text.
Provide a 'reason' ONLY if the answer is 'no' OR 'idk'.
The provided summary claims is drawn from the summary. Try to provide a correction in the reason using the facts in the original text.

**
IMPORTANT: Please make sure to only return in JSON format, with the 'verdicts' key as a list of JSON objects.
Example Original Text: "Einstein won the Nobel Prize for his discovery of the photoelectric effect. Einstein won the Nobel Prize in 1968. Einstein is a German Scientist."
Example Summary Claims: ["Barack Obama is a caucasian male.", "Zurich is a city in London", "Einstein won the Nobel Prize for the discovery of the photoelectric effect which may have contributed to his fame.", "Einstein won the Nobel Prize in 1969 for his discovery of the photoelectric effect.", "Einstein was a German chef."]

Example:
{{
    "verdicts": [
        {{
            "verdict": "idk",
            "reason": "The original text does not mention Barack Obama at all, let alone his racial features."
        }},
        {{
            "verdict": "idk",
            "reason": "The original text does not mention Zurich, nor does it mention Zurich being in London."
        }},
        {{
            "verdict": "yes"
        }},
        {{
            "verdict": "no",
            "reason": "The summary claims Einstein won the Nobel Prize in 1969, which is untrue as the original text states it is 1968 instead."
        }},
        {{
            "verdict": "no",
            "reason": "The summary claims Einstein is a German chef, which is not correct as the original text states he was a German scientist instead."
        }}
    ]
}}
===== END OF EXAMPLE ======

The length of 'verdicts' SHOULD BE STRICTLY EQUAL to that of summary claims.
You DON'T have to provide a reason if the answer is 'yes'.
ONLY provide a 'no' answer if the summary DIRECTLY CONTRADICTS the claims. YOU SHOULD NEVER USE YOUR PRIOR KNOWLEDGE IN YOUR JUDGEMENT.
Claims made using vague, suggestive, speculative language such as 'may have', 'possibility due to', does NOT count as a contradiction.
Claims that is not backed up due to a lack of information/is not mentioned in the summary MUST be answered 'idk', otherwise I WILL DIE.
**

Original Text:
{original_text}

Summary Claims:
{summary_claims}

JSON:
"""
