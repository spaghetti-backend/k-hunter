from enum import Enum
from typing import Any

from textual.dom import DOMNode
from textual.reactive import reactive

from keyhunter import const as CONST
from keyhunter.content.schemas import ContentLanguage, ContentType
from keyhunter.typer.schemas import TyperEngine


class TyperBorder(str, Enum):
    BLANK = "blank"
    ROUND = "round"
    SOLID = "solid"
    THICK = "thick"
    DOUBLE = "double"
    HEAVY = "heavy"
    HKEY = "hkey"
    TALL = "tall"
    WIDE = "wide"


SettingsDict = dict[str, Any]


class BaseSettings(DOMNode):
    def __init__(self):
        super().__init__()
        for base in self.__class__.__bases__:
            self.__annotations__.update(base.__annotations__)

    def dump(self) -> SettingsDict:
        settings = {}
        for setting_name in self.__annotations__:
            setting = getattr(self, setting_name)
            if isinstance(setting, BaseSettings):
                settings[setting_name] = setting.dump()
            else:
                settings[setting_name] = setting

        return settings

    def load(self, settings: SettingsDict, r: bool = True) -> None:
        for setting_name in self.__annotations__:
            setting = getattr(self, setting_name)
            if isinstance(setting, BaseSettings):
                setting.load(settings.get(setting_name, {}))
            else:
                setting_type = type(setting)
                reactive_setting = self._reactives[setting_name]
                setting_default = reactive_setting._default
                value = setting_type(settings.get(setting_name, setting_default))
                if r:
                    self.set_reactive(reactive_setting, value)
                else:
                    setattr(self, setting_name, value)


class SizeConstraints(BaseSettings):
    width: reactive[int] = reactive(CONST.SLE_WIDTH, init=False)
    height: reactive[int] = reactive(CONST.SLE_HEIGHT, init=False)

    min_width = CONST.SLE_MIN_WIDTH
    max_width = CONST.SLE_MAX_WIDTH

    min_height = CONST.SLE_MIN_HEIGHT
    max_height = CONST.SLE_MAX_HEIGHT


class SingleLineEngineSettings(SizeConstraints):
    start_from_center: reactive[bool] = reactive(
        CONST.SLE_START_FROM_CENTER, init=False
    )


class StandardEngineSettings(SizeConstraints):
    min_height = CONST.SE_MIN_HEIGHT
    max_height = CONST.SE_MAX_HEIGHT


class TyperSettings(BaseSettings):
    engine: reactive[TyperEngine] = reactive(TyperEngine.SINGLE_LINE, init=False)
    border: reactive[TyperBorder] = reactive(TyperBorder.HKEY, init=False)
    single_line_engine: SingleLineEngineSettings = SingleLineEngineSettings()
    standard_engine: StandardEngineSettings = StandardEngineSettings()


class ContentSettings(BaseSettings):
    language: reactive[ContentLanguage] = reactive(ContentLanguage.EN, init=False)
    content_type: reactive[ContentType] = reactive(ContentType.COMMON, init=False)
    content_lenght: reactive[int] = reactive(CONST.CONTENT_LENGHT, init=False)
    min_content_lenght = CONST.CONTENT_MIN_LENGHT
    max_content_lenght = CONST.CONTENT_MAX_LENGHT


class AppSettings(BaseSettings):
    theme: reactive[str] = reactive(CONST.THEME, init=False)
    typer: TyperSettings = TyperSettings()
    content: ContentSettings = ContentSettings()
