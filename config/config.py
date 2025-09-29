
import os
from typing import Dict, Union
from omegaconf import DictConfig, ListConfig


class ConfigLifecycleHandler:

    def task_begin(self, config: DictConfig, tag: str) -> DictConfig:

        """Modify the config at the beginning of a task.
        
        Args:
            config(`DictConfig`): The config instance.
            tag(`str`): The agent tag.
        """
        return config


class Config:
    """All task begin from a config"""

    tag: str = ''
    supported_config_names = [
        'agent.yaml'
    ]

    @classmethod
    def from_task(cls,
                  config_dir_or_id,
                  env: Dict[str, str] = None) -> Union[DictConfig, ListConfig]:
        if not os.path.exists(config_dir_or_id):
            config_dir_or_id = snap