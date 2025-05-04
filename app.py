import sys
import os
import argparse
import json
from pathlib import Path

from nlp_processor import NLPProcessor
from code_generator import CodeGenerator
from config_generator import ConfigGenerator

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate test code and configs from natural language')
    parser.add_argument('--input', '-i', type=str, help='Input file with test step descriptions')
    parser.add_argument('--output-dir', '-o', type=str, default='output', help='Output directory for generated files')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    return parser.parse_args()

def setup_environment():
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    # Create directories for generated code and configs
    code_dir = output_dir / 'code'
    config_dir = output_dir / 'configs'
    
    if not code_dir.exists():
        code_dir.mkdir(parents=True)
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
    
    return output_dir, code_dir, config_dir

def process_input_file(file_path, nlp_processor, code_generator, config_generator, output_dir):
    try:
        with open(file_path, 'r') as f:
            test_steps = f.read().strip().split('\n\n')
        
        results = []
        for i, step_text in enumerate(test_steps):
            if not step_text.strip():
                continue
                
            print(f"Processing step {i+1}...")
            parsed_step = nlp_processor.process(step_text)
            
            code_file = f"step_{i+1}.py"
            config_file = f"step_{i+1}_config.json"
            
            code = code_generator.generate(parsed_step)
            config = config_generator.generate(parsed_step)
            
            code_path = output_dir / 'code' / code_file
            config_path = output_dir / 'configs' / config_file
            
            with open(code_path, 'w') as f:
                f.write(code)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            results.append({
                'step_number': i + 1,
                'description': step_text,
                'code_file': str(code_path),
                'config_file': str(config_path)
            })
            
            print(f"Generated {code_file} and {config_file}")
        
        # Create a summary file
        summary_path = output_dir / 'summary.json'
        with open(summary_path, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"Processing complete. Results saved to {output_dir}")
        return results
        
    except Exception as e:
        print(f"Error processing input file: {e}")
        return None

def interactive_mode(nlp_processor, code_generator, config_generator, output_dir):
    print("=== Test Step AI Generator ===")
    print("Enter test step descriptions. Type 'exit' to quit.")
    print()
    
    step_count = 1
    while True:
        print(f"Step {step_count}:")
        lines = []
        
        while True:
            line = input()
            if line.strip().lower() == 'done':
                break
            lines.append(line)
        
        step_text = '\n'.join(lines)
        
        if step_text.strip().lower() == 'exit':
            break
            
        if not step_text.strip():
            continue
            
        try:
            parsed_step = nlp_processor.process(step_text)
            
            code_file = f"step_{step_count}.py"
            config_file = f"step_{step_count}_config.json"
            
            code = code_generator.generate(parsed_step)
            config = config_generator.generate(parsed_step)
            
            code_path = output_dir / 'code' / code_file
            config_path = output_dir / 'configs' / config_file
            
            with open(code_path, 'w') as f:
                f.write(code)
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
            print(f"\nGenerated files:")
            print(f"- Code: {code_path}")
            print(f"- Config: {config_path}")
            print("\nGenerated code preview:")
            print("------------------------")
            print('\n'.join(code.split('\n')[:10]) + '\n...\n')
            print("------------------------")
            
            step_count += 1
            
        except Exception as e:
            print(f"Error processing step: {e}")
        
        print("\nEnter next step description or 'exit' to quit:")

def main():
    args = parse_arguments()
    output_dir, code_dir, config_dir = setup_environment()
    
    # Initialize processors
    nlp_processor = NLPProcessor()
    code_generator = CodeGenerator()
    config_generator = ConfigGenerator()
    
    if args.interactive:
        interactive_mode(nlp_processor, code_generator, config_generator, output_dir)
    elif args.input:
        process_input_file(args.input, nlp_processor, code_generator, config_generator, output_dir)
    else:
        print("No input provided. Use --input FILE or --interactive")
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
