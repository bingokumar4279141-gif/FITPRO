import os

# Set API key from environment
api_key = os.environ.get("FITPRO_GEMINI_API_KEY")

if not api_key:
    print("✗ API Key not found in environment variable FITPRO_GEMINI_API_KEY")
    exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    print("Testing Gemini API...")
    response = model.generate_content("Say 'Hello from FitPro' in one sentence.")
    
    print("✓ API Test Success!")
    print("Response:", response.text[:150])
    
except ImportError:
    print("✗ google-generativeai not installed. Run: pip install google-generativeai")
except Exception as e:
    print("✗ API Test Failed:", str(e)[:200])
