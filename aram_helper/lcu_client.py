import base64
import json
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

import psutil


@dataclass(frozen=True)
class LcuCredentials:
    port: str
    token: str


def extract_lcu_credentials(command_line: str) -> LcuCredentials | None:
    port = re.search(r"--app-port=(\d+)", command_line)
    token = re.search(r"--remoting-auth-token=([\w-]+)", command_line)
    if not port or not token:
        return None
    return LcuCredentials(port=port.group(1), token=token.group(1))


class LcuClient:
    def __init__(self):
        self.credentials: LcuCredentials | None = None

    def connect(self) -> bool:
        for proc in psutil.process_iter(["name", "cmdline"]):
            name = proc.info.get("name") or ""
            if "LeagueClientUx" not in name:
                continue

            cmdline = " ".join(proc.info.get("cmdline") or ())
            credentials = extract_lcu_credentials(cmdline)
            if credentials:
                self.credentials = credentials
                return True

        self.credentials = None
        return False

    def request(self, endpoint: str, timeout: float = 2.0):
        if not self.credentials:
            return None

        auth = base64.b64encode(f"riot:{self.credentials.token}".encode()).decode()
        url = f"https://127.0.0.1:{self.credentials.port}{endpoint}"
        request = urllib.request.Request(url, headers={"Authorization": f"Basic {auth}"})
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(request, context=context, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

    def gameflow_phase(self) -> str | None:
        result = self.request("/lol-gameflow/v1/gameflow-phase")
        return result if isinstance(result, str) else None

    def champ_select_session(self) -> dict | None:
        result = self.request("/lol-champ-select/v1/session")
        return result if isinstance(result, dict) else None

    def gameflow_session(self) -> dict | None:
        result = self.request("/lol-gameflow/v1/session")
        return result if isinstance(result, dict) else None
