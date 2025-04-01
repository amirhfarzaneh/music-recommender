# Album Recommender Project

This project allows you to:
1. Retrieve your favorite albums from Tidal
2. Fetch album reviews from Angry Metal Guy website
3. Reformat these reviews using AI models (either OpenAI's API or local Ollama models)

## Setup and Installation

### Prerequisites
- Python 3.9 or higher
- Tidal account
- (Optional) OpenAI API key
- (Optional) GPU for local model inference

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tidal-album-reviews.git
   cd tidal-album-reviews
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For local AI models, install Ollama:
   - Visit [ollama.ai](https://ollama.ai) and follow the installation instructions for your platform
   - Pull the Llama 3 model: `ollama pull llama3`

## Step-by-Step Workflow

### 1. Getting Tidal Favorites
```python
# Run this to fetch your favorite albums from Tidal
python tidalapi_fetch.py
```

This script:
- Authenticates with your Tidal account
- Retrieves your favorite albums
- Saves album details to a CSV file (tidal_favorite_albums.csv)

### 2. Fetching Album Reviews
```python
# Run this to search for album reviews on Angry Metal Guy
python amg.py
```

This script:
- Reads the Tidal favorites CSV file
- Assigns a unique ID to each album
- Searches for album reviews on Angry Metal Guy
- Extracts review text and rating
- Saves reviews as text files in the "album_reviews" folder
- Updates the CSV file with review ratings and album IDs

### 3. Reformatting Reviews with AI

#### Option A: Using OpenAI API (requires API key)
```python
# First, create a config.yaml file with your API key
# Then run:
python openai.py
```

You can get available models with:
```python
python get_models.py
```

#### Option B: Using Local Ollama Models (requires GPU)
```python
# Make sure Ollama is running and you've pulled a model
# Then run:
python ollama_reviews.py
```

This script:
- Processes album reviews using local models
- Saves reformatted reviews in the "reformatted_reviews" folder

## File Structure

- `tidalapi_fetch.py` - Fetches favorite albums from Tidal
- `amg.py` - Retrieves album reviews from Angry Metal Guy
- `get_models.py` - Lists available OpenAI models
- `openai.py` - Reformats reviews using OpenAI API
- `ollama_reviews.py` - Reformats reviews using local models
- `config.yaml` - Configuration file for API keys
- `tidal_favorite_albums.csv` - Your favorite Tidal albums
- `tidal_favorite_albums_with_ratings.csv` - Albums with review ratings
- `album_reviews/` - Original album reviews
- `reformatted_reviews/` - AI-reformatted reviews

## Notes

- The `amg.py` script uses a 0.5-second delay between requests to avoid overloading the Angry Metal Guy website
- Local model inference is more cost-effective but requires a GPU
- The OpenAI API is more powerful but requires credits/payment

## Troubleshooting

### OpenAI API Quota Error
If you receive a quota error, you can:
1. Add billing information to your OpenAI account
2. Use a less expensive model like GPT-3.5 Turbo
3. Switch to local models using the Ollama approach

### Ollama Connection Error
If you can't connect to Ollama:
1. Ensure Ollama is running
2. Check that you've pulled the model: `ollama pull llama3`
3. Verify the API is accessible at localhost:11434

### Missing Album Reviews
Not all albums will have reviews on Angry Metal Guy. The script will show warnings for albums that don't have reviews.
