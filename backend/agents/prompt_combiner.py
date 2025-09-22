from pathlib import Path
import toml
from typing import Optional
from backend.utils.logging_config import get_module_logger

logger = get_module_logger('prompt_combiner')

class PromptCombiner:
    def __init__(self, general_prompts_dir: Path = None, stage_prompts_dir: Path = None):
        self.general_prompts_dir = general_prompts_dir or Path("backend/config/prompts/general")
        self.stage_prompts_dir = stage_prompts_dir or Path("backend/config/prompts/stages")
    
    def load_general_prompt(self, prompt_name: str, version: str = "latest") -> str:
        return self._load_prompt_from_toml(prompt_name, version, self.general_prompts_dir)
    
    def load_stage_prompt(self, prompt_name: str, version: str = "latest") -> str:
        return self._load_prompt_from_toml(prompt_name, version, self.stage_prompts_dir)
    
    def _load_prompt_from_toml(self, prompt_name: str, version: str, prompt_dir: Path) -> str:
        if not prompt_dir.is_dir():
            raise NotADirectoryError(f"Prompt directory not found: {prompt_dir}")
        
        toml_file_path = prompt_dir / f"{prompt_name}.toml"
        if not toml_file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {toml_file_path}")
        
        with open(toml_file_path, 'r') as file:
            toml_content = toml.load(file)
        
        if version == "latest":
            versions = [key for key in toml_content.keys() if key.startswith('v')]
            if not versions:
                raise ValueError(f"No versioned content found in {toml_file_path}")
            version_key = max(versions, key=lambda v: int(v[1:]))
        else:
            version_key = f"v{version}" if not version.startswith('v') else version
            if version_key not in toml_content:
                raise ValueError(f"Version {version_key} not found in {toml_file_path}")
        
        return toml_content[version_key]
    
    def combine_prompts(self, situation_tone: str, stage_prompt: str, response_style: str) -> str:
        combined = f"{situation_tone.strip()}\n\n{stage_prompt.strip()}\n\n{response_style.strip()}"
        
        logger.debug(f"Combined prompt created: {len(combined)} characters")
        
        return combined
    
    def get_combined_prompt(self, stage_prompt_name: str, 
                          situation_version: str = "latest", 
                          response_version: str = "latest") -> str:
        try:
            situation_tone = self.load_general_prompt("situation_and_tone", situation_version)
            stage_prompt = self.load_stage_prompt(stage_prompt_name, "latest")
            response_style = self.load_general_prompt("response_style", response_version)
            
            combined = self.combine_prompts(situation_tone, stage_prompt, response_style)
            
            logger.info(f"Successfully combined prompts for stage: {stage_prompt_name}")
            return combined
            
        except Exception as e:
            logger.error(f"Failed to combine prompts for {stage_prompt_name}: {str(e)}")
            raise