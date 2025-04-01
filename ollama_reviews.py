import os
import csv
import requests
import time
import json

def process_review_with_ollama(review_text, artist, album, model="llama3"):
    """Process a review using a local Ollama model"""
    try:
        # Create a prompt for the model to reformat the review
        prompt = f"""
I have a music review for the album "{album}" by "{artist}" from Angry Metal Guy website.
Please reformat this review to make it easier to read, with:
1. Clear sections
2. Better paragraph organization
3. Highlighted key points
4. A summary of pros and cons at the end
5. Keep all the original content but make it more reader-friendly

Here is the review:
---
{review_text}
---

Provide only the reformatted review without any additional commentary.
"""

        # Call the Ollama API
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error processing review with Ollama: {e}")
        return None

def main():
    # Setup directories
    reviews_folder = "album_reviews"
    reformatted_folder = "reformatted_reviews"
    
    # Choose which model to use - Llama 3 is recommended for text reformatting
    model = "llama3"  # Alternatives: "mistral", "phi3", "gemma:7b", etc.
    
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
            
            # Process with local model
            print(f"Sending to {model} for reformatting...")
            reformatted_review = process_review_with_ollama(original_review, artist, album, model)
            
            if reformatted_review:
                # Save the reformatted review
                reformatted_path = os.path.join(reformatted_folder, filename)
                with open(reformatted_path, 'w', encoding='utf-8') as f:
                    # Keep the original metadata
                    f.write(metadata + "\n\n")
                    f.write(f"--- REFORMATTED BY {model.upper()} ---\n\n")
                    f.write(reformatted_review)
                
                print(f"Reformatted review saved to: {reformatted_path}")
            else:
                print(f"Failed to reformat review for {artist} - {album}")
                
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
        
        # Sleep between requests
        time.sleep(0.5)
    
    print("\nProcessing complete! All reviews have been reformatted.")

if __name__ == "__main__":
    main()
