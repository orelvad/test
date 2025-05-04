"""
Register Operations Module

This module provides functions for reading from and writing to hardware registers.
It supports different access methods (memory-mapped I/O, SPI, I2C, etc.) based on configuration.
"""

import time
import logging
from typing import Dict, Any, Optional, Union, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('register_ops')

# Mock register access for demonstration purposes
class RegisterSimulator:
    def __init__(self):
        # Initialize register map with default values
        self.register_map = {}
        self.initialize_default_registers()
    
    def initialize_default_registers(self):
        """Initialize default registers with some values"""
        # Control registers
        self.register_map["0x0000"] = 0x0000  # Status register
        self.register_map["0x0001"] = 0x0001  # Control register
        self.register_map["0x0002"] = 0x0000  # Interrupt status
        self.register_map["0x0003"] = 0x0000  # Interrupt mask
        
        # Configuration registers
        self.register_map["0x0010"] = 0x0001  # Clock configuration
        self.register_map["0x0011"] = 0x0040  # Power configuration
        self.register_map["0x0012"] = 0x0030  # Interface configuration
        
        # Data registers
        for i in range(0x0100, 0x0110):
            addr = f"0x{i:04X}"
            self.register_map[addr] = 0x0000
        
        # Add some hex addresses as well
        self.register_map["0xA000"] = 0xA000
        self.register_map["0xB000"] = 0xB000
        
        logger.debug("Initialized default register map")
    
    def read(self, address: str) -> int:
        """
        Read from a register address.
        
        Args:
            address (str): Register address in hex or decimal
            
        Returns:
            int: Register value
        """
        # Convert decimal address to hex if needed
        if isinstance(address, str) and not address.startswith("0x"):
            try:
                addr_int = int(address)
                address = f"0x{addr_int:04X}"
            except ValueError:
                logger.error(f"Invalid address format: {address}")
                return 0
        
        # Ensure address is properly formatted
        if isinstance(address, int):
            address = f"0x{address:04X}"
        
        # Read from register map
        if address in self.register_map:
            value = self.register_map[address]
            logger.debug(f"Read register {address} = 0x{value:04X}")
            return value
        else:
            # If address doesn't exist, create it with default value 0
            self.register_map[address] = 0
            logger.warning(f"Register {address} not in map, creating with default value 0")
            return 0
    
    def write(self, address: str, value: int) -> bool:
        """
        Write to a register address.
        
        Args:
            address (str): Register address in hex or decimal
            value (int): Value to write
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Convert decimal address to hex if needed
        if isinstance(address, str) and not address.startswith("0x"):
            try:
                addr_int = int(address)
                address = f"0x{addr_int:04X}"
            except ValueError:
                logger.error(f"Invalid address format: {address}")
                return False
        
        # Ensure address is properly formatted
        if isinstance(address, int):
            address = f"0x{address:04X}"
        
        # Write to register map
        try:
            # Ensure value is an integer
            if isinstance(value, str):
                if value.startswith("0x"):
                    value = int(value, 16)
                else:
                    value = int(value)
            
            self.register_map[address] = value
            logger.debug(f"Wrote register {address} = 0x{value:04X}")
            
            # Simulate register side effects for demonstration
            if address == "0x0001":  # Control register
                if value & 0x0001:  # If bit 0 is set (enable)
                    self.register_map["0x0000"] |= 0x0001  # Set enabled bit in status
                else:
                    self.register_map["0x0000"] &= ~0x0001  # Clear enabled bit in status
            
            return True
        except Exception as e:
            logger.error(f"Error writing to register {address}: {e}")
            return False


# Create global register simulator instance for demonstration
_register_simulator = RegisterSimulator()


def read_register(address: Union[str, int], access_method: str = "default") -> int:
    """
    Read a value from the specified register address.
    
    Args:
        address (str or int): Register address in hex (0x...) or decimal
        access_method (str): Method to access the register ("memory", "spi", "i2c", etc.)
        
    Returns:
        int: Register value
    """
    try:
        # In a real implementation, you would have different access methods
        # based on the specified access_method parameter
        
        if access_method == "memory":
            # Memory-mapped I/O implementation would go here
            pass
        elif access_method == "spi":
            # SPI access implementation would go here
            pass
        elif access_method == "i2c":
            # I2C access implementation would go here
            pass
        else:
            # Default access using simulator
            value = _register_simulator.read(address)
            logger.info(f"Read register {address} = 0x{value:04X}")
            return value
        
    except Exception as e:
        logger.error(f"Error reading register {address}: {e}")
        return 0


def write_register(address: Union[str, int], value: Union[str, int], 
                  access_method: str = "default", verify: bool = True) -> bool:
    """
    Write a value to the specified register address.
    
    Args:
        address (str or int): Register address in hex (0x...) or decimal
        value (str or int): Value to write in hex (0x...) or decimal
        access_method (str): Method to access the register ("memory", "spi", "i2c", etc.)
        verify (bool): Verify the write by reading back the value
        
    Returns:
        bool: True if successful (and verified if verify=True), False otherwise
    """
    try:
        # In a real implementation, you would have different access methods
        # based on the specified access_method parameter
        
        if access_method == "memory":
            # Memory-mapped I/O implementation would go here
            pass
        elif access_method == "spi":
            # SPI access implementation would go here
            pass
        elif access_method == "i2c":
            # I2C access implementation would go here
            pass
        else:
            # Default access using simulator
            success = _register_simulator.write(address, value)
            if not success:
                return False
            
            if verify:
                # Read back the value to verify
                read_value = _register_simulator.read(address)
                if isinstance(value, str) and value.startswith("0x"):
                    value = int(value, 16)
                elif isinstance(value, str):
                    value = int(value)
                
                if read_value != value:
                    logger.error(f"Verification failed for register {address}: wrote 0x{value:04X}, read 0x{read_value:04X}")
                    return False
            
            logger.info(f"Wrote register {address} = 0x{value:04X}")
            return True
        
    except Exception as e:
        logger.error(f"Error writing register {address}: {e}")
        return False


def modify_register_bits(address: Union[str, int], bit_mask: Union[str, int], 
                        bit_values: Union[str, int], access_method: str = "default") -> bool:
    """
    Modify specific bits of a register while preserving others.
    
    Args:
        address (str or int): Register address in hex (0x...) or decimal
        bit_mask (str or int): Bit mask indicating which bits to modify
        bit_values (str or int): Values for the bits specified by the mask
        access_method (str): Method to access the register
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read current value
        current_value = read_register(address, access_method)
        
        # Convert parameters to integers if they're hex strings
        if isinstance(bit_mask, str) and bit_mask.startswith("0x"):
            bit_mask = int(bit_mask, 16)
        elif isinstance(bit_mask, str):
            bit_mask = int(bit_mask)
            
        if isinstance(bit_values, str) and bit_values.startswith("0x"):
            bit_values = int(bit_values, 16)
        elif isinstance(bit_values, str):
            bit_values = int(bit_values)
        
        # Clear bits specified by mask
        cleared_value = current_value & ~bit_mask
        
        # Set new bit values (masked to ensure only masked bits are set)
        new_value = cleared_value | (bit_values & bit_mask)
        
        # Write the new value back
        success = write_register(address, new_value, access_method)
        
        if success:
            logger.info(f"Modified register {address}: mask=0x{bit_mask:04X}, values=0x{bit_values:04X}, result=0x{new_value:04X}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error modifying register {address} bits: {e}")
        return False


