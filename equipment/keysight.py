"""
Keysight Equipment Control Module

This module provides functions for controlling and interacting with Keysight test equipment,
such as power supplies, oscilloscopes, signal generators, and more.
"""

import time
import logging
from typing import Dict, Any, Optional, Union, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('keysight')

# Mock VISA interface for demonstration purposes
# In a real implementation, you would use a library like pyvisa
class MockVisa:
    def __init__(self):
        self.equipment_state = {
            'voltage': 0.0,
            'current': 0.0,
            'current_limit': 1.0,
            'frequency': 1000.0,
            'power': 0.0,
            'output_enabled': False,
            'connected': False
        }
    
    def write(self, command: str) -> None:
        """Mock writing a command to an instrument"""
        logger.debug(f"VISA Write: {command}")
        if command.startswith("VOLT "):
            try:
                voltage = float(command.replace("VOLT ", ""))
                self.equipment_state['voltage'] = voltage
                logger.info(f"Set voltage to {voltage}V")
            except ValueError:
                logger.error(f"Invalid voltage value in command: {command}")
        
        elif command.startswith("CURR "):
            try:
                current = float(command.replace("CURR ", ""))
                self.equipment_state['current_limit'] = current
                logger.info(f"Set current limit to {current}A")
            except ValueError:
                logger.error(f"Invalid current value in command: {command}")
        
        elif command.startswith("FREQ "):
            try:
                freq = float(command.replace("FREQ ", ""))
                self.equipment_state['frequency'] = freq
                logger.info(f"Set frequency to {freq}Hz")
            except ValueError:
                logger.error(f"Invalid frequency value in command: {command}")
        
        elif command == "OUTP ON":
            self.equipment_state['output_enabled'] = True
            logger.info("Output enabled")
        
        elif command == "OUTP OFF":
            self.equipment_state['output_enabled'] = False
            logger.info("Output disabled")
    
    def query(self, command: str) -> str:
        """Mock querying an instrument"""
        logger.debug(f"VISA Query: {command}")
        if command == "MEAS:VOLT?":
            return str(self.equipment_state['voltage'])
        
        elif command == "MEAS:CURR?":
            # In real equipment, the measured current might be different from the limit
            self.equipment_state['current'] = min(
                self.equipment_state['voltage'] / 100.0,  # Simulate a 100 ohm load
                self.equipment_state['current_limit']
            )
            return str(self.equipment_state['current'])
        
        elif command == "MEAS:POW?":
            # Calculate power based on V*I
            power = self.equipment_state['voltage'] * self.equipment_state['current']
            self.equipment_state['power'] = power
            return str(power)
        
        elif command == "FREQ?":
            return str(self.equipment_state['frequency'])
        
        elif command == "*IDN?":
            return "Keysight Technologies,E36313A,MY12345678,1.2.3"
        
        return "0.0"  # Default response for unrecognized commands


