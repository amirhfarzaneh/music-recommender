import tidalapi
import time
import csv
import os

# Create a session
session = tidalapi.Session()

# Login using OAuth (this will display a URL to visit and link your account)
session.login_oauth_simple()

# Check if login was successful
if session.check_login():
    # Get your favorites
    favorites = session.user.favorites
    
    # Get your favorite albums
    favorite_albums = favorites.albums()
    
    # Prepare CSV file
    csv_filename = "tidal_favorite_albums.csv"
    
    # Write to CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Album', 'Artist', 'Release Date', 'Year', 'Cover URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Display albums with the specified metadata
        print("Your favorite albums:")
        for album in favorite_albums:
            album_data = {
                'Album': album.name,
                'Artist': album.artist.name,
                'Release Date': album.release_date,
                'Year': album.year,
                'Cover URL': album.image()
            }
            
            # Write to CSV
            writer.writerow(album_data)
            
            # Print to console
            print(f"- Album: {album.name}")
            print(f"  Artist: {album.artist.name}")
            print(f"  Release date: {album.release_date}")
            print(f"  Year: {album.year}")
            print(f"  Cover URL: {album.image()}")
            print("  ---")
            
            # Add a sleep to avoid hitting rate limits
            time.sleep(0.5)  # Wait 0.5 seconds between albums
    
    print(f"Data saved to {os.path.abspath(csv_filename)}")
else:
    print("Login failed!")



