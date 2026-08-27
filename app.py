import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
from styles import CSS, JS, EXAMPLES, HEADER_HTML

load_dotenv(override=True)

manager = ResearchManager()

#Step 1: Ask the clarifier agent for 3 questions about the query
async def get_questions(query: str):
    if not query or not query.strip():
        return ( [],
        gr.update(visible=False, value="", label="Answer 1"),
        gr.update(visible=False, value="", label="Answer 2"),
        gr.update(visible=False, value="", label="Answer 3"),
        gr.update(visible=False),
    )

    results = await manager.get_clarifying_questions(query)
    questions = list(results.questions) [:3]
    while len(questions) < 3:
        questions.append("")
    return (
        questions,
        gr.update(visible=True, value=questions[0], label="Answer 1"),
        gr.update(visible=True, value=questions[1], label="Answer 2"),
        gr.update(visible=True, value=questions[2], label="Answer 3"),
        gr.update(visible=True),
    )

#Step 2: Run the research pipeline, folding the Q&A into the search planning. 
async def run(query: str, a1: str, a2: str, a3: str, questions: list[str]):
    clarifications = "\n\n".join(
        f"Q: {q}\nA: {a.strip()}"
        for q, a in zip(questions or [], [a1, a2, a3])
        if q and a and a.strip()
    ) or None

    async for status_update in manager.run(query, clarifications):
        yield status_update

with gr.Blocks(title="Deep Research") as ui:
    gr.HTML(HEADER_HTML)

    questions_state = gr.State([])

    with gr.Row(elem_classes="dr-query-row"):
        query_textbox = gr.Textbox(
            placeholder="Type a research question...",
            show_label=False,
            container=False,
            autofocus=True,
            elem_id="dr-query",
            scale=5,
        )
        
        clarify_button = gr.Button("Clarify", variant="secondary", elem_id="dr-clarify", scale=1)

    gr.HTML('<div class="dr-examples-label">Try one</div>')
    gr.Examples(examples=EXAMPLES, inputs=query_textbox, elem_id="dr-examples")

    gr.HTML('<div class="dr-examples-label">A few quick questions (optional)</div>')
    a1_box, a2_box, a3_box = [
        gr.Textbox(visible=False, placeholder="Your answer (optional)") for _ in range(3)
    ]
    run_button = gr.Button("Investigate", variant="primary", elem_id="dr-run", visible=False)

    report = gr.Markdown(elem_id="dr-report")

    gr.on(triggers=[clarify_button.click, query_textbox.submit], fn=get_questions,
        inputs=query_textbox,
        outputs=[questions_state, a1_box, a2_box, a3_box, run_button],
    )

    run_button.click(run, inputs=[query_textbox, a1_box, a2_box, a3_box, questions_state], outputs=report)

if __name__ == "__main__":
    ui.launch(css=CSS, js=JS, theme=gr.themes.Base())

