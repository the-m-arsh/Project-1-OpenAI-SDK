from typing import Any


from agents import Agent, WebSearchTool, ModelSettings
from email_agent import send_email_tool
import os
from dotenv import load_dotenv

load_dotenv(override=True)
MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini")
HOW_MANY_SEARCHES = int(os.getenv("HOW_MANY_SEARCHES", 5))

# --- Entry point: Manager Agent ---
MANAGER_INSTRUCTIONS = """
You are the entry point of a research pipeline. You will receive a research query, and
possibly clarifications. Immediately hand off to the Planner Agent so the pipeline can
begin - do not do any research or planning yourself.
"""

manager_agent_handoffs = Agent(
    name = "Manager Agent (Handoff)",
    instructions = MANAGER_INSTRUCTIONS,
    model = MODEL_NAME,
)

# ---  Stage 1: Planner Agent ---
PLANNER_INSTRUCTIONS = """
You are a research assistant. You will receive a research query, and possibly
clarifications the user gave in response to earlier clarifying questions.

Come up with {HOW_MANY_SEARCHES} web searches that would best answer the query. If
clarifications were provided, use them to sharpen your choice of searches (scope, time
period, geography, angle, etc).

List the searches as a numbered list, each with a one-line reason. Then hand off to the
Search Agent so it can perform them.
"""

handoff_planner_agent = Agent(
    name = "Planner Agent (Handoff)",
    instructions = PLANNER_INSTRUCTIONS,
    model = MODEL_NAME,
)

manager_agent_handoffs.handoffs = [handoff_planner_agent]

# --- Stage 2: Search Agent ---
SEARCH_INSTRUCTIONS = """
You are a research assistant. You will receive a numbered list of search terms (with
reasons) earlier in the conversation.

For EVERY term in the list, use your web search tool to search the web, and write a
concise 2-3 paragraph summary (under 300 words) for that term. Do this separately for
each term - do not skip any.

Once you have summaries for all the search terms, hand off to the Writer Agent,
including the original query and all your summaries in the message you hand off with.
"""

handoff_search_agent = Agent(
    name = "Search Agent (Handoff)",
    instructions = SEARCH_INSTRUCTIONS,
    tools = [WebSearchTool()],
    model = MODEL_NAME,
    model_settings = ModelSettings(tool_choice="required"),
    )

handoff_planner_agent.handoffs = [handoff_search_agent]

# --- Stage 3: Writer Agent ---
WRITER_INSTRUCTIONS = """
You are a senior researcher. You will receive the original query and a set of web
search summaries earlier in the conversation.

Write a comprehensive markdown report based on them. Aim for at least 1000 words of content.

Once your report is written, hand off to the Email Agent so it can be sent. Include
your full report in the message you hand off with.
"""

handoff_writer_agent = Agent(
    name = "Writer Agent (Handoff)",
    instructions = WRITER_INSTRUCTIONS,
    model = MODEL_NAME, 
)

handoff_search_agent.handoffs = [handoff_writer_agent]

# --- Stage 4: Email Agent ---
EMAIL_INSTRUCTIONS = """
You are the final stage of a research pipeline. You will receive a complete markdown
research report earlier in the conversation.

1. Use your tool to send that report as a well-presented HTML email, with an
   appropriate subject line.
2. Your final reply to the user must be the FULL markdown report, unchanged, followed
   by a short line confirming the email was sent. Do not summarize or shorten the report.
"""

handoff_email_agent = Agent(
    name = "Email Agent (Handoff)",
    instructions = EMAIL_INSTRUCTIONS,
    tools = [send_email_tool],
    model = MODEL_NAME,
    model_settings = ModelSettings(tool_choice="required"),
)

handoff_writer_agent.handoffs = [handoff_email_agent]