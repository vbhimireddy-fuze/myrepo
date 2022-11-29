# coding=utf-8
from pathlib import Path
from typing import Optional

import yaml


class ConfUtil:

    def __init__(self, conf_path: Path, log_path: Path) -> None:
        self.__conf: Optional[dict] = yaml.safe_load(self.__load_file(conf_path))
        self.__log_conf: Optional[dict] = yaml.safe_load(self.__load_file(log_path))

    def __load_file(self, path: Path) -> str:
        with open(str(path.absolute()), 'r', encoding='utf-8') as f:
            return f.read()

    @property
    def conf(self) -> Optional[dict]:
        return self.__conf

    @property
    def log_conf(self) -> Optional[dict]:
        return self.__log_conf
