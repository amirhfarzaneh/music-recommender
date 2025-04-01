# amg.py
import csv
import requests
from bs4 import BeautifulSoup
import time
import re
import uuid
import os
import shutil

def search_angry_metal_guy(album_name, artist_name):
    """Search for album reviews on Angry Metal Guy website"""
    # Format search query
    search_query = f"{artist_name} {album_name}"
    search_url = f"https://www.angrymetalguy.com/?s={search_query.replace(' ', '+')}"
    
    # Send request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Parse response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find search results
        search_results = soup.find_all('article', class_='post')
        
        for result in search_results:
            title_element = result.find('h2', class_='entry-title')
            if not title_element:
                continue
                
            title = title_element.text.strip()
            # Check if both artist and album name are in the title
            if artist_name.lower() in title.lower() and album_name.lower() in title.lower():
                link = title_element.find('a')['href']
                return link
        
        return None
    
    except Exception as e:
        print(f"Error searching for {artist_name} - {album_name}: {e}")
        return None

def extract_review_and_rating(review_url):
    """Extract review text and rating from a review page"""
    if not review_url:
        return None, None
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(review_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find review content
        review_content = soup.find('div', class_='entry-content')
        if not review_content:
            return None, None
            
        # Extract ALL text content, not just paragraphs
        # This gets text from paragraphs, blockquotes, headers, etc.
        review_text = review_content.get_text(separator="\n\n", strip=True)
        
        # Find rating
        rating = None
        # Look for rating pattern like "4.0/5.0" or similar
        rating_pattern = re.compile(r'(\d\.\d)/5\.0')
        
        # Check in the review text
        rating_match = rating_pattern.search(review_text)
        if rating_match:
            rating = rating_match.group(1)
        
        # Check in specific rating div if exists
        rating_div = soup.find('div', class_='rating')
        if rating_div and not rating:
            rating_text = rating_div.text.strip()
            rating_match = rating_pattern.search(rating_text)
            if rating_match:
                rating = rating_match.group(1)
        
        return review_text, rating
        
    except Exception as e:
        print(f"Error extracting review from {review_url}: {e}")
        return None, None

def main():
    # Create a directory for review texts
    reviews_folder = "album_reviews"
    if os.path.exists(reviews_folder):
        shutil.rmtree(reviews_folder)  # Remove if exists to start fresh
    os.makedirs(reviews_folder)
    
    # Read the existing CSV file
    input_csv = 'tidal_favorite_albums.csv'
    albums = []
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            for row in reader:
                # Generate a random ID for each album
                album_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for brevity
                row['AlbumID'] = album_id
                row['AMG_Rating'] = ""  # Add empty AMG_Rating field
                albums.append(row)
    except Exception as e:
        print(f"Error reading CSV file '{input_csv}': {e}")
        return

    print(f"Loaded {len(albums)} albums from {input_csv}")
    
    # Process ALL albums
    total_albums = len(albums)
    for i, album in enumerate(albums):
        artist_name = album['Artist']
        album_name = album['Album']
        album_id = album['AlbumID']
        
        print(f"\n[{i+1}/{total_albums}] Searching for review: {artist_name} - {album_name} (ID: {album_id})")
        
        # Search for review
        review_url = search_angry_metal_guy(album_name, artist_name)
        
        if review_url:
            print(f"Found review at: {review_url}")
            
            # Extract review and rating
            review_text, rating = extract_review_and_rating(review_url)
            
            if review_text:
                # Save review text to file
                review_filename = os.path.join(reviews_folder, f"{album_id}.txt")
                with open(review_filename, 'w', encoding='utf-8') as f:
                    f.write(f"Artist: {artist_name}\n")
                    f.write(f"Album: {album_name}\n")
                    f.write(f"Album ID: {album_id}\n")  # Include UUID in the review file
                    f.write(f"Review URL: {review_url}\n\n")
                    f.write(review_text)
                
                print(f"Review saved to: {review_filename}")
                
                if rating:
                    album['AMG_Rating'] = rating
                    print(f"Rating: {rating}/5.0")
                    print(f"Review excerpt: {review_text[:200]}...")
                else:
                    print(f"Review excerpt: {review_text[:200]}...")
                    print("Rating: Not found")
            else:
                print("Could not extract review or rating")
        else:
            print(f"No review found for {artist_name} - {album_name}")
        
        # Sleep to avoid overloading the server
        time.sleep(2)
    
    # Save updated CSV with AlbumID and AMG_Rating
    output_csv = 'tidal_favorite_albums_with_ratings.csv'
    
    # Add the new fields to the fieldnames list
    new_fieldnames = fieldnames + ['AlbumID', 'AMG_Rating']
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(albums)
    
    print(f"\nUpdated CSV saved to {output_csv}")
    print(f"Review texts saved to {reviews_folder}/ directory")
    print(f"Processed {total_albums} albums in total")

if __name__ == "__main__":
    main()