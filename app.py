"""
FitPro Backend Server
Handles AI chatbot requests and communicates with Google Gemini API
"""

from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
API_KEY = os.getenv("FITPRO_GEMINI_API_KEY") or "AIzaSyDnBS9gmW6Dr6uY5WAX4KdY4pFnwWj9DOA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

SYSTEM_PROMPT = """You are a friendly and knowledgeable fitness assistant for the FitPro app. 
You help users with:
- Fitness advice and workout recommendations
- Nutrition and calorie information
- Motivation and goal-setting
- Exercise technique and form
- Recovery and rest advice

Be concise, friendly, and encouraging. Keep responses to 2-3 sentences unless more detail is requested.
If the question is not fitness-related, politely redirect to fitness topics."""


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "FitPro Backend is running"})


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests from the APK"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        # Combine system prompt with user message
        full_message = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"
        
        # Get response from Gemini
        response = model.generate_content(full_message)
        ai_response = response.text
        
        return jsonify({
            "success": True,
            "message": ai_response,
            "timestamp": None
        })
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Sorry, I couldn't process that. Please try again."
        }), 500


if __name__ == '__main__':
    # For local testing: app.run(debug=True, host='0.0.0.0', port=5000)
    # For production (Render): port from environment
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
