from flask import Flask, request, jsonify
import requests
import re
import sys

app = Flask(__name__)

# Your YouTube API key
YOUTUBE_API_KEY = "AIzaSyBZKN7j0rj22Da7uTbY0E-SIHSn3WGlgZ4"
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

def fetch_youtube_data(query):
    """Fetch search results from YouTube API."""
    try:
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
    except Exception as e:
        print("Error in fetch_youtube_data:", e, file=sys.stderr)
        return {"error": str(e)}

def fetch_video_details(video_ids):
    """Fetch additional video details (e.g., views, likes, comments) from the YouTube API."""
    try:
        params = {
            "part": "snippet,statistics",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(YOUTUBE_VIDEOS_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch video details. HTTP Status Code: {response.status_code}"}
    except Exception as e:
        print("Error in fetch_video_details:", e, file=sys.stderr)
        return {"error": str(e)}

def format_search_response(data):
    """Format the YouTube API response for search results."""
    if "error" in data:
        return data["error"]

    items = data.get("items", [])
    if not items:
        return []

    video_ids = [item["id"]["videoId"] for item in items if "videoId" in item["id"]]
    video_stats_response = fetch_video_details(video_ids)
    video_stats = {item["id"]: item for item in video_stats_response.get("items", [])}

    video_details = []
    for item in items:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        stats = video_stats.get(video_id, {}).get("statistics", {})
        video_details.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "imageUrl": snippet["thumbnails"]["high"]["url"],
            "link": f"https://youtube.com/watch?v={video_id}",
            "views": stats.get("viewCount", "N/A")
        })

    return video_details

def format_video_response(data):
    """Format the response for a specific video."""
    if "error" in data:
        return data["error"]

    items = data.get("items", [])
    if not items:
        return {"error": "Video not found or API returned empty data"}

    item = items[0]
    snippet = item["snippet"]
    stats = item["statistics"]
    return {
        "title": snippet["title"],
        "channel": snippet["channelTitle"],
        "imageUrl": snippet["thumbnails"]["high"]["url"],
        "link": f"https://youtube.com/watch?v={item['id']}",
        "views": stats.get("viewCount", "N/A"),
        "likes": stats.get("likeCount", "N/A"),
        "comments": stats.get("commentCount", "N/A")
    }

def extract_video_id_from_url(url):
    """Extract video ID from a YouTube URL."""
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route('/api', methods=['GET'])
def youtube_api():
    """Handle YouTube search or specific video queries."""
    query = request.args.get('query')
    if not query:
        return jsonify({"status": False, "message": "Query parameter is missing"}), 400

    try:
        # Check if query is a URL
        video_id = extract_video_id_from_url(query)
        if video_id:
            video_data = fetch_video_details([video_id])
            formatted_data = format_video_response(video_data)
            if isinstance(formatted_data, str):  # error string
                return jsonify({"status": False, "message": formatted_data}), 500
            return jsonify({
                "status": True,
                "creator": "API DEVELOPER @TheSmartDev & @agent",
                "result": formatted_data
            })

        # Search query
        youtube_data = fetch_youtube_data(query)
        formatted_data = format_search_response(youtube_data)
        if isinstance(formatted_data, str):
            return jsonify({"status": False, "message": formatted_data}), 500
        return jsonify({
            "status": True,
            "creator": "API DEVELOPER @TheSmartDev & @agent",
            "result": formatted_data
        })

    except Exception as e:
        print("Error in main /api route:", e, file=sys.stderr)
        return jsonify({"status": False, "message": "Internal server error"}), 500

# Vercel-compatible handler
def handler(environ, start_response):
    return app(environ, start_response)
