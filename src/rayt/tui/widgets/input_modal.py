from textual.app import ComposeResult
from textual.widgets import Button, Input
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual import events


class InputModal(ModalScreen[str]):

    CSS = """
    InputModal {
        align: center middle;
    }
    
    InputModal > Vertical {
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        min-width: 50%;
        min-height: 10;
    }
    
    InputModal Label {
        text-align: center;
        margin-bottom: 1;
    }
    
    InputModal Input {
        margin: 1 0;
    }
    
    InputModal Button {
        margin: 1 2;
    }
    """

    def __init__(self, title: str = "Input here ..."):
        super().__init__()
        self.title_text = title

    def compose(self) -> ComposeResult:
        yield Input(placeholder=self.title_text, id="user_input")
        with Horizontal():
            yield Button("cancel", id="cancel_btn")
            yield Button("confirm", id="confirm_btn", variant="primary")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.dismiss(None)
        elif event.button.id == "confirm_btn":
            input_value = self.query_one(Input).value
            self.dismiss(input_value)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            input_value = self.query_one(Input).value
            self.dismiss(input_value)
