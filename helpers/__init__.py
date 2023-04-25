from pathlib import Path
import os


class Paths:
    def __init__(self, full_path: str):
        self.full_path = full_path  # this is property

    def __str__(self) -> str:
        return str(self.full_path)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, value):
        self._dir = Path(value)

    @property
    def full_path(self):
        return self._dir / self._filename

    @full_path.setter
    def full_path(self, value):
        parts = Path(value).parts
        if len(parts) > 1:
            self._dir = Path(os.path.join(*parts[:-1]))
        else:
            self._dir = Path('')
        self._filename = Path(parts[-1])


PathSplit = Path
