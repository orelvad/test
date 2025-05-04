# Test Step AI Generator

This project uses spaCy to convert natural language test step descriptions into executable code and JSON configuration files. It's specifically designed for test automation involving Keysight equipment and register operations.

## Features

- Natural language processing of test step descriptions
- Code generation for test automation
- JSON configuration file generation
- Support for Keysight equipment operations
- Register read/write operations

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Download the spaCy model:
   ```
   python -m spacy download en_core_web_md
   ```

3. Run the application:
   ```
   python app.py
   ```

## Usage

1. Enter your test step descriptions in natural language
2. The system will generate code snippets and JSON configuration files
3. The generated code will use existing functions for equipment operation and register access

## Structure

- `app.py`: Main application entry point
- `nlp_processor.py`: spaCy-based NLP processing
- `code_generator.py`: Code generation module
- `config_generator.py`: JSON configuration generator
- `equipment/`: Equipment operation modules
- `register/`: Register access functions
- `templates/`: Code and config templates
- `models/`: Custom spaCy models

## Examples

```
Input: "Set the power supply voltage to 3.3V and measure the current"

Output:
- Python code for executing the step
- JSON configuration with parameters
```
