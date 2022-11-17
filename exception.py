#正雨 @ 1695960757
class ClientNotExists(Exception):
    guid = ""

    def __init__(self, guid):
        self.guid = guid


class MediaNotExistsError(Exception):
    pass