def wait_for_register_value(address: Union[str, int], expected_value: Union[str, int],
                           mask: Union[str, int] = None, timeout_ms: int = 1000,
                           interval_ms: int = 10, access_method: str = "default") -> bool:
    """
    Wait for a register to contain an expected value, possibly masked.
    
    Args:
        address (str or int): Register address in hex (0x...) or decimal
        expected_value (str or int): Expected value to wait for
        mask (str or int, optional): Mask to apply to both the read value and expected value
        timeout_ms (int): Maximum time to wait in milliseconds
        interval_ms (int): Interval between reads in milliseconds
        access_method (str): Method to access the register
        
    Returns:
        bool: True if the expected value was found within timeout, False otherwise
    """
    try:
        # Convert parameters to integers if they're hex strings
        if isinstance(expected_value, str) and expected_value.startswith("0x"):
            expected_value = int(expected_value, 16)
        elif isinstance(expected_value, str):
            expected_value = int(expected_value)
            
        if mask is not None:
            if isinstance(mask, str) and mask.startswith("0x"):
                mask = int(mask, 16)
            elif isinstance(mask, str):
                mask = int(mask)
        
        # Calculate timeout
        start_time = time.time()
        timeout_s = timeout_ms / 1000.0
        interval_s = interval_ms / 1000.0
        
        while time.time() - start_time < timeout_s:
            # Read current value
            current_value = read_register(address, access_method)
            
            # Apply mask if specified
            if mask is not None:
                current_value &= mask
                expected_value &= mask
            
            # Check if value matches
            if current_value == expected_value:
                logger.info(f"Register {address} matched expected value 0x{expected_value:04X} after {(time.time() - start_time) * 1000:.1f}ms")
                return True
            
            # Wait for next interval
            time.sleep(interval_s)
        
        logger.warning(f"Timeout waiting for register {address} to match expected value 0x{expected_value:04X}")
        return False
        
    except Exception as e:
        logger.error(f"Error waiting for register {address} value: {e}")
        return False
