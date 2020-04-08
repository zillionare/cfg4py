from typing import Optional


class Config(object):
    __access_counter__ = 0

    def __cfg4py_reset_access_counter__(self):
        self.__access_counter__ = 0

    def __getattribute__(self, name):
        """
        keep tracking if the config is accessed. If there's no access, then even the refresh interval is reached, we
        will not call the remote fetcher.

        Args:
            name:

        Returns:

        """
        obj = object.__getattribute__(self, name)
        if name.startswith("__") and name.endswith("__"):
            return obj

        if callable(obj):
            return obj

        self.__access_counter__ += 1
        return obj
