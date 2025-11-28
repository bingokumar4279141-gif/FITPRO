"""
AI Chatbot Module for FitPro
Handles chat interactions with Google's Gemini API or fallback to local responses
"""

import json
from datetime import datetime
from typing import Optional, List, Dict
import socket


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
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot
        
        Args:
            api_key: Optional Google Gemini API key. If not provided, uses fallback responses
        """
        self.api_key = api_key
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
        
        # Try to initialize Google Gemini API
        if api_key:
            self._init_gemini(api_key)
            if not self.use_api:
                print("[INFO] API key provided but initialization failed. Using fallback mode.")
        else:
            print("[INFO] No API key provided. Using fallback responses.")
    
    def _init_gemini(self, api_key: str):
        """Initialize Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.use_api = True
            print("[INFO] Gemini API initialized successfully")
        except ImportError:
            print("[WARN] google-generativeai not installed. Using fallback responses.")
        except Exception as e:
            print(f"[WARN] Failed to initialize Gemini API: {e}. Using fallback responses.")
    
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
            if self.use_api and self.model and has_internet:
                return self._get_api_response(user_message)
            elif self.use_api and self.model and not has_internet:
                return ChatbotResponse("❌ No internet connection. Unable to reach AI. Please check your connection.")
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
        """Get response using Google Gemini API with conversation history"""
        try:
            # Add user message to history
            self.chat_history.append({
                "role": "user",
                "parts": [user_message]
            })
            
            # Start with system prompt as first message
            if not self.chat_history or (len(self.chat_history) > 0 and self.chat_history[0].get("role") != "system"):
                self.chat_history.insert(0, {
                    "role": "user",
                    "parts": [self.system_prompt]
                })
            
            # Use conversation history for context-aware responses
            response = self.model.generate_content(
                [{"role": msg["role"], "parts": msg["parts"]} for msg in self.chat_history]
            )
            assistant_message = response.text
            
            # Add assistant response to history
            self.chat_history.append({
                "role": "model",
                "parts": [assistant_message]
            })
            
            # Keep only last 20 messages (10 exchanges) to manage token usage
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            return ChatbotResponse(assistant_message)
        
        except Exception as e:
            print(f"[ERROR] API response error: {e}")
            # Fallback to default response
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
            "That's a great question! In general, consistency and listening to your body are key to fitness success.",
            "Great question about fitness! Make sure to stay hydrated, warm up before exercise, and rest between workouts.",
            "Interesting! Remember that everyone's fitness journey is unique. Focus on progress, not perfection!",
            "Good thinking! The best workout is the one you'll actually do. Find what you enjoy!",
            "Nice question! Building a routine that fits your lifestyle is more important than perfection.",
            "That's important! Remember that rest and recovery are just as crucial as the workout itself.",
            "Absolutely! Nutrition plays a huge role in achieving your fitness goals.",
            "Smart thinking! Tracking your progress helps you stay motivated and see improvements over time.",
            "Great mindset! Starting small and building up gradually is the best approach to long-term success.",
            "Exactly! Combining cardio, strength training, and flexibility work gives you a well-rounded fitness routine.",
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
