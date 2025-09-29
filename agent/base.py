from typing import Dict, Optional

from omegaconf import DictConfig


class Agent:
    DEFAULT_TAG = 'Agent-default'

    def __init__(self,
                 config_dir_or_id: Optional[str] = None,
                 config: Optional[DictConfig] = None,
                 env: Optional[Dict[str, str]] = None,
                 trust_remote_code: bool = False):
        
        if config_dir_or_id is not None:
            self.config: DictConfig