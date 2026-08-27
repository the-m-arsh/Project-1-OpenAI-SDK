import gradio as gr
from dotenv import load_dotenv
from agents import Runner
from manager_agent_handoffs import manager_agent_handoffs

load_dotenv(override=True)


async def run(query: str, clarifications: str):
    input_message = f"Query: {query}"
    if clarifications and clarifications.strip():
        input_message += f"\n\nClarifications:\n{clarifications.strip()}"
    result = await Runner.run(manager_agent_handoffs, input_message)
    return result.final_output


with gr.Blocks() as ui:
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    clarifications_textbox = gr.Textbox(label="Any clarifications? (optional)", lines=3)
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    run_button.click(run, inputs=[query_textbox, clarifications_textbox], outputs=report)

ui.launch(theme=gr.themes.Default(primary_hue="sky"))