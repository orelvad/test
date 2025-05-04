import os
from pathlib import Path
import jinja2
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('code_generator')

class CodeGenerator:
    """
    Generates Python code for test steps based on parsed NLP information.
    Uses Jinja2 templates for generating code based on equipment type and actions.
    """
    
    def __init__(self, template_dir=None):
        """
        Initialize the code generator with templates.
        
        Args:
            template_dir (str, optional): Directory containing code templates
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / 'templates' / 'code'
        
        self.template_dir = Path(template_dir)
        
        # Create template directory if it doesn't exist
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True)
            self._create_default_templates()
        
        # Set up Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_custom_filters()
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters for code generation"""
        self.jinja_env.filters['camel_case'] = lambda s: ''.join(
            word.capitalize() if i > 0 else word.lower()
            for i, word in enumerate(s.split('_'))
        )
        
        self.jinja_env.filters['snake_case'] = lambda s: s.lower().replace(' ', '_')
    
    def _create_default_templates(self):
        """Create default templates for different equipment and actions"""
        # Base template for all test steps
        base_template = '''"""
{{ step.original_text }}
Generated on: {{ timestamp }}
"""

import time
from typing import Dict, Any, Optional, Union
from equipment import keysight
from register import register_ops

{% if 'initialize' in step.actions %}
def initialize_equipment():
    """Initialize the required equipment"""
    {% if 'keysight' in step.equipment %}
    # Initialize Keysight equipment
    equipment = keysight.initialize()
    return equipment
    {% else %}
    # Generic equipment initialization
    equipment = {}
    return equipment
    {% endif %}

{% endif %}
{% if 'set' in step.actions %}
def set_parameters(equipment, **params):
    """Set parameters on the equipment"""
    {% if 'voltage' in step.parameters and step.parameters.voltage is not none %}
    # Set voltage to {{ step.parameters.voltage }}
    keysight.set_voltage(equipment, {{ step.parameters.voltage }})
    {% endif %}
    {% if 'current' in step.parameters and step.parameters.current is not none %}
    # Set current to {{ step.parameters.current }}
    keysight.set_current(equipment, {{ step.parameters.current }})
    {% endif %}
    {% if 'frequency' in step.parameters and step.parameters.frequency is not none %}
    # Set frequency to {{ step.parameters.frequency }}
    keysight.set_frequency(equipment, {{ step.parameters.frequency }})
    {% endif %}
    {% if step.addresses %}
    # Write to registers
    {% for addr in step.addresses %}
    register_ops.write_register({{ addr }}, params.get("reg_value_{{ loop.index }}", 0))
    {% endfor %}
    {% endif %}
    return True

{% endif %}
{% if 'get' in step.actions %}
def get_measurements(equipment):
    """Get measurements from the equipment"""
    results = {}
    {% if 'voltage' in step.parameters %}
    # Measure voltage
    results["voltage"] = keysight.measure_voltage(equipment)
    {% endif %}
    {% if 'current' in step.parameters %}
    # Measure current
    results["current"] = keysight.measure_current(equipment)
    {% endif %}
    {% if 'resistance' in step.parameters %}
    # Measure resistance
    results["resistance"] = keysight.measure_resistance(equipment)
    {% endif %}
    {% if 'power' in step.parameters %}
    # Measure power
    results["power"] = keysight.measure_power(equipment)
    {% endif %}
    {% if 'frequency' in step.parameters %}
    # Measure frequency
    results["frequency"] = keysight.measure_frequency(equipment)
    {% endif %}
    {% if step.addresses %}
    # Read from registers
    {% for addr in step.addresses %}
    results["reg_{{ loop.index }}"] = register_ops.read_register({{ addr }})
    {% endfor %}
    {% endif %}
    return results

{% endif %}
{% if 'verify' in step.actions %}
def verify_conditions(measurements, expected_values):
    """Verify measurements against expected values"""
    results = {}
    for key, expected in expected_values.items():
        if key in measurements:
            actual = measurements[key]
            tolerance = expected.get("tolerance", 0.05)
            min_val = expected["value"] * (1 - tolerance)
            max_val = expected["value"] * (1 + tolerance)
            results[key] = {
                "expected": expected["value"],
                "actual": actual,
                "passed": min_val <= actual <= max_val
            }
    return results

{% endif %}
{% if 'wait' in step.actions %}
def wait_for_condition(equipment, timeout=10.0, interval=0.5):
    """Wait for a specific condition to be met"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        {% if 'voltage' in step.parameters or 'current' in step.parameters %}
        # Check conditions
        measurements = get_measurements(equipment)
        {% if 'voltage' in step.parameters and step.parameters.voltage is not none %}
        if abs(measurements["voltage"] - {{ step.parameters.voltage }}) <= 0.1:
            return True
        {% endif %}
        {% if 'current' in step.parameters and step.parameters.current is not none %}
        if abs(measurements["current"] - {{ step.parameters.current }}) <= 0.01:
            return True
        {% endif %}
        {% endif %}
        time.sleep(interval)
    return False

{% endif %}
def main():
    """Main function to execute the test step"""
    try:
        {% if 'initialize' in step.actions %}
        equipment = initialize_equipment()
        {% else %}
        # Assuming equipment is already initialized
        equipment = keysight.get_equipment()
        {% endif %}
        
        {% if 'set' in step.actions %}
        set_parameters(equipment, 
                      {% for param, value in step.parameters.items() %}
                      {% if value is not none %}
                      {{ param }}={{ value }},
                      {% endif %}
                      {% endfor %}
                      )
        {% endif %}
        
        {% if 'wait' in step.actions %}
        # Wait for system to stabilize
        wait_for_condition(equipment)
        {% endif %}
        
        {% if 'get' in step.actions %}
        # Measure parameters
        measurements = get_measurements(equipment)
        print("Measurements:", measurements)
        {% endif %}
        
        {% if 'verify' in step.actions %}
        # Verify expected values
        expected_values = {
            {% for param, value in step.parameters.items() %}
            {% if value is not none %}
            "{{ param }}": {"value": {{ value }}, "tolerance": 0.05},
            {% endif %}
            {% endfor %}
        }
        verification = verify_conditions(measurements, expected_values)
        print("Verification results:", verification)
        {% endif %}
        
        {% if 'disconnect' in step.actions or 'shutdown' in step.actions %}
        # Shutdown equipment
        keysight.shutdown(equipment)
        {% endif %}
        
        return True
    except Exception as e:
        print(f"Error executing test step: {e}")
        return False

if __name__ == "__main__":
    main()
'''
        
        # Create the base template
        base_template_path = self.template_dir / 'base_template.py.j2'
        with open(base_template_path, 'w') as f:
            f.write(base_template)
        
        # Create specialized templates for specific equipment
        keysight_template = '''"""
{{ step.original_text }}
Generated on: {{ timestamp }}
"""

import time
from typing import Dict, Any, Optional, Union
from equipment import keysight
from register import register_ops

def setup_keysight_equipment():
    """Set up Keysight equipment for testing"""
    equipment = keysight.initialize()
    return equipment

{% if 'set' in step.actions %}
def configure_keysight(equipment, **params):
    """Configure Keysight equipment with specified parameters"""
    {% if 'voltage' in step.parameters and step.parameters.voltage is not none %}
    # Set voltage to {{ step.parameters.voltage }}V
    keysight.set_voltage(equipment, {{ step.parameters.voltage }})
    {% endif %}
    {% if 'current' in step.parameters and step.parameters.current is not none %}
    # Set current to {{ step.parameters.current }}A
    keysight.set_current_limit(equipment, {{ step.parameters.current }})
    {% endif %}
    {% if 'frequency' in step.parameters and step.parameters.frequency is not none %}
    # Set frequency to {{ step.parameters.frequency }}Hz
    keysight.set_frequency(equipment, {{ step.parameters.frequency }})
    {% endif %}
    {% if step.addresses %}
    # Write to registers
    {% for addr in step.addresses %}
    register_ops.write_register({{ addr }}, params.get("reg_value_{{ loop.index }}", 0))
    {% endfor %}
    {% endif %}
    return True
{% endif %}

{% if 'get' in step.actions %}
def measure_with_keysight(equipment):
    """Perform measurements using Keysight equipment"""
    results = {}
    {% if 'voltage' in step.parameters %}
    # Measure voltage
    results["voltage"] = keysight.measure_voltage(equipment)
    {% endif %}
    {% if 'current' in step.parameters %}
    # Measure current
    results["current"] = keysight.measure_current(equipment)
    {% endif %}
    {% if 'power' in step.parameters %}
    # Calculate power
    voltage = keysight.measure_voltage(equipment)
    current = keysight.measure_current(equipment)
    results["power"] = voltage * current
    {% endif %}
    {% if step.addresses %}
    # Read from registers
    {% for addr in step.addresses %}
    results["reg_{{ loop.index }}"] = register_ops.read_register({{ addr }})
    {% endfor %}
    {% endif %}
    return results
{% endif %}

def main():
    """Main function to execute the Keysight test step"""
    try:
        # Set up Keysight equipment
        equipment = setup_keysight_equipment()
        
        {% if 'set' in step.actions %}
        # Configure the equipment
        configure_keysight(equipment, 
                          {% for param, value in step.parameters.items() %}
                          {% if value is not none %}
                          {{ param }}={{ value }},
                          {% endif %}
                          {% endfor %}
                          )
        {% endif %}
        
        {% if 'wait' in step.actions %}
        # Wait for system to stabilize
        time.sleep(2.0)
        {% endif %}
        
        {% if 'get' in step.actions %}
        # Take measurements
        measurements = measure_with_keysight(equipment)
        print("Measurements:", measurements)
        {% endif %}
        
        {% if 'verify' in step.actions %}
        # Verify measurements against expected values
        expected_values = {
            {% for param, value in step.parameters.items() %}
            {% if value is not none %}
            "{{ param }}": {"value": {{ value }}, "tolerance": 0.05},
            {% endif %}
            {% endfor %}
        }
        
        all_passed = True
        for key, expected in expected_values.items():
            if key in measurements:
                actual = measurements[key]
                tolerance = expected.get("tolerance", 0.05)
                min_val = expected["value"] * (1 - tolerance)
                max_val = expected["value"] * (1 + tolerance)
                passed = min_val <= actual <= max_val
                all_passed = all_passed and passed
                print(f"Verification - {key}: Expected {expected['value']}, Got {actual}, {'PASS' if passed else 'FAIL'}")
        
        if all_passed:
            print("All verifications PASSED")
        else:
            print("Some verifications FAILED")
        {% endif %}
        
        {% if 'disconnect' in step.actions or 'shutdown' in step.actions %}
        # Shutdown Keysight equipment
        keysight.shutdown(equipment)
        {% endif %}
        
        return True
    except Exception as e:
        print(f"Error executing Keysight test step: {e}")
        return False

if __name__ == "__main__":
    main()
'''
        
        keysight_template_path = self.template_dir / 'keysight_template.py.j2'
        with open(keysight_template_path, 'w') as f:
            f.write(keysight_template)
        
        # Create register operations template
        register_template = '''"""
{{ step.original_text }}
Generated on: {{ timestamp }}
"""

import time
from typing import Dict, Any, Optional, Union
from register import register_ops

def main():
    """Main function to execute register operations"""
    try:
        {% if 'get' in step.actions %}
        # Read from registers
        results = {}
        {% for addr in step.addresses %}
        # Read from register {{ addr }}
        value = register_ops.read_register({{ addr }})
        results["{{ addr }}"] = value
        print(f"Register {{ addr }} value: {value}")
        {% endfor %}
        {% endif %}
        
        {% if 'set' in step.actions %}
        # Write to registers
        {% for addr in step.addresses %}
        # Write to register {{ addr }}
        register_ops.write_register({{ addr }}, {{ step.parameters.get("value", 0) }})
        print(f"Wrote value {{ step.parameters.get('value', 0) }} to register {{ addr }}")
        {% endfor %}
        {% endif %}
        
        {% if 'verify' in step.actions %}
        # Verify register values
        {% for addr in step.addresses %}
        # Read and verify register {{ addr }}
        value = register_ops.read_register({{ addr }})
        expected = {{ step.parameters.get("value", 0) }}
        passed = value == expected
        print(f"Verification - Register {{ addr }}: Expected {expected}, Got {value}, {'PASS' if passed else 'FAIL'}")
        {% endfor %}
        {% endif %}
        
        return True
    except Exception as e:
        print(f"Error executing register operations: {e}")
        return False

if __name__ == "__main__":
    main()
'''
        
        register_template_path = self.template_dir / 'register_template.py.j2'
        with open(register_template_path, 'w') as f:
            f.write(register_template)
            
        logger.info("Created default code templates")
    
    def select_template(self, parsed_step):
        """
        Select the appropriate template based on parsed step information.
        
        Args:
            parsed_step (dict): The parsed test step information
            
        Returns:
            jinja2.Template: The selected template
        """
        # Choose template based on equipment and actions
        if "keysight" in parsed_step["equipment"]:
            template_name = "keysight_template.py.j2"
        elif parsed_step["addresses"] and (len(parsed_step["equipment"]) == 0 or 
                                         parsed_step["primary_action"] in ["get", "set"]):
            template_name = "register_template.py.j2"
        else:
            template_name = "base_template.py.j2"
            
        return self.jinja_env.get_template(template_name)
    
    def generate(self, parsed_step):
        """
        Generate Python code for a test step.
        
        Args:
            parsed_step (dict): The parsed test step information
            
        Returns:
            str: Generated Python code
        """
        template = self.select_template(parsed_step)
        
        # Create context for template rendering
        context = {
            "step": parsed_step,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render the template with the provided context
        code = template.render(**context)
        
        logger.info(f"Generated code for step: '{parsed_step['original_text'][:50]}...' if len(parsed_step['original_text']) > 50 else parsed_step['original_text']")
        
        return code
