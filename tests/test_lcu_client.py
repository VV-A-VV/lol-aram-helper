import unittest
from unittest.mock import patch

from aram_helper.lcu_client import LcuClient, extract_lcu_credentials


class LcuClientTest(unittest.TestCase):
    def test_extracts_port_and_token(self):
        command_line = (
            '"LeagueClientUx.exe" --app-port=51521 '
            "--remoting-auth-token=abc-123_XY"
        )

        credentials = extract_lcu_credentials(command_line)

        self.assertIsNotNone(credentials)
        self.assertEqual(credentials.port, "51521")
        self.assertEqual(credentials.token, "abc-123_XY")

    def test_returns_none_when_missing_token(self):
        self.assertIsNone(extract_lcu_credentials("--app-port=51521"))

    def test_gameflow_session_uses_gameflow_endpoint(self):
        client = LcuClient()

        with patch.object(client, "request", return_value={"phase": "InProgress"}) as request:
            session = client.gameflow_session()

        self.assertEqual(session, {"phase": "InProgress"})
        request.assert_called_once_with("/lol-gameflow/v1/session")


if __name__ == "__main__":
    unittest.main()
