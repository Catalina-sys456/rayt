import subprocess
from enum import Enum


class ServiceStatus(Enum):
    active = 1
    inactive = 2
    failed = 3
    unknow = 4


class Systemd:
    @classmethod
    def service_status(cls, service_name: str) -> ServiceStatus:
        try:
            output = (
                subprocess.check_output(
                    ["systemctl", "show", "-p", "ActiveState", service_name],
                    stderr=subprocess.STDOUT,
                )
                .decode()
                .strip()
            )
            match output:
                case "ActiveState=active":
                    return ServiceStatus.active
                case "ActiveState=inactive":
                    return ServiceStatus.inactive
                case "ActiveState=failed":
                    return ServiceStatus.failed
                case _:
                    return ServiceStatus.unknow
        except subprocess.CalledProcessError as e:
            print(f"Error checking service status: {e.output.strip()}")
            return ServiceStatus.unknow
        except Exception as e:
            print(e)
            return ServiceStatus.unknow

    @classmethod
    def __action(cls, action: str, service_name: str):
        try:
            subprocess.run(
                ["systemctl", action, service_name],
                check=True,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error {action} {service_name} service: {e.stderr.strip()}")
        except FileNotFoundError:
            print("Error: systemctl command not found. Is this a systemd Linux system?")
        except Exception as e:
            print(f"Unexpected error: {e}")

    @classmethod
    def start(cls, service_name: str):
        cls.__action("start", service_name)

    @classmethod
    def stop(cls, service_name: str):
        cls.__action("stop", service_name)

    @classmethod
    def restart(cls, service_name: str):
        cls.__action("restart", service_name)

    @classmethod
    def enable(cls, service_name: str):
        cls.__action("enable", service_name)

    @classmethod
    def disable(cls, service_name: str):
        cls.__action("disable", service_name)
