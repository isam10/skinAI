# utils.py
import google.generativeai as genai

def configure_genai(api_key):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 0.3,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 4096,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

def analyze_skin_image(model, image, prompt_template):
    try:
        response = model.generate_content([prompt_template, image])
        return response.text
    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"

def chat_with_dr_tarannum(model, user_message):
    try:
        response = model.generate_content(user_message)
        # Clean up the response - remove any unwanted characters or formatting
        doctor_response = response.text.strip()
        return doctor_response
    except Exception as e:
        return f"I apologize, but I'm experiencing technical difficulties at the moment. Please try again in a few moments."