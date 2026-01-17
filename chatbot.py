"""
AI Chatbot Module for FitPro
Handles chat interactions with FitPro Backend or local fallback responses
"""

import json
from datetime import datetime
from typing import Optional, List, Dict
import socket
import requests


def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Check if device has internet connection"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


class ChatbotResponse:
    """Structured response from the chatbot"""
    def __init__(self, message: str, is_error: bool = False, timestamp: Optional[str] = None):
        self.message = message
        self.is_error = is_error
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")


class FitProChatbot:
    """AI-powered fitness chatbot for FitPro app"""
    
    # Default fitness-related responses when API is not available
    DEFAULT_RESPONSES = {
        "hello": "Hi there! I'm your fitness assistant. Ask me about workouts, nutrition, or fitness tips!",
        "hi": "Hello! Welcome to FitPro. How can I help you today?",
        "how are you": "I'm doing great! Ready to help you achieve your fitness goals!",
        "help": "I can help you with:\n• Workout advice\n• Nutrition tips\n• Motivation\n• Fitness goals\n• Exercise techniques\nJust ask away!",
        "steps": "Great question! A healthy daily step goal is typically 10,000 steps, but any activity is beneficial. Start where you are and gradually increase!",
        "calories": "Daily calorie needs vary by person. As a rough estimate: sedentary = 1,800-2,000, active = 2,200-2,800. Combine with exercise for best results!",
        "workout": "Popular workouts include: walking, running, cycling, HIIT, strength training, yoga, and sports. Pick what you enjoy!",
        "motivation": "Remember: every step counts! Consistency beats perfection. Celebrate small wins and keep moving forward!",
        "tired": "Rest is important for recovery! Make sure you're getting 7-9 hours of sleep and staying hydrated.",
    }
    
    def __init__(self, api_key: Optional[str] = None, backend_url: Optional[str] = None):
        """
        Initialize the chatbot
        
        Args:
            api_key: Deprecated - no longer used
            backend_url: URL of the FitPro backend server (e.g., https://fitpro-backend.render.com)
        """
        self.api_key = api_key
        self.backend_url = backend_url or "https://fitpro-backend.onrender.com"  # Default backend
        self.use_api = False
        self.client = None
        self.model = None
        self.chat_history: List[Dict] = []
        self.system_prompt = """You are a friendly and knowledgeable fitness assistant for the FitPro app. 
You help users with:
- Fitness advice and workout recommendations
- Nutrition and calorie information
- Motivation and goal-setting
- Exercise technique and form
- Recovery and rest advice

Be concise, friendly, and encouraging. Keep responses to 2-3 sentences unless more detail is requested.
If the question is not fitness-related, politely redirect to fitness topics."""
        
        # Test backend connection
        self._test_backend_connection()
    
    def _test_backend_connection(self):
        """Test if backend is reachable"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                self.use_api = True
                print("[INFO] Connected to FitPro backend")
            else:
                print("[WARN] Backend returned non-200 status")
        except Exception as e:
            print(f"[WARN] Could not connect to backend: {e}. Using fallback responses.")
    
    def get_response(self, user_message: str) -> ChatbotResponse:
        """
        Get a response to a user message
        
        Args:
            user_message: The user's input message
            
        Returns:
            ChatbotResponse object with the assistant's response
        """
        if not user_message.strip():
            return ChatbotResponse("Please type a message to get started!")
        
        # Check internet connection
        has_internet = check_internet_connection()
        
        try:
            if self.use_api and has_internet:
                return self._get_api_response(user_message)
            elif self.use_api and not has_internet:
                return ChatbotResponse("❌ No internet connection. Unable to reach server. Please check your connection.")
            else:
                return self._get_fallback_response(user_message)
        except Exception as e:
            print(f"[ERROR] Chatbot error: {e}")
            if not has_internet:
                return ChatbotResponse("❌ No internet connection.")
            return ChatbotResponse(
                f"Oops! Something went wrong. Try again in a moment.",
                is_error=True
            )
    
    def _get_api_response(self, user_message: str) -> ChatbotResponse:
        """Get response using FitPro Backend"""
        try:
            # Call backend API
            response = requests.post(
                f"{self.backend_url}/chat",
                json={"message": user_message},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    assistant_message = data.get("message", "No response received")
                    return ChatbotResponse(assistant_message)
                else:
                    return ChatbotResponse(data.get("message", "Backend error"))
            else:
                return ChatbotResponse(f"❌ Backend error: {response.status_code}")
        
        except requests.Timeout:
            return ChatbotResponse("❌ Request timeout. Please check your internet connection.")
        except Exception as e:
            print(f"[ERROR] Backend request error: {e}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message: str) -> ChatbotResponse:
        """Get response using predefined fitness responses"""
        msg_lower = user_message.lower().strip()
        
        # Check for exact matches
        for key, response in self.DEFAULT_RESPONSES.items():
            if key in msg_lower:
                return ChatbotResponse(response)
        
        # Generic fitness response
        generic_responses = [
            "sorry bro app is down"
        ]
        
        import random
        response = random.choice(generic_responses)
        return ChatbotResponse(response)
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


class ChatMessage:
    """Represents a single chat message"""
    def __init__(self, text: str, is_user: bool, timestamp: Optional[str] = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
