from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# YouTube API Configuration
YOUTUBE_API_KEY = "AIzaSyBZKN7j0rj22Da7uTbY0E-SIHSn3WGlgZ4"
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"


def fetch_youtube_data(query):
    """Fetch search results from YouTube Data API."""
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(YOUTUBE_SEARCH_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch data. HTTP Status Code: {response.status_code}"}


@app.route('/')
def index():
    """Root route for the API."""
    return "Welcome to the YouTube Search API hosted on Vercel!"


@app.route('/api', methods=['GET'])
def youtube_search():
    """Handle YouTube search queries."""
    # Get the `query` parameter from the request
    query = request.args.get('query')
    if not query:
        return jsonify({"status": False, "message": "Query parameter is missing"}), 400

    # Fetch data from YouTube Data API
    youtube_data = fetch_youtube_data(query)
    
    # Check for errors in the response
    if "error" in youtube_data:
        return jsonify({"status": False, "message": youtube_data["error"]}), 500

    # Return the response in JSON format
    return jsonify({
        "status": True,
        "message": "YouTube data fetched successfully",
        "data": youtube_data
    })


if __name__ == '__main__':
    app.run(debug=True)
