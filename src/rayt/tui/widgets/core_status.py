from textual.widgets import Label
from textual.app import ComposeResult
from textual.binding import Binding
from rayt.control import CoreControl, ServiceStatus
from typing import Type, TypeVar

T = TypeVar("T", bound=CoreControl)


class CoreStatusLabel(Label, can_focus=True):

    DEFAULT_CSS = """
    CoreStatusLabel {
        width: auto;
        height: auto;
        min-height: 1;
        color: $text-accent;
        text-style: underline;
        &:hover { color: $accent; }
        &:focus { text-style: bold reverse; }
        pointer: pointer;
    }
    """

    BINDINGS = [
        Binding("s", "start_service", "Start service"),
        Binding("p", "stop_service", "Stop service"),
        Binding("r", "restart_service", "Restart service"),
    ]

    def __init__(self, core_cls: Type[T]):
        super().__init__()
        self.core = core_cls

    def compose(self) -> ComposeResult:
        yield Label(
            f"● {self.core.service_name} service status", id=self.core.service_name
        )

    def on_mount(self) -> None:
        self.set_interval(1, self.update_status)

    def update_status(self):
        status: ServiceStatus = self.core.service_status()
        status_light = self.query_one(f"#{self.core.service_name}", Label)
        match status:
            case ServiceStatus.active:
                status_light.styles.color = "green"
                status_light.update(
                    f"● {self.core.service_name} service active    ● Stop service"
                )
            case ServiceStatus.inactive:
                status_light.styles.color = "blue"
                status_light.update(
                    f"● {self.core.service_name} service inactive    ● Start service"
                )
            case ServiceStatus.failed:
                status_light.styles.color = "red"
                status_light.update(
                    f"● {self.core.service_name} service failed    ● Start service"
                )
            case ServiceStatus.unknow:
                status_light.styles.color = "yellow"
                status_light.update(f"● {self.core.service_name} service status unknow")

    def on_click(self) -> None:
        self.action_execute_callback()

    def action_execute_callback(self) -> None:
        """Execute the callback function if it exists."""
        status = self.core.service_status()
        if status == ServiceStatus.active:
            self.core.stop_service()
        elif status == ServiceStatus.inactive or status == ServiceStatus.failed:
            self.core.start_service()

    def action_start_service(self):
        self.core.start_service()

    def action_stop_service(self):
        self.core.stop_service()

    def action_restart_service(self):
        self.core.start_service()
