from pathlib import Path
import subprocess


def ensure_file_exists(file_path: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def get_public_ip() -> str:
    urls = [
        "https://ifconfig.me",
        "https://api.ipify.org",
        "https://ident.me",
        "https://ipinfo.io/ip",
    ]
    errors = []
    for url in urls:
        try:
            output = (
                subprocess.check_output(["curl", "-s", url], stderr=subprocess.STDOUT)
                .decode()
                .strip()
            )
            return output
        except Exception as e:
            errors.append(str(e))
    raise RuntimeError(f'Error: {"; ".join(errors)}')
