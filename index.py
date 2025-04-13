from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

YOUTUBE_API_KEY = "AIzaSyBZKN7j0rj22Da7uTbY0E-SIHSn3WGlgZ4"
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

def fetch_youtube_data(query):
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

def fetch_video_details(video_ids):
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

def format_search_response(data):
    if "error" in data:
        return data["error"]

    items = data.get("items", [])
    video_details = []
    video_ids = [item["id"]["videoId"] for item in items]

    video_stats_response = fetch_video_details(video_ids)
    video_stats = {item["id"]: item for item in video_stats_response.get("items", [])}

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
    if "error" in data:
        return data["error"]

    item = data.get("items", [])[0]
    if not item:
        return {"error": "Video not found"}

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
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route('/api', methods=['GET'])
def youtube_api():
    query = request.args.get('query')
    if not query:
        return jsonify({"status": False, "message": "Query parameter is missing"}), 400

    video_id = extract_video_id_from_url(query)
    if video_id:
        video_data = fetch_video_details([video_id])
        formatted_data = format_video_response(video_data)
        if isinstance(formatted_data, str):
            return jsonify({"status": False, "message": formatted_data}), 500
        return jsonify({
            "status": True,
            "creator": "API DEVELOPER @TheSmartDev & @agent",
            "result": formatted_data
        })

    youtube_data = fetch_youtube_data(query)
    formatted_data = format_search_response(youtube_data)
    if isinstance(formatted_data, str):
        return jsonify({"status": False, "message": formatted_data}), 500
    return jsonify({
        "status": True,
        "creator": "API DEVELOPER @TheSmartDev & @agent",
        "result": formatted_data
    })

# Vercel WSGI handler
def handler(environ, start_response):
    return app(environ, start_response)
