from io import StringIO
import qrcode
from textual.app import ComposeResult
from textual.widgets import Button, Label, TextArea
from textual.screen import ModalScreen
from textual import events


class ShowQrcode(ModalScreen[str]):

    CSS = """
    ShowQrcode {
        align: center middle;
    }
    
    ShowQrcode > Vertical {
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        min-width: 50%;
        min-height: 10;
    }
    
    ShowQrcode Label {
        text-align: center;
        margin-bottom: 1;
    }
    
    InputModal TextArea {
        margin: 1 0;
    }
    
    InputModal Button {
        margin: 1 2;
    }
    """

    def __init__(self, link: str):
        super().__init__()
        self.link = link

    def link_to_qrcode(self, link: str) -> str:
        qr = qrcode.QRCode()
        qr.add_data(link)
        f = StringIO()
        qr.print_ascii(out=f)
        return f.getvalue()

    def compose(self) -> ComposeResult:
        qrcode = self.link_to_qrcode(self.link)
        # yield TextArea(self.link, disabled=True, language='text')
        yield Label(self.link)
        yield TextArea(qrcode, disabled=True, language="text")
        yield Button("confirm", id="confirm_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_btn":
            self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key == "enter":
            self.dismiss(None)