def initialize(address: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize Keysight equipment and establish a connection.
    
    Args:
        address (str, optional): VISA address of the equipment
        
    Returns:
        dict: Equipment connection object with necessary state
    """
    logger.info(f"Initializing Keysight equipment{f' at {address}' if address else ''}")
    
    # In a real implementation, you would use pyvisa to connect to the equipment
    # Example: rm = visa.ResourceManager(); inst = rm.open_resource(address)
    
    # For demonstration, create a mock VISA object
    visa_conn = MockVisa()
    visa_conn.equipment_state['connected'] = True
    
    # Create equipment connection object
    equipment = {
        'visa': visa_conn,
        'address': address or "GPIB0::22::INSTR",
        'type': 'keysight',
        'last_error': None
    }
    
    # Test connection by querying the equipment identification
    try:
        idn = visa_conn.query("*IDN?")
        equipment['model'] = idn.split(',')[1] if ',' in idn else "Unknown"
        logger.info(f"Connected to Keysight {equipment['model']}")
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error during initialization: {e}")
    
    return equipment


def get_equipment() -> Dict[str, Any]:
    """
    Get a reference to an already initialized equipment object.
    This is a mock function for demonstration purposes.
    
    Returns:
        dict: Equipment connection object
    """
    # In a real implementation, you might have a global registry of equipment
    # or retrieve equipment references from a database/file
    return initialize()


def set_voltage(equipment: Dict[str, Any], voltage: float) -> bool:
    """
    Set the output voltage of a power supply.
    
    Args:
        equipment (dict): Equipment connection object
        voltage (float): Voltage value to set in volts
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        visa_conn = equipment['visa']
        visa_conn.write(f"VOLT {voltage}")
        logger.info(f"Set voltage to {voltage}V")
        return True
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error setting voltage: {e}")
        return False


def set_current_limit(equipment: Dict[str, Any], current: float) -> bool:
    """
    Set the current limit of a power supply.
    
    Args:
        equipment (dict): Equipment connection object
        current (float): Current limit value in amperes
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        visa_conn = equipment['visa']
        visa_conn.write(f"CURR {current}")
        logger.info(f"Set current limit to {current}A")
        return True
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error setting current limit: {e}")
        return False


def set_frequency(equipment: Dict[str, Any], frequency: float) -> bool:
    """
    Set the frequency of a signal generator.
    
    Args:
        equipment (dict): Equipment connection object
        frequency (float): Frequency value in Hz
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        visa_conn = equipment['visa']
        visa_conn.write(f"FREQ {frequency}")
        logger.info(f"Set frequency to {frequency}Hz")
        return True
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error setting frequency: {e}")
        return False


def enable_output(equipment: Dict[str, Any], enable: bool = True) -> bool:
    """
    Enable or disable the output of a power supply or signal generator.
    
    Args:
        equipment (dict): Equipment connection object
        enable (bool): True to enable output, False to disable
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        visa_conn = equipment['visa']
        command = "OUTP ON" if enable else "OUTP OFF"
        visa_conn.write(command)
        logger.info(f"Output {'enabled' if enable else 'disabled'}")
        return True
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error {'enabling' if enable else 'disabling'} output: {e}")
        return False


def measure_voltage(equipment: Dict[str, Any]) -> float:
    """
    Measure the output voltage.
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        float: Measured voltage in volts
    """
    try:
        visa_conn = equipment['visa']
        result = visa_conn.query("MEAS:VOLT?")
        voltage = float(result)
        logger.info(f"Measured voltage: {voltage}V")
        return voltage
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error measuring voltage: {e}")
        return 0.0


def measure_current(equipment: Dict[str, Any]) -> float:
    """
    Measure the output current.
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        float: Measured current in amperes
    """
    try:
        visa_conn = equipment['visa']
        result = visa_conn.query("MEAS:CURR?")
        current = float(result)
        logger.info(f"Measured current: {current}A")
        return current
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error measuring current: {e}")
        return 0.0


def measure_power(equipment: Dict[str, Any]) -> float:
    """
    Measure or calculate the output power.
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        float: Measured or calculated power in watts
    """
    try:
        visa_conn = equipment['visa']
        
        # Some equipment provides direct power measurement
        try:
            result = visa_conn.query("MEAS:POW?")
            power = float(result)
        except:
            # If not available, calculate from voltage and current
            voltage = measure_voltage(equipment)
            current = measure_current(equipment)
            power = voltage * current
            
        logger.info(f"Power: {power}W")
        return power
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error measuring power: {e}")
        return 0.0


def measure_resistance(equipment: Dict[str, Any]) -> float:
    """
    Measure resistance (for multimeters).
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        float: Measured resistance in ohms
    """
    try:
        visa_conn = equipment['visa']
        # In a real implementation, you would switch to resistance mode first
        # visa_conn.write("FUNC 'RES'")
        result = visa_conn.query("MEAS:RES?")
        resistance = float(result)
        logger.info(f"Measured resistance: {resistance}Ω")
        return resistance
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error measuring resistance: {e}")
        return 0.0


def measure_frequency(equipment: Dict[str, Any]) -> float:
    """
    Measure the frequency of a signal.
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        float: Measured frequency in Hz
    """
    try:
        visa_conn = equipment['visa']
        result = visa_conn.query("FREQ?")
        frequency = float(result)
        logger.info(f"Measured frequency: {frequency}Hz")
        return frequency
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error measuring frequency: {e}")
        return 0.0


def shutdown(equipment: Dict[str, Any]) -> bool:
    """
    Safely shutdown the equipment.
    
    Args:
        equipment (dict): Equipment connection object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Disable output before closing
        enable_output(equipment, False)
        
        # In a real implementation, you would close the VISA connection
        # equipment['visa'].close()
        
        equipment['visa'].equipment_state['connected'] = False
        logger.info("Equipment safely shut down")
        return True
    except Exception as e:
        equipment['last_error'] = str(e)
        logger.error(f"Error shutting down equipment: {e}")
        return False
