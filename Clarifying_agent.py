from pydantic import BaseModel, Field
from agents import Agent
import os
from dotenv import load_dotenv
load_dotenv(override=True)

MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini")

INSTRUCTIONS = """
You are an expert research scoping assistant. Before conducting research, your job is to identify the most important unknowns in the user's query.

Given the user's research query, generate exactly 3 high-value clarifying questions. The questions should help establish:

1. Scope: What should be included or excluded, including relevant time period, geography, industry, market, or population?
2. Intent: What is the user trying to accomplish with the research, and how will the findings be used?
3. Focus: What specific angle, comparison, criteria, methodology, or level of depth matters most?

Rules:

- Ask exactly 3 questions.
- Prioritize questions whose answers would meaningfully change the research plan.
- Do not ask for information the user has already provided.
- Avoid generic, redundant, or low-value questions.
- Keep each question short (one sentence), specific, and easy to answer.
- If one category is already clear from the query, use that question to clarify another important dimension instead.
- Return only the 3 questions—no preamble, explanations, or answers.
"""

class ClarifyingQuestions(BaseModel):
    questions: list[str] = Field(
        description = "Exactly 3 clarifying questions about the research query."
    )

clarifier_agent = Agent(
    name = "Clarifying Agent",
    instructions = INSTRUCTIONS,
    model = MODEL_NAME,
    output_type = ClarifyingQuestions
)