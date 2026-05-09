multimodal_rules = """
    --- MULTIMODAL INPUT RULES ---
    - Treat image content as factual evidence.
    - Only reference visual details that are explicitly and clearly visible.
    - Do not infer or guess objects, text, or details not visibly present.
    - If an image is unclear or ambiguous, mark uncertainty explicitly.
"""


class CoverageTemplate:
    @staticmethod
    def generate_reason(questions, score):
        return f"""You will be given a list of questions that the original text can answer but the summary cannot. Your task is to explain the coverage score.
Given the coverage score, which is a 0-1 score indicating how well the summary covers the key information in the original text (higher the better), CONCISELY summarize the provided information to justify the score.

{multimodal_rules}

**
IMPORTANT: Please make sure to only return in JSON format, with the 'reason' key providing the reason.
Example JSON:
{{
    "reason": "The score is <coverage_score> because <your_reason>."
}}

If there are no uncovered questions, DON'T mention anything and instead offer some praise.
Be sure in your reason, as if you know what the summary and original text is.
**

Coverage Score:
{score}

Questions the original text can answer but not the summary:
{questions}

JSON:
"""

    @staticmethod
    def generate_answers(questions, text):
        return f"""Based on the list of close-ended 'yes' or 'no' questions, generate a JSON with key 'answers', which is a list of strings that determines whether the provided text contains sufficient information to answer EACH question.

{multimodal_rules}

Answers should STRICTLY be either 'yes' or 'no'.
Answer 'no' if the provided text does not contain enough information to answer the question.
**
IMPORTANT: Please make sure to only return in JSON format, with the 'answers' key as a list of strings.

Example:
Example Text: Mario and Luigi were best buds but since Luigi had a crush on Peach Mario ended up killing him.
Example Questions: ["Are there enough information about Luigi and Mario?"]
Example Answers:
{{
    "answers": ["yes"]
}}

The length of 'answers' SHOULD BE STRICTLY EQUAL to that of questions.
===== END OF EXAMPLE ======

Text:
{text}

Questions:
{questions}

JSON:
"""

    @staticmethod
    def generate_questions(text, n):
        return f"""Based on the given text, generate {n} closed-ended questions that can be answered with either a 'yes' or 'no'.
The questions generated should ALWAYS result in a 'yes' based on the given text.

{multimodal_rules}

** IMPORTANT
Only return a JSON with a 'questions' key, which is a list of strings.
The questions have to be STRICTLY closed ended.
The given text should be able to answer 'yes' for each question.
**
Text:
{text}

JSON:
"""
