# get_models.py
import os
import yaml
from openai import OpenAI
import json
from datetime import datetime

def load_config():
    """Load configuration from config.yaml file"""
    config_file = 'config.yaml'
    
    # Check if config file exists
    if not os.path.exists(config_file):
        # Create a template config file
        default_config = {
            'openai': {
                'api_key': 'YOUR_API_KEY_HERE'
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Config file '{config_file}' created. Please edit it with your actual API key.")
        return None
    
    # Load config from file
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate config
    if not config or 'openai' not in config or 'api_key' not in config['openai']:
        print(f"Error: Config file '{config_file}' is missing required fields.")
        return None
    
    # Check if the API key is still the default placeholder
    if config['openai']['api_key'] == 'YOUR_API_KEY_HERE':
        print(f"Error: Please update '{config_file}' with your actual OpenAI API key.")
        return None
    
    return config

def get_available_models():
    """Get a list of available models from OpenAI API"""
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Get API key from config
    api_key = config['openai']['api_key']
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Get the list of available models
        models = client.models.list()
        
        # Create a timestamp for the output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'openai_models_{timestamp}.json'
        
        # Extract model information
        model_info = []
        for model in models.data:
            model_data = {
                'id': model.id,
                'created': model.created,
                'owned_by': model.owned_by
            }
            model_info.append(model_data)
        
        # Sort models by creation date (newest first)
        model_info.sort(key=lambda x: x['created'], reverse=True)
        
        # Print the models to the console
        print("\nAvailable OpenAI Models:")
        print("=" * 80)
        print(f"{'Model ID':<40} {'Created':<15} {'Owned By':<20}")
        print("-" * 80)
        
        for model in model_info:
            # Convert timestamp to readable date
            created_date = datetime.fromtimestamp(model['created']).strftime('%Y-%m-%d')
            print(f"{model['id']:<40} {created_date:<15} {model['owned_by']:<20}")
        
        # Save the complete model data to a JSON file
        with open(output_file, 'w') as f:
            json.dump(models.dict(), f, indent=2)
        
        print("\nComplete model information saved to:", output_file)
        
        # Print GPT-4 models specifically (these are the most powerful ones)
        gpt4_models = [m for m in model_info if 'gpt-4' in m['id']]
        
        if gpt4_models:
            print("\nGPT-4 Models Available:")
            print("-" * 80)
            for model in gpt4_models:
                created_date = datetime.fromtimestamp(model['created']).strftime('%Y-%m-%d')
                print(f"{model['id']:<40} {created_date:<15} {model['owned_by']:<20}")
        
    except Exception as e:
        print(f"Error getting available models: {e}")

if __name__ == "__main__":
    get_available_models()