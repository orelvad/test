import json
import os
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('config_generator')

class ConfigGenerator:
    """
    Generates JSON configuration files for test steps based on parsed NLP information.
    Creates configuration with parameters for equipment settings and measurements.
    """
    
    def __init__(self, template_dir=None):
        """
        Initialize the configuration generator.
        
        Args:
            template_dir (str, optional): Directory containing config templates
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / 'templates' / 'config'
        
        self.template_dir = Path(template_dir)
        
        # Create template directory if it doesn't exist
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)
            self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default JSON template files for configurations"""
        # Base config template
        base_config = {
            "step_info": {
                "description": "Template description",
                "timestamp": "",
                "primary_action": ""
            },
            "equipment": {
                "type": "",
                "connection": {
                    "interface": "GPIB",
                    "address": "GPIB0::22::INSTR"
                }
            },
            "parameters": {},
            "register_operations": [],
            "verification": {
                "enabled": False,
                "tolerances": {}
            }
        }
        
        base_config_path = self.template_dir / 'base_config.json'
        with open(base_config_path, 'w') as f:
            json.dump(base_config, f, indent=4)
        
        # Keysight specific config
        keysight_config = {
            "step_info": {
                "description": "Keysight equipment operation",
                "timestamp": "",
                "primary_action": ""
            },
            "equipment": {
                "type": "keysight",
                "model": "",
                "connection": {
                    "interface": "GPIB",
                    "address": "GPIB0::22::INSTR",
                    "timeout_ms": 5000
                }
            },
            "parameters": {
                "voltage": {
                    "value": 0.0,
                    "unit": "V",
                    "range": "AUTO"
                },
                "current": {
                    "value": 0.0,
                    "unit": "A",
                    "range": "AUTO"
                },
                "frequency": {
                    "value": 0.0,
                    "unit": "Hz"
                }
            },
            "register_operations": [],
            "verification": {
                "enabled": False,
                "tolerances": {
                    "voltage": 0.05,
                    "current": 0.05,
                    "frequency": 0.01
                }
            }
        }
        
        keysight_config_path = self.template_dir / 'keysight_config.json'
        with open(keysight_config_path, 'w') as f:
            json.dump(keysight_config, f, indent=4)
        
        # Register operations config
        register_config = {
            "step_info": {
                "description": "Register operations",
                "timestamp": "",
                "primary_action": ""
            },
            "register_operations": [
                {
                    "address": "0x0000",
                    "operation": "read",
                    "expected_value": 0,
                    "mask": "0xFFFF"
                }
            ],
            "timing": {
                "delay_before_ms": 0,
                "delay_after_ms": 0,
                "timeout_ms": 1000
            },
            "verification": {
                "enabled": False,
                "retry_count": 3,
                "retry_delay_ms": 100
            }
        }
        
        register_config_path = self.template_dir / 'register_config.json'
        with open(register_config_path, 'w') as f:
            json.dump(register_config, f, indent=4)
        
        logger.info("Created default config templates")
    
    def _load_template(self, template_name):
        """
        Load a JSON template file.
        
        Args:
            template_name (str): Name of the template file
            
        Returns:
            dict: The template as a dictionary
        """
        template_path = self.template_dir / template_name
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Template file {template_name} not found, using empty dict")
            return {}
    
    def select_template(self, parsed_step):
        """
        Select the appropriate template based on parsed step information.
        
        Args:
            parsed_step (dict): The parsed test step information
            
        Returns:
            dict: The selected template as a dictionary
        """
        # Choose template based on equipment and actions
        if "keysight" in parsed_step["equipment"]:
            return self._load_template("keysight_config.json")
        elif parsed_step["addresses"] and (len(parsed_step["equipment"]) == 0 or 
                                         parsed_step["primary_action"] in ["get", "set"]):
            return self._load_template("register_config.json")
        else:
            return self._load_template("base_config.json")
    
    def generate(self, parsed_step):
        """
        Generate JSON configuration for a test step.
        
        Args:
            parsed_step (dict): The parsed test step information
            
        Returns:
            dict: Generated configuration as a dictionary
        """
        # Get the base template
        config = self.select_template(parsed_step)
        
        # Fill in step information
        config["step_info"] = {
            "description": parsed_step["original_text"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "primary_action": parsed_step["primary_action"]
        }
        
        # Fill in equipment information if available
        if parsed_step["equipment"]:
            config["equipment"]["type"] = parsed_step["equipment"][0] if parsed_step["equipment"] else ""
        
        # Fill in parameters
        if "parameters" not in config:
            config["parameters"] = {}
            
        for param, value in parsed_step["parameters"].items():
            if param not in config["parameters"]:
                config["parameters"][param] = {}
                
            if value is not None:
                if isinstance(config["parameters"][param], dict):
                    config["parameters"][param]["value"] = value
                else:
                    config["parameters"][param] = {"value": value}
        
        # Fill in register operations
        if "register_operations" not in config:
            config["register_operations"] = []
            
        for i, addr in enumerate(parsed_step["addresses"]):
            operation = {
                "address": addr,
                "operation": "write" if "set" in parsed_step["actions"] else "read"
            }
            
            if "set" in parsed_step["actions"]:
                operation["value"] = parsed_step["parameters"].get("value", 0)
                
            if "verify" in parsed_step["actions"]:
                operation["expected_value"] = parsed_step["parameters"].get("value", 0)
                config["verification"]["enabled"] = True
                
            config["register_operations"].append(operation)
        
        # Enable verification if 'verify' is in actions
        if "verification" in config and "verify" in parsed_step["actions"]:
            config["verification"]["enabled"] = True
        
        logger.info(f"Generated config for step: '{parsed_step['original_text'][:50]}...' if len(parsed_step['original_text']) > 50 else parsed_step['original_text']")
        
        return config
