from abc import ABC, abstractmethod
import shutil
from typing import Self

from rayt.control.service import ServiceStatus, Systemd


class CoreControl(ABC):
    service_name: str
    package_name: str

    @classmethod
    def service_status(cls) -> ServiceStatus:
        status = Systemd.service_status(cls.service_name)
        return status

    @classmethod
    def start_service(cls):
        Systemd.start(cls.service_name)

    @classmethod
    def stop_service(cls):
        Systemd.stop(cls.service_name)

    @classmethod
    def restart_service(cls):
        Systemd.restart(cls.service_name)

    @classmethod
    def enable_service(cls):
        Systemd.enable(cls.service_name)

    @classmethod
    def disable_service(cls):
        Systemd.disable(cls.service_name)

    @classmethod
    @abstractmethod
    def install(cls) -> bool:
        pass

    @classmethod
    @abstractmethod
    def uninstall(cls) -> bool:
        pass

    @classmethod
    @abstractmethod
    def update(cls) -> bool:
        pass

    @classmethod
    def installed_or_not(cls) -> bool:
        result = shutil.which(cls.package_name)
        if result == None:
            return False
        else:
            return True

    @classmethod
    def ensure_intalled(cls) -> bool:
        installed = cls.installed_or_not()
        if not installed:
            if cls.install():
                return True
            else:
                return False
        else:
            return True


class CoreProtocolControl(CoreControl):
    @abstractmethod
    def write_config(self) -> Self:
        pass

    @abstractmethod
    def get_share_link(self) -> str:
        pass
