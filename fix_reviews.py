import os
import csv
import yaml
from openai import OpenAI
import time

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

# Function to process a review with GPT-4.5
def process_review_with_gpt(client, review_text, artist, album):
    try:
        # Create a prompt for GPT to reformat the review
        prompt = f"""
I have a music review for the album "{album}" by "{artist}" from Angry Metal Guy website.
Please reformat this review to make it easier to read in a .txt file, with:
1. Clear sections
2. Better paragraph organization
4. Keep all the original content but make it more reader-friendly

Here is the review:
---
{review_text}
---

Provide only the reformatted review without any additional commentary.
"""

        # Call the OpenAI API with GPT-4.5
        response = client.chat.completions.create(
            model="gpt-4.5-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that specializes in reformatting music reviews to make them more readable while preserving all original content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Low temperature for more consistent formatting
        )
        
        # Extract the reformatted review from the response
        reformatted_review = response.choices[0].message.content.strip()
        return reformatted_review
        
    except Exception as e:
        print(f"Error processing review with GPT: {e}")
        return None

def main():
    # Load configuration
    config = load_config()
    if not config:
        return
    
    # Get API key from config
    api_key = config['openai']['api_key']
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Setup directories
    reviews_folder = "album_reviews"
    reformatted_folder = "reformatted_reviews"
    
    # Create reformatted reviews directory if it doesn't exist
    if not os.path.exists(reformatted_folder):
        os.makedirs(reformatted_folder)
    
    # Read the albums data from CSV
    albums_data = {}
    
    try:
        with open('tidal_favorite_albums_with_ratings.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                album_id = row.get('AlbumID')
                if album_id:
                    albums_data[album_id] = {
                        'Artist': row.get('Artist', ''),
                        'Album': row.get('Album', ''),
                        'AMG_Rating': row.get('AMG_Rating', '')
                    }
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Process all review files
    review_files = [f for f in os.listdir(reviews_folder) if f.endswith('.txt')]
    
    for i, filename in enumerate(review_files):
        album_id = filename.split('.')[0]  # Extract album ID from filename
        review_file_path = os.path.join(reviews_folder, filename)
        
        # Check if we have album data for this ID
        if album_id not in albums_data:
            print(f"Warning: No album data found for ID {album_id}, skipping")
            continue
        
        artist = albums_data[album_id]['Artist']
        album = albums_data[album_id]['Album']
        
        print(f"\n[{i+1}/{len(review_files)}] Processing review for: {artist} - {album}")
        
        try:
            # Read the original review
            with open(review_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract review metadata (first 4 lines) and the review text
                lines = content.split('\n')
                metadata = '\n'.join(lines[:4])
                original_review = '\n'.join(lines[4:]).strip()
            
            # Process with GPT-4.5
            print(f"Sending to GPT for reformatting...")
            reformatted_review = process_review_with_gpt(client, original_review, artist, album)
            
            if reformatted_review:
                # Save the reformatted review
                reformatted_path = os.path.join(reformatted_folder, filename)
                with open(reformatted_path, 'w', encoding='utf-8') as f:
                    # Keep the original metadata
                    f.write(metadata + "\n\n")
                    f.write("--- REFORMATTED BY GPT ---\n\n")
                    f.write(reformatted_review)
                
                print(f"Reformatted review saved to: {reformatted_path}")
            else:
                print(f"Failed to reformat review for {artist} - {album}")
                
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
        
        # Sleep to avoid hitting rate limits
        time.sleep(1)
    
    print("\nProcessing complete! All reviews have been reformatted.")

if __name__ == "__main__":
    main()
