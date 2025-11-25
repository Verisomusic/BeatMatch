# Music Label Matcher Backend

FastAPI backend for analyzing audio tracks and finding matching record labels.

## Features

- Audio analysis using librosa (tempo, spectral features)
- Style classification based on BPM
- Spotify label recommendations
- Simple REST API

## Deployment to Render.com

### Step 1: Get Spotify API Credentials (Optional but Recommended)

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Name it "Music Label Matcher"
5. Copy your **Client ID** and **Client Secret**

### Step 2: Deploy to Render

1. Create account at https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (or upload files)
4. Configure:
   - **Name**: music-label-matcher-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Instance Type**: Free

5. Add Environment Variables (Settings → Environment):
   - `SPOTIFY_CLIENT_ID` = your Spotify client ID
   - `SPOTIFY_CLIENT_SECRET` = your Spotify client secret

6. Click "Create Web Service"

### Step 3: Get Your Backend URL

After deployment, Render will give you a URL like:
```
https://music-label-matcher-api.onrender.com
```

### Step 4: Update Frontend

In your Lovable frontend, update `src/pages/Index.tsx` line 42:

```typescript
const response = await fetch("https://YOUR-APP-NAME.onrender.com/analyze", {
```

Replace with your actual Render URL.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --port 10000
```

Server runs at: http://localhost:10000

## API Endpoints

### GET /
Health check endpoint

### POST /analyze
Analyze WAV file

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `file` (WAV file)

**Response:**
```json
{
  "tempo": 120.5,
  "spectral_centroid": 2500.3,
  "spectral_bandwidth": 1800.2,
  "style": "House",
  "recommended_labels": [
    {
      "name": "Defected Records",
      "url": "https://open.spotify.com/..."
    }
  ]
}
```

## Troubleshooting

### "Spotify API not configured"
- Add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables
- App will work without them but show fallback labels

### Build fails on Render
- Check that requirements.txt has correct versions
- librosa may take 5-10 minutes to install (this is normal)
- Make sure Python 3 is selected as environment

### Analysis takes too long
- First request after idle may take 30-60 seconds (Render cold start)
- Subsequent requests will be faster
- Consider upgrading to paid Render plan for always-on instances

## Notes

- Free Render tier spins down after 15 minutes of inactivity
- First request after idle will be slow (30-60 seconds)
- WAV files only (other formats not supported)
- Max file size depends on Render limits (~10MB recommended)
