import logging
import gradio as gr

from manifest.schemas import ManifestState
from manifest.entities import Pipelines, Agents, PipelineAgents
from manifest.pipelines.brainstorm_pipeline import BrainstormPipeline
from manifest.pipelines.plan_pipeline import PlanPipeline


LOGGER = logging.getLogger(__name__)


class ManifestUI:
    """Gradio interface for the WebAppDeveloper system."""

    def __init__(self):
        """Initialize UI."""
        self.pipelines = {
            Pipelines.BRAINSTORM: BrainstormPipeline(),
            Pipelines.PLAN: PlanPipeline(),
            Pipelines.IMPLEMENT: None,
            Pipelines.REFINEMENT: None,
        }

        self.state = ManifestState()

        self.current_mode = Pipelines.BRAINSTORM

    def reset_current(self, mode: str) -> tuple[str, list[dict[str, str]]]:
        """Reset current session."""

        try:
            status_message: str = ""

            self.state.conversations[mode] = []
            status_message += f"✅ Successfully reset {mode} conversations.\n\n  "

            for agent in PipelineAgents[mode]:
                self.state.documents[agent] = []
                status_message += f"✅ Successfully reset {mode} document [Agent: {agent}].\n\n  "

                self.state.messages[agent] = []
                status_message += f"✅ Successfully reset {mode} messages [Agent: {agent}].\n\n  "

        except Exception as e:
            LOGGER.error(f"Reset error: {e}")
            status_message =  f"❌ Error resetting `{mode}`: {e}"


        return status_message, self.state.conversations[mode]

    def reset_all(self):

        status_msg = ""

        for mode in self.pipelines.keys():
            status_msg += self.reset_current(mode)[0]

        return status_msg, self.state.conversations[self.current_mode]

    def chat(self, message: str) -> tuple[str, list[dict[str, str]]]:

        if not self.state.conversations.get(self.current_mode):
            self.state.conversations[self.current_mode] = []

        if not message.strip():
            return "❌ Message is empty!", self.state.conversations[self.current_mode]

        self.state.conversations[self.current_mode].append({"role": "user", "content": message})

        if not self.pipelines[self.current_mode]:
            self.state.conversations[self.current_mode].append({
                "role": "assistant",
                "content": f"❌ {self.current_mode} mode is not implemented yet."
            })
            return "❌ Pipeline not implemented!", self.state.conversations[self.current_mode]

        try:
            response = self.pipelines[self.current_mode].invoke(message, self.state)
            status_msg: str = "Success!"
        except Exception as e:
            LOGGER.error(f"Error processing message: {e}")
            status_msg = f"Error processing message: {e}"
            response = f"❌ Error: {str(e)}"

        self.state.conversations[self.current_mode].append({"role": "assistant", "content": response})
        return status_msg, self.state.conversations[self.current_mode]

    def switch_mode(self, mode: str) -> tuple[str, list[dict[str, str]]]:
        """Switch agent mode."""

        if not self.state.conversations.get(mode):
            self.state.conversations[mode] = []

        if not self.pipelines.get(mode):
            msg: str = f"⚠️ {mode} mode is not implemented yet"
            LOGGER.warning(msg)

        self.current_mode = mode

        msg = f"✅ Switched to {mode} mode"
        LOGGER.info(msg)
        return msg, self.state.conversations[self.current_mode]

    def create_interface(self) -> gr.Blocks:
        """Create Gradio UI."""
        with gr.Blocks(title="Manifest", theme=gr.themes.Soft()) as interface:
            with gr.Row():
                with gr.Column(min_width=100):
                    gr.Markdown("# 🚀 Manifest Assistant")
                    gr.Markdown("Multi-mode AI assistant for web application development")

                    # Status Message
                    status_message = gr.Markdown("")

                    # Reset Buttons
                    with gr.Row():
                        reset_mode_btn = gr.Button(f"Reset Current Mode")
                        reset_all_btn = gr.Button(f"Reset All")

                    # Tabs
                    with gr.Tabs():
                        with gr.Tab(label=Pipelines.BRAINSTORM) as brainstorm_tab:
                            pass

                        with gr.Tab(label=Pipelines.PLAN) as plan_tab:
                            pass

                        with gr.Tab(label=Pipelines.IMPLEMENT) as implementation_tab:
                            pass

                        with gr.Tab(label=Pipelines.REFINEMENT) as refinement_tab:
                            pass

                    msg_input = gr.Textbox(
                        label="Your Input",
                        placeholder="Describe your idea...",
                        lines=10,
                    )

                    send_btn = gr.Button("Send")

                # Chatbot
                with gr.Column():
                    chatbot = gr.Chatbot(
                        value=self.state.conversations.get(self.current_mode) or [],
                        label="Conversation",
                        type="messages",
                        height=700,
                        min_width=1300,
                        show_label=False
                    )

            def reset_mode_fn() -> tuple[str, list[dict[str, str]]]:
                return self.reset_current(self.current_mode)

            def reset_all_fn() -> tuple[str, list[dict[str, str]]]:
                return self.reset_all()

            reset_mode_btn.click(
                reset_mode_fn,
                [],
                outputs=[status_message, chatbot],
            )

            reset_all_btn.click(
                reset_all_fn,
                [],
                outputs=[status_message, chatbot],
            )

            def brainstorm_selected_fn() -> tuple[str, list[dict[str, str]]]:
                return self.switch_mode(Pipelines.BRAINSTORM)
            def plan_selected_fn() -> tuple[str, list[dict[str, str]]]:
                return self.switch_mode(Pipelines.PLAN)
            def implement_selected_fn() -> tuple[str, list[dict[str, str]]]:
                return self.switch_mode(Pipelines.IMPLEMENT)
            def refinement_selected_fn() -> tuple[str, list[dict[str, str]]]:
                return self.switch_mode(Pipelines.REFINEMENT)

            brainstorm_tab.select(fn=brainstorm_selected_fn, outputs=[status_message, chatbot])
            plan_tab.select(fn=plan_selected_fn, outputs=[status_message, chatbot])
            implementation_tab.select(fn=implement_selected_fn, outputs=[status_message, chatbot])
            refinement_tab.select(fn=refinement_selected_fn, outputs=[status_message, chatbot])

            def chat(user_message: str) -> tuple[str, list[dict[str, str]]]:
                status_msg, history = self.chat(user_message)
                return status_msg, history

            # Send message
            send_btn.click(
                chat,
                inputs=[msg_input],
                outputs=[status_message, chatbot],
            )

        return interface

    def launch(self, **kwargs):
        """Launch the UI."""
        interface = self.create_interface()
        interface.launch(**kwargs)
