from modules.minimum_important_functions import *

logger = get_logger(__name__)


class Translator:
    def __init__(self, lang="en", translations: dict = {}):
        if not translations:

            translations = {
                "open url": {"ru": "открываю ссылку", "en": "opening url"},
                "close url": {"ru": "закрываю ссылку"},
            }
        self.translations = translations
        self.lang = lang

    def translate(self, message="", lang=None):
        if not lang:
            lang = self.lang

        translations = self.translations.get(message, {})
        # logger.debug(f"{lang=} {translations=} for {message=}")
        value = translations.get(lang, message)
        return value


if __name__ == "__main__":
    kwargs = {
        "lang": "en",
        "lang": "ru",
    }
    translator = Translator(**kwargs)
    messages = clear_list(
        """
    open url
    close url
    nah
    """
    )
    for message in messages:
        translated = translator.translate(message)
        logger.info(f"{translated=} for {message=}")
