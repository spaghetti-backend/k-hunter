from keyhunter.settings.commands import SettingChangeCommand
from keyhunter.settings.schemas import AppSettings
from keyhunter.settings.storage import SettingsStorage


class SettingsService:
    def __init__(self, settings: AppSettings) -> None:
        self._history: list[SettingChangeCommand] = []
        self._storage = SettingsStorage()
        self._settings = settings

        user_settings = self._storage.load()
        self._settings.load(user_settings)

    def update(self, command: SettingChangeCommand):
        command.execute(self._settings)
        self._history.append(command)
        self.save()

    def reset_to_default(self) -> None:
        self._settings.load({})

    def save(self) -> None:
        self._storage.save(self._settings.dump())
