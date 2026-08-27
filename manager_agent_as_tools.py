from agents import Agent, RunResult
from planner_agent import planner_agent, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from email_agent import MODEL_NAME, email_agent
import os
from dotenv import load_dotenv

load_dotenv(override=True)
MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini")

async def extract_search_plan(run_result: RunResult) -> str:
    """
    planner_agent normally returns a structured WebSearchPlan object. When it's used
    as a tool, we want the manager agent to receive plain, readable text instead of a
    Python object repr - so it can clearly see each search term and reason, and know
    to call web_search once per line.
    """
    plan: WebSearchPlan = run_result.final_output
    lines = [f"{i + 1}. {item.query} (reason: {item.reason})" for i, item in enumerate(plan.searches)]
    return "\n".join(lines)


async def extract_report(run_result: RunResult) -> str:
    """
    writer_agent normally returns a ReportData object (summary + report + follow-ups).
    We only want the manager agent to see the markdown report itself, so it passes the
    exact report text to the email tool rather than a paraphrased or garbled version.
    """
    report: ReportData = run_result.final_output
    return report.markdown_report


plan_searches_tool = planner_agent.as_tool(
    tool_name="plan_searches",
    tool_description=(
        "Given a research query (and optional clarifications), returns a numbered "
        "list of web search terms to run, each with a reason."
    ),
    custom_output_extractor=extract_search_plan,
)

web_search_tool = search_agent.as_tool(
    tool_name="web_search",
    tool_description="Given a single search term, searches the web and returns a concise summary of the results.",
)

write_report_tool = writer_agent.as_tool(
    tool_name="write_report",
    tool_description=(
        "Given the original query and a collection of search result summaries, "
        "writes a comprehensive markdown report. Returns only the report's markdown text."
    ),
    custom_output_extractor=extract_report,
)

send_report_email_tool = email_agent.as_tool(
    tool_name="send_report_email",
    tool_description="Sends the given markdown report out via email.",
)


INSTRUCTIONS = """
You are a research manager. Orchestrate a full research pipeline using your tools, in this exact order:

1. Call `plan_searches` with the user's query (and clarifications, if provided).
2. Call `web_search` once for EACH search term returned by `plan_searches` - one call
   per term, using the exact query text. Do not skip any term.
3. Once you have every search summary, call `write_report` with the original query and
   all the summaries gathered.
4. Call `send_report_email` with the markdown report `write_report` gave you.
5. Your final reply to the user must be the exact, full markdown report text from
   `write_report` - do not summarize, shorten, or rewrite it.

If the user gives clarifications alongside their query, pass them along to
`plan_searches` so the searches are properly scoped.
"""

manager_agent_as_tools = Agent(
    name="Manager Agent (Tools)",
    instructions=INSTRUCTIONS,
    tools=[plan_searches_tool, web_search_tool, write_report_tool, send_report_email_tool],
    model=MODEL_NAME,
)