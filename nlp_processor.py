import spacy
import re
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('nlp_processor')

class NLPProcessor:
    """
    Natural Language Processor for test step descriptions using spaCy.
    Extracts actions, equipment, parameters, and other relevant information.
    """
    
    def __init__(self, model_name="en_core_web_trf"):
        """
        Initialize the NLP processor with a spaCy model.
        
        Args:
            model_name (str): Name of the spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Downloading...")
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
            logger.info(f"Downloaded and loaded spaCy model: {model_name}")
        
        self._load_equipment_patterns()
        self._load_action_patterns()
        self._load_parameter_patterns()
        self._add_custom_components()
    
    def _load_equipment_patterns(self):
        """Load patterns for recognizing equipment names"""
        self.equipment_patterns = [
            "keysight",
            "power supply", 
            "oscilloscope",
            "signal generator",
            "spectrum analyzer",
            "multimeter",
            "source meter",
            "network analyzer",
            "logic analyzer",
            "arbitrary waveform generator",
            "power meter",
            "frequency counter"
        ]
    
    def _load_action_patterns(self):
        """Load patterns for recognizing actions"""
        self.action_patterns = {
            "set": ["set", "configure", "adjust", "change", "modify"],
            "get": ["get", "read", "measure", "acquire", "retrieve", "monitor"],
            "verify": ["verify", "check", "validate", "confirm", "ensure", "assert"],
            "connect": ["connect", "link", "attach", "join"],
            "disconnect": ["disconnect", "detach", "remove", "separate"],
            "wait": ["wait", "delay", "pause", "sleep"],
            "initialize": ["initialize", "init", "start", "boot", "power on", "turn on"],
            "shutdown": ["shutdown", "stop", "power off", "turn off", "terminate"]
        }
    
    def _load_parameter_patterns(self):
        """Load patterns for recognizing measurement parameters"""
        self.parameter_patterns = {
            "voltage": ["voltage", "volt", "V"],
            "current": ["current", "ampere", "amp", "A", "mA", "µA"],
            "resistance": ["resistance", "ohm", "Ω", "kΩ", "MΩ"],
            "power": ["power", "watt", "W", "mW", "kW"],
            "frequency": ["frequency", "freq", "Hz", "kHz", "MHz", "GHz"],
            "time": ["time", "second", "s", "ms", "µs", "ns"],
            "temperature": ["temperature", "temp", "°C", "celsius", "fahrenheit", "°F"],
            "phase": ["phase", "degree", "°"],
            "address": ["address", "register", "addr", "reg"]
        }
    
    def _add_custom_components(self):
        """Add custom components to the spaCy pipeline if needed"""
        # Could extend the pipeline with custom components here
        pass
    
    def extract_entities(self, doc):
        """
        Extract relevant entities from the spaCy Doc object.
        
        Args:
            doc (spacy.tokens.Doc): Processed spaCy document
            
        Returns:
            dict: Dictionary of extracted entities
        """
        entities = {
            "equipment": [],
            "actions": [],
            "parameters": {},
            "values": {},
            "addresses": [],
            "conditions": [],
        }
        
        # Extract equipment mentions
        for equipment in self.equipment_patterns:
            if equipment.lower() in doc.text.lower():
                entities["equipment"].append(equipment)
        
        # Extract action verbs
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', doc.text.lower()):
                    if action_type not in entities["actions"]:
                        entities["actions"].append(action_type)
        
        # Extract parameters and values with improved pattern matching
        for param_type, patterns in self.parameter_patterns.items():
            for pattern in patterns:
                # Match patterns like "3.3V", "10 MHz", "100mA"
                # This improved regex handles various unit formats
                regex_patterns = [
                    r'(\d+(?:\.\d+)?)\s*' + pattern,  # e.g., "3.3 V"
                    r'(\d+(?:\.\d+)?)' + pattern,      # e.g., "3.3V"
                ]
                
                for regex in regex_patterns:
                    matches = re.finditer(regex, doc.text.lower())
                    for match in matches:
                        value = float(match.group(1))
                        entities["parameters"][param_type] = True
                        entities["values"][param_type] = value
                        break  # Found a match for this pattern, move to next param_type
                
                # Also look for mentions without specific values
                if param_type not in entities["parameters"] and re.search(r'\b' + pattern + r'\b', doc.text.lower()):
                    entities["parameters"][param_type] = True
        
        # Extract register addresses (hexadecimal or decimal)
        addr_matches = re.finditer(r'(?:register|reg|address|addr)\s+(0x[0-9a-fA-F]+|\d+)', doc.text, re.IGNORECASE)
        for match in addr_matches:
            addr = match.group(1)
            entities["addresses"].append(addr)
            
        # Also look for direct mentions of hex addresses like 0xA000
        hex_addr_matches = re.finditer(r'\b(0x[0-9a-fA-F]+)\b', doc.text)
        for match in hex_addr_matches:
            addr = match.group(1)
            if addr not in entities["addresses"]:
                entities["addresses"].append(addr)
                
        # Extract register values in hex format
        reg_value_matches = re.finditer(r'(?:value|set|write).*?(0x[0-9a-fA-F]+)', doc.text, re.IGNORECASE)
        for match in reg_value_matches:
            value = match.group(1)
            entities["values"]["value"] = int(value, 16)
            entities["parameters"]["value"] = True
        
        # Extract conditional statements (e.g., "if ... then ...")
        condition_matches = re.finditer(r'if\s+.*?\s+then\s+.*?(?:\.|$)', doc.text, re.IGNORECASE)
        for match in condition_matches:
            entities["conditions"].append(match.group(0))
        
        return entities
    
    def process(self, text):
        """
        Process a test step description and extract structured information.
        
        Args:
            text (str): Natural language description of a test step
            
        Returns:
            dict: Structured representation of the test step
        """
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract relevant entities
        entities = self.extract_entities(doc)
        
        # Determine the primary action
        primary_action = entities["actions"][0] if entities["actions"] else "unknown"
        
        # Structure the parsed information
        parsed_step = {
            "original_text": text,
            "primary_action": primary_action,
            "actions": entities["actions"],
            "equipment": entities["equipment"],
            "parameters": {},
            "addresses": entities["addresses"],
            "conditions": entities["conditions"],
        }
        
        # Add parameters and their values
        for param, value in entities["values"].items():
            parsed_step["parameters"][param] = value
        
        # Add any other parameters without specific values
        for param in entities["parameters"]:
            if param not in parsed_step["parameters"]:
                parsed_step["parameters"][param] = None
        
        # Add syntactic dependencies for more complex analysis
        dependencies = []
        for token in doc:
            if token.dep_ != "punct" and token.head != token:
                dependencies.append({
                    "token": token.text,
                    "relation": token.dep_,
                    "head": token.head.text
                })
        parsed_step["dependencies"] = dependencies
        
        logger.info(f"Processed input: '{text[:50]}...' if len(text) > 50 else text")
        return parsed_step
