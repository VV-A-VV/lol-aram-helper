import unittest

from aram_helper.app_state import AppStateService
from aram_helper.models import GamePhase


class FakeLcu:
    def __init__(self, connected, phase, session=None, gameflow_session=None):
        self.connected = connected
        self.phase = phase
        self.session = session
        self.gameflow = gameflow_session

    def connect(self):
        return self.connected

    def gameflow_phase(self):
        return self.phase

    def champ_select_session(self):
        return self.session

    def gameflow_session(self):
        return self.gameflow


class AppStateServiceTest(unittest.TestCase):
    def test_disconnected_snapshot(self):
        service = AppStateService(FakeLcu(False, None))

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.DISCONNECTED)
        self.assertEqual(snapshot.status, "状态: 未检测到客户端")

    def test_champ_select_snapshot(self):
        session = {
            "localPlayerCellId": 3,
            "actions": [[{"actorCellId": 3, "championId": 876}]],
            "benchChampions": [{"championId": 904}, {"championId": 63}],
        }
        service = AppStateService(FakeLcu(True, "ChampSelect", session))

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.CHAMP_SELECT)
        self.assertEqual(snapshot.selected_champion_id, "876")
        self.assertEqual(snapshot.champion_ids, ("876", "904", "63"))

    def test_in_game_keeps_locked_champion(self):
        service = AppStateService(FakeLcu(True, "InProgress"))
        service.locked_champion_id = "876"

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.IN_PROGRESS)
        self.assertEqual(snapshot.champion_ids, ("876",))

    def test_in_game_recovers_champion_from_gameflow_session(self):
        session = {
            "gameData": {
                "playerChampionSelections": [
                    {"championId": 157, "puuid": "local-player"},
                ]
            }
        }
        service = AppStateService(FakeLcu(True, "InProgress", gameflow_session=session))

        snapshot = service.poll()

        self.assertEqual(snapshot.phase, GamePhase.IN_PROGRESS)
        self.assertEqual(snapshot.selected_champion_id, "157")
        self.assertEqual(snapshot.champion_ids, ("157",))


if __name__ == "__main__":
    unittest.main()
