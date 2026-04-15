from typing import Self
from rayt.control.control import CoreControl, CoreProtocolControl
import subprocess
from uuid import uuid4
import json

from rayt.control.openssl import openssl_base64_password, openssl_generate_cert
from rayt.control.utils import ensure_file_exists


class JuicityControl(CoreControl):
    service_name = "juicity-server"
    package_name = "juicity-server"

    def __init__(self) -> None:
        super().__init__()
        self.config_path = "/usr/local/etc/juicity/server.json"

    @classmethod
    def install(cls) -> bool:
        result = subprocess.run(
            [
                "bash",
                "-c",
                "bash <(curl -sL https://github.com/juicity/juicity-installer/raw/master/installer.sh)",
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    @classmethod
    def uninstall(cls) -> bool:
        result = subprocess.run(
            [
                "bash",
                "-c",
                "bash <(curl -sL https://github.com/juicity/juicity-installer/raw/master/uninstaller.sh)",
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    @classmethod
    def update(cls) -> bool:
        return cls.install()


class Juicity(JuicityControl, CoreProtocolControl):
    listen: str
    uuid: str
    password: str
    cert_path: str
    key_path: str
    congestion_control: str
    disable_outbound_udp443: bool
    log_level: str

    def __init__(self) -> None:
        super().__init__()
        self.listen = ":443"
        self.uuid = str(uuid4())
        self.password = openssl_base64_password(16)
        self.cert_path = "/usr/local/etc/juicity/server.crt"
        self.key_path = "/usr/local/etc/juicity/server.key"
        self.congestion_control = "bbr"
        self.disable_outbound_udp443 = True
        self.log_level = "info"

    def write_config(self) -> Self:
        config = {
            "listen": self.listen,
            "users": {self.uuid: self.password},
            "certificate": self.cert_path,
            "private_key": self.key_path,
            "congestion_control": self.congestion_control,
            "disable_outbound_udp443": self.disable_outbound_udp443,
            "log_level": self.log_level,
        }
        openssl_generate_cert(cert_path=self.cert_path, key_path=self.key_path)
        json_str = json.dumps(config, indent=4)
        ensure_file_exists(self.config_path)
        with open(self.config_path, "w") as f:
            f.write(json_str)
        return self

    def get_share_link(self) -> str:
        try:
            output = (
                subprocess.check_output(
                    ["juicity-server", "generate-sharelink", "-c", self.config_path],
                    stderr=subprocess.STDOUT,
                )
                .decode()
                .strip()
            )
            return output
        except Exception as e:
            raise RuntimeError(f"Error: failed to generate juicity share link: {e}")
