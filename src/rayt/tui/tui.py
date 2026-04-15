from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Button, Footer, Header, Label, Select, SelectionList
from rayt.control import Hysrteria2AcmeControl, Hysteria2TlsControl, ServiceStatus
from rayt.control.control import CoreControl
from rayt.control import Hysteria2Control, JuicityControl
from rayt.control.juicity import Juicity, JuicityControl
from rayt.tui.widgets import CoreStatusLabel, InputModal, ShowQrcode


class Rayt(App):

    CSS = """
    Screen {
        align: center middle;
        padding: 1 2;
    }

    Vertical {
        width: 80%;
        margin: 1 0;
    }

    Label {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    SelectionList {
        padding: 1;
        border: solid $accent;
        width: 80%;
        height: auto;
        margin-bottom: 2;
    }

    Select {
        width: 100%;
        margin-bottom: 1;
    }

    Button {
        width: 80%;
        height: 3;
        margin-top: 1;
        background: $accent;
        color: $text;
    }

    CoreStatusLabel {
        width: 80%;
        margin-bottom: 1;
        padding: 1;
    }

    Notification {
        background: $panel;
        border: solid $accent;
    }
    """

    core_list = ["hysteria2", "juicity"]
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode", show=True),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

        hysteria2 = """hysteria2-acme
hysteria2-tls
    """.splitlines()
        juicity = "juicity".splitlines()
        yield CoreStatusLabel(Hysteria2Control)
        yield CoreStatusLabel(JuicityControl)
        with Vertical():
            yield Label("Hysteria2")
            yield Select.from_values(hysteria2)
            yield Label("Juicity")
            yield Select.from_values(juicity)

        core_options = [
            ("Hysteria2", "hysteria2", Hysteria2Control.installed_or_not()),
            ("Juicity", "juicity", JuicityControl.installed_or_not()),
        ]
        yield SelectionList(*core_options, id="core-list")
        yield Button("Confirm install cores", id="btn-cores")

    def str_to_core_class(self, core_srt: str) -> None | CoreControl:
        match core_srt:
            case "hysteria2":
                core_class = Hysteria2Control()
                return core_class
            case "juicity":
                core_class = JuicityControl()
                return core_class

    def install_or_not(self, core_str: str) -> bool:
        core_class = self.str_to_core_class(core_str)
        if core_class is not None:
            return core_class.installed_or_not()
        else:
            return False

    def install(self, install_class: CoreControl) -> bool:
        self.notify(f"Installing {install_class.package_name}")
        if install_class.install():
            self.notify(f"Install {install_class.package_name} complete")
            return True
        else:
            self.notify(
                f"Install {install_class.package_name} failed", severity="error"
            )
            return False

    def restart_service(self, start_class: CoreControl) -> bool:
        self.notify(f"Starting {start_class.service_name}")
        start_class.restart_service()
        if start_class.service_status() == ServiceStatus.failed:
            self.notify(f"{start_class.service_name} failed", severity="error")
            return False
        else:
            return True

    def ensure_installed(self, ensure_class: CoreControl) -> bool:
        if ensure_class.installed_or_not():
            return True
        else:
            return self.install(ensure_class)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "btn-cores":
                self.handle_btn_cores()

    def on_mount(self) -> None:
        self.query_one("#core-list", SelectionList).border_title = (
            "Select core to install"
        )

    def handle_btn_cores(self):
        selected_item = self.query_one(SelectionList).selected
        self.notify(str(selected_item))

        for i in selected_item:
            core_class = self.str_to_core_class(str(i))
            if core_class is not None:
                self.ensure_installed(core_class)

    def handle_hysteria2_acme(self):
        hysteria2 = Hysrteria2AcmeControl()

        def handle_result(result: str | None):
            if result is not None:
                hysteria2.set_domain(result).write_config()
                try:
                    self.ensure_installed(hysteria2)
                    self.restart_service(hysteria2)
                    hysteria2.enable_service()
                    self.push_screen(ShowQrcode(hysteria2.get_share_link()))
                except Exception as e:
                    print(f"Error: {e}")

        self.push_screen(InputModal("Domain name"), handle_result)

    def handle_hysteria2_tls(self):
        hysteria2 = Hysteria2TlsControl()
        hysteria2.write_config()
        try:
            self.ensure_installed(hysteria2)
            self.restart_service(hysteria2)
            hysteria2.enable_service()
            self.push_screen(ShowQrcode(hysteria2.get_share_link()))
        except Exception as e:
            print(f"Error: {e}")

    def handle_juicity(self):
        juicity = Juicity()
        juicity.write_config()
        try:
            self.ensure_installed(juicity)
            self.restart_service(juicity)
            juicity.enable_service()
            self.push_screen(ShowQrcode(juicity.get_share_link()))
        except Exception as e:
            print(f"Error: {e}")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        match event.value:
            case "hysteria2-acme":
                self.handle_hysteria2_acme()

            case "hysteria2-tls":
                self.handle_hysteria2_tls()

            case "juicity":
                self.handle_juicity()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
