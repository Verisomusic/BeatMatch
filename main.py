"""
Music Label Matcher - FastAPI Backend
Deploy this to Render.com

Start command: uvicorn main:app --host 0.0.0.0 --port 10000
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import librosa
import numpy as np
import tempfile
import os
from typing import List, Dict
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = FastAPI(title="Music Label Matcher API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify configuration (you'll need to set these as environment variables)
# Get these from: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# Initialize Spotify client if credentials are provided
sp = None
if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        ))
    except Exception as e:
        print(f"Spotify initialization failed: {e}")


def classify_style(tempo: float) -> str:
    """Classify music style based on tempo."""
    if tempo < 90:
        return "Ambient / Downtempo"
    elif tempo < 115:
        return "Pop / R&B"
    elif tempo < 128:
        return "House"
    elif tempo < 140:
        return "Techno"
    elif tempo < 160:
        return "Drum & Bass / Jungle"
    else:
        return "Fast Electronic / Hardcore"


def get_genre_keywords(tempo: float) -> List[str]:
    """Get genre keywords for Spotify search based on tempo."""
    if tempo < 90:
        return ["ambient", "downtempo", "chillout", "lofi"]
    elif tempo < 115:
        return ["pop", "rnb", "indie", "alternative"]
    elif tempo < 128:
        return ["house", "deep house", "tech house"]
    elif tempo < 140:
        return ["techno", "minimal techno", "progressive"]
    elif tempo < 160:
        return ["drum and bass", "dnb", "jungle"]
    else:
        return ["hardcore", "hardstyle", "gabber"]


def search_labels_on_spotify(tempo: float) -> List[Dict[str, str]]:
    """Search for similar labels on Spotify based on tempo/genre."""
    if not sp:
        return [
            {"name": "Spotify API not configured", "url": "https://developer.spotify.com/dashboard"},
            {"name": "Set SPOTIFY_CLIENT_ID", "url": "https://developer.spotify.com/dashboard"},
            {"name": "Set SPOTIFY_CLIENT_SECRET", "url": "https://developer.spotify.com/dashboard"}
        ]
    
    labels = []
    keywords = get_genre_keywords(tempo)
    
    try:
        # Search for artists in the genre
        for keyword in keywords[:2]:  # Limit to 2 genres
            results = sp.search(q=f"genre:{keyword}", type="artist", limit=5)
            
            if results and results.get("artists") and results["artists"].get("items"):
                for artist in results["artists"]["items"]:
                    # Get artist's top tracks to find labels
                    artist_id = artist["id"]
                    top_tracks = sp.artist_top_tracks(artist_id)
                    
                    if top_tracks and top_tracks.get("tracks"):
                        for track in top_tracks["tracks"][:2]:  # Check first 2 tracks
                            album = track.get("album", {})
                            label = album.get("label", "")
                            
                            if label and label not in [l["name"] for l in labels]:
                                labels.append({
                                    "name": label,
                                    "url": artist.get("external_urls", {}).get("spotify", "")
                                })
                            
                            if len(labels) >= 8:  # Limit to 8 labels
                                return labels
    
    except Exception as e:
        print(f"Spotify search error: {e}")
        return [{"name": f"Search error: {str(e)}", "url": ""}]
    
    # Fallback if no labels found
    if not labels:
        labels = get_fallback_labels(tempo)
    
    return labels[:8]


def get_fallback_labels(tempo: float) -> List[Dict[str, str]]:
    """Return curated fallback labels based on tempo."""
    if tempo < 90:
        return [
            {"name": "Ninja Tune", "url": "https://open.spotify.com/label/0aOC4pKKYl9wDLqaScqBKq"},
            {"name": "Ghostly International", "url": "https://open.spotify.com/label/0f1J4JvjYbVB1p1ZvLQmZg"},
            {"name": "Warp Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"}
        ]
    elif tempo < 115:
        return [
            {"name": "XL Recordings", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Interscope Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Republic Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"}
        ]
    elif tempo < 128:
        return [
            {"name": "Defected Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Toolroom Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Spinnin' Deep", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"}
        ]
    elif tempo < 140:
        return [
            {"name": "Drumcode", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Afterlife", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "KNTXT", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"}
        ]
    else:
        return [
            {"name": "Hospital Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "RAM Records", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"},
            {"name": "Critical Music", "url": "https://open.spotify.com/label/0aT7J5CbM8kHPVnFLGZsLz"}
        ]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "Music Label Matcher API",
        "spotify_configured": sp is not None
    }


@app.post("/analyze")
async def analyze_track(file: UploadFile = File(...)):
    """
    Analyze an uploaded WAV file and return:
    - tempo (BPM)
    - spectral_centroid
    - spectral_bandwidth
    - style classification
    - recommended labels
    """
    
    # Validate file type
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only WAV files are supported")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        try:
            # Save uploaded file
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            temp_path = tmp_file.name
            
            # Load audio with librosa
            y, sr = librosa.load(temp_path, sr=22050)
            
            # Extract tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo)
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_centroid = float(np.mean(spectral_centroids))
            
            spectral_bandwidths = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_bandwidth = float(np.mean(spectral_bandwidths))
            
            # Classify style
            style = classify_style(tempo)
            
            # Get label recommendations
            recommended_labels = search_labels_on_spotify(tempo)
            
            return {
                "tempo": tempo,
                "spectral_centroid": spectral_centroid,
                "spectral_bandwidth": spectral_bandwidth,
                "style": style,
                "recommended_labels": recommended_labels
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
