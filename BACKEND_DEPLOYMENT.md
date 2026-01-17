# FitPro Backend Deployment Guide

## Option 1: Deploy to Render.com (Recommended - Always Free)

### Step 1: Create GitHub Repository for Backend
1. Go to GitHub and create a new repo called `fitpro-backend`
2. Clone it: `git clone https://github.com/YOUR_USERNAME/fitpro-backend.git`
3. Copy these files into the repo:
   - `fitpro_backend.py` (rename to `app.py`)
   - `backend_requirements.txt` (rename to `requirements.txt`)
   - `.env` file (with your API key)
4. Create `runtime.txt` with: `python-3.11.9`
5. Push to GitHub

### Step 2: Deploy to Render.com
1. Go to https://render.com (sign up with GitHub)
2. Click "New +" → "Web Service"
3. Connect your `fitpro-backend` repo
4. Fill in:
   - **Name:** fitpro-backend
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click "Advanced" and add environment variable:
   - **Key:** `FITPRO_GEMINI_API_KEY`
   - **Value:** `AIzaSyDnBS9gmW6Dr6uY5WAX4KdY4pFnwWj9DOA`
6. Click "Create Web Service"
7. Wait 5 minutes for deployment

### Step 3: Get Your Backend URL
- Once deployed, you'll get a URL like: `https://fitpro-backend.onrender.com`
- Test it: Visit `https://fitpro-backend.onrender.com/health`
- Should see: `{"status":"ok","message":"FitPro Backend is running"}`

### Step 4: Update Your App
- Replace `backend_url` in `fitpro.py` with your Render URL

---

## Option 2: Local Testing (For Testing Only)

### Run Backend Locally
```bash
cd d:\downloads\Python workspace
pip install -r backend_requirements.txt
python fitpro_backend.py
```

Backend will run at `http://localhost:5000`

To test chatbot on your phone:
- Connect phone and PC to same WiFi
- Find your PC's IP: `ipconfig` (look for IPv4 Address, e.g., 192.168.1.100)
- Use `http://192.168.1.100:5000` as backend URL
- **Note:** Must keep PC running and server active

---

## Testing the Backend

### Using curl:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is a good daily step goal?"}'
```

### Expected Response:
```json
{
  "success": true,
  "message": "A healthy daily step goal is typically 10,000 steps, but aim for at least 7,000-8,000 steps daily. Any increase in movement is beneficial for your health!",
  "timestamp": null
}
```

---

## Troubleshooting

**Backend not connecting:**
- Check your Render URL is correct
- Make sure API key is set as environment variable
- Test with: `https://your-url.onrender.com/health`

**Chatbot still showing fallback responses:**
- Make sure internet connection is working
- Check backend URL in fitpro.py
- Verify backend is running (check Render dashboard)

**API key errors:**
- Make sure `FITPRO_GEMINI_API_KEY` environment variable is set
- Don't hardcode API key directly in files

