# coding=utf-8
from pathlib import Path
from typing import Optional, Union

import yaml


class ConfUtil:

    def __init__(self, conf_path: Union[Path, str], log_path: Union[Path, str]) -> None:
        if isinstance(conf_path, Path):
            self.__conf: Optional[dict] = yaml.safe_load(self.__load_file(conf_path))
        elif isinstance(conf_path, str):
            self.__conf: Optional[dict] = yaml.safe_load(conf_path)
        if isinstance(log_path, Path):
            self.__log_conf: Optional[dict] = yaml.safe_load(self.__load_file(log_path))
        elif isinstance(log_path, str):
            self.__log_conf: Optional[dict] = yaml.safe_load(log_path)

    def __load_file(self, path: Path) -> str:
        with open(str(path.absolute()), 'r', encoding='utf-8') as f:
            return f.read()

    @property
    def conf(self) -> Optional[dict]:
        return self.__conf

    @property
    def log_conf(self) -> Optional[dict]:
        return self.__log_conf
