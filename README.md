# Deep Research Agent
 
A multi-agent deep research assistant built with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). Give it a research query, optionally answer a few clarifying questions, and it will plan web searches, run them, write a full markdown report, and email it to you.
 
The project implements the same research pipeline **three different ways**, as a comparison of agentic orchestration patterns:
 
1. **Class-based manager** — plain Python orchestrates calls to each agent.
2. **Agents-as-tools** — a single "manager" agent orchestrates by calling the other agents as tools.
3. **Handoffs** — control passes fully from one agent to the next in a relay chain.
## How it works
 
Every version runs the same four-stage pipeline:
 
1. **Plan** — the Planner Agent turns the query (plus any clarifications) into a set of web search terms.
2. **Search** — the Search Agent runs each search term and summarizes the results.
3. **Write** — the Writer Agent turns all the summaries into a full markdown report.
4. **Send** — the Email Agent emails (or pushes) the finished report.
There's also a **Clarifying Agent** that, given the original query, generates 3 clarifying questions up front (used by the main Gradio app, `app.py`).
 
## Project structure
 
| File | Purpose |
|---|---|
| `app.py` | Main Gradio UI: asks 3 clarifying questions, then runs the class-based research pipeline. |
| `simple.py` | Minimal Gradio UI for the class-based pipeline, no clarifying questions. |
| `simple_tools.py` | Minimal Gradio UI for the **agents-as-tools** pipeline. |
| `simple_handoffs.py` | Minimal Gradio UI for the **handoffs** pipeline. |
| `research_manager.py` | `ResearchManager` class — the class-based orchestrator used by `app.py` and `simple.py`. |
| `manager_agent_tools.py` | Manager agent built with the agents-as-tools pattern, used by `simple_tools.py`. |
| `manager_agent_handoffs.py` | Chain of agents wired together with handoffs, used by `simple_handoffs.py`. |
| `Clarifying_agent.py` | Generates 3 clarifying questions about a research query. |
| `planner_agent.py` | Turns a query into a set of web search terms. |
| `search_agent.py` | Runs a single web search and summarizes it. |
| `writer_agent.py` | Writes the final markdown report from search summaries. |
| `email_agent.py` | Sends the finished report by email (or push notification). |
| `messenger.py` | Low-level email (SMTP) and push notification (Pushover) helpers. |
| `styles.py` | CSS/JS/HTML for the styled `app.py` UI. |
| `requirements.txt` | Python dependencies. |
 
## Setup
 
**1. Clone the repo and create a virtual environment**
 
```bash
git clone <your-repo-url>
cd <your-repo-folder>
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
```
 
**2. Install dependencies**
 
```bash
pip install -r requirements.txt
```
 
**3. Create a `.env` file** in the project root with the following variables:
 
```bash
# Required
OPENAI_API_KEY=your-openai-api-key
 
# Optional - model & search tuning
DEFAULT_MODEL_NAME=gpt-5.4-mini
HOW_MANY_SEARCHES=5
 
# Email delivery (set USE_EMAIL=false to use Pushover instead)
USE_EMAIL=true
EMAIL_ADDRESS=you@example.com
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_APP_PASSWORD=your-email-app-password
 
# Push notifications (used when USE_EMAIL=false)
PUSHOVER_USER=your-pushover-user-key
PUSHOVER_TOKEN=your-pushover-app-token
```
 
> Note: for Gmail, `EMAIL_SMTP_SERVER` is `smtp.gmail.com` and `EMAIL_APP_PASSWORD` must be an [app password](https://support.google.com/accounts/answer/185833), not your regular account password.
 
## Running it
 
Each entry point is a standalone Gradio app.
 
**Full experience (clarifying questions + styled UI):**
```bash
python app.py
```
 
**Class-based pipeline, no clarifying questions:**
```bash
python simple.py
```
 
**Agents-as-tools pipeline:**
```bash
python simple_tools.py
```
 
**Handoffs pipeline:**
```bash
python simple_handoffs.py
```
 
Each will print a local URL (typically `http://127.0.0.1:7860`) to open in your browser.
 
## Tracing
 
Every run of the class-based pipeline (`research_manager.py`) prints a trace URL to the [OpenAI traces dashboard](https://platform.openai.com/traces), where you can inspect every agent call, tool call, and model response step by step.
 
## The three orchestration patterns, compared
 
| | Class-based (`research_manager.py`) | Agents-as-tools (`manager_agent_tools.py`) | Handoffs (`manager_agent_handoffs.py`) |
|---|---|---|---|
| Who decides the sequence? | Python code | The manager agent (LLM) | Each agent decides when it's done |
| Who holds control? | Python, throughout | The manager agent, throughout | Passed permanently, stage to stage |
| Searches run | In parallel (`asyncio.gather`) | Sequentially, one tool call per term | Sequentially, by one agent |
| Best for | Predictable, debuggable pipelines | Flexible orchestration with LLM judgment | Simple linear pipelines, minimal orchestration code |
 
