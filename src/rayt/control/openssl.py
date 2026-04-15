import subprocess
from rayt.control.utils import ensure_file_exists


def openssl_base64_password(num_bytes: int) -> str:
    """
    Generate a random Base64 string from the specified number of bytes using OpenSSL.

    Args:
        num_bytes: The number of random bytes to generate. The resulting Base64 string
                  will be longer (approximately 4/3 * num_bytes characters).

    Returns:
        A Base64 encoded string, or None if an error occurs.
    """
    if not isinstance(num_bytes, int) or num_bytes <= 0:
        raise ValueError("Error: num_bytes must be a positive integer")

    try:
        output = (
            subprocess.check_output(
                ["openssl", "rand", "-base64", str(num_bytes)], stderr=subprocess.STDOUT
            )
            .decode()
            .strip()
        )
        return output
    except Exception as e:
        raise RuntimeError(f"Error: {e}")


def openssl_generate_cert(cert_path: str, key_path: str):
    ensure_file_exists(cert_path)
    ensure_file_exists(key_path)

    try:
        subprocess.run(
            [
                "bash",
                "-c",
                f"openssl req -x509 -nodes -newkey ec:<(openssl ecparam -name prime256v1) -keyout {key_path} -out {cert_path} -subj '/CN=MyOrg Root CA/C=AT/ST=Vienna/L=Vienna/O=MyOrg' -days 36500",
            ]
        )
    except Exception as e:
        raise RuntimeError(f"Error: {e}")
