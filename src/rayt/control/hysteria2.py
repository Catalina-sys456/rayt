from typing import Self
from rayt.control.control import CoreControl, CoreProtocolControl
from rayt.control.utils import ensure_file_exists, get_public_ip
from .openssl import openssl_base64_password, openssl_generate_cert
from .service import *
import subprocess
import yaml


class Hysteria2Control(CoreControl):
    service_name = "hysteria-server"
    package_name = "hysteria"
    listen: str
    config_path: str
    password: str
    url: str

    def __init__(self) -> None:
        super().__init__()
        self.listen = ":443"
        self.config_path = "/etc/hysteria/config.yaml"
        self.password = openssl_base64_password(16)
        self.url = "https://skydrive.live.com/"

    @classmethod
    def install(cls) -> bool:
        result = subprocess.run(
            ["bash", "-c", "bash <(curl -fsSL https://get.hy2.sh/)"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    @classmethod
    def uninstall(cls) -> bool:
        result = subprocess.run(
            ["bash", "-c", "bash <(curl -fsSL https://get.hy2.sh/) --remove"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    @classmethod
    def update(cls) -> bool:
        result = cls.install()
        return result


class Hysrteria2AcmeControl(Hysteria2Control, CoreProtocolControl):
    domain: str
    email: str

    def __init__(self) -> None:
        super().__init__()
        self.domain = ""
        self.email = "your@email.com"

    # default domain name is '', must set
    def set_domain(self, domain: str) -> Self:
        self.domain = domain
        return self

    def write_config(self) -> Self:
        config = {
            "listen": self.listen,
            "acme": {
                "domains": [self.domain],
                "email": self.email,
            },
            "auth": {
                "type": "password",
                "password": self.password,
            },
            "masquerade": {
                "type": "proxy",
                "proxy": {
                    "url": self.url,
                    "rewriteHost": True,
                },
            },
        }
        ensure_file_exists(self.config_path)
        yaml_str = yaml.dump(config, allow_unicode=True)
        with open(f"{self.config_path}", "w") as f:
            f.write(yaml_str)
        return self

    def get_share_link(self) -> str:
        link = f"hysteria2://{self.password}@{self.domain}:{self.listen}?security=&insecure=0"
        return link


class Hysteria2TlsControl(Hysteria2Control, CoreProtocolControl):
    cert_path: str
    key_path: str

    def __init__(self) -> None:
        super().__init__()
        self.cert_path = "/etc/hysteria/server.crt"
        self.key_path = "/etc/hysteria/server.key"

    def write_config(self) -> Self:
        openssl_generate_cert(key_path=self.key_path, cert_path=self.cert_path)
        config = {
            "listen": self.listen,
            "tls": {
                "cert": self.cert_path,
                "key": self.key_path,
            },
            "auth": {
                "type": "password",
                "password": self.password,
            },
            "masquerade": {
                "type": "proxy",
                "proxy": {
                    "url": self.url,
                    "rewriteHost": True,
                },
            },
        }
        ensure_file_exists(self.config_path)
        yaml_str = yaml.dump(config, allow_unicode=True)
        with open(f"{self.config_path}", "w") as f:
            f.write(yaml_str)
        return self

    def get_share_link(self) -> str:
        ip = get_public_ip()
        url = f"hysteria2://{self.password}@{ip}:{self.listen}?security=tls&insecure=1"
        return url
