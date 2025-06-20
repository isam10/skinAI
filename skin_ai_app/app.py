from flask import Flask, render_template, request, redirect, url_for, session
from utils import configure_genai, analyze_skin_image, chat_with_dr_tarannum
from PIL import Image
import os
import time
from datetime import datetime
from werkzeug.utils import secure_filename

# --- Setup ---
app = Flask(__name__)
app.secret_key = "your-secret-key"
UPLOAD_FOLDER = "static/uploaded"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Gemini Setup ---
GEMINI_API_KEY = "AIzaSyBzekQd-7LWgs2hFQ79QcDyWvWXPdCZayU"
model = configure_genai(GEMINI_API_KEY)

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    diagnosis = None
    image_path = None
    
    if request.method == "POST":
        if 'image' in request.files:
            file = request.files["image"]
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                image = Image.open(filepath)
                prompt = """
                Analyze this skin image.
                Tell me only:
                1. Whether it looks like a malignant condition.
                2. give the name of the disease if possible.
                3. Short reason why you think so
                4. Recommended next steps
                Format this as a professional medical assessment. use proper spacing leave lines it between whereever required. start every sentence on a new line .
                
                """
                diagnosis = analyze_skin_image(model, image, prompt)
                image_path = '/' + filepath
                
                # Save the diagnosis to the session to pass to the chat page
                session["diagnosis"] = diagnosis
                session["image_path"] = image_path
                
                # Clear the chat history whenever a new image is uploaded
                if "chat_history" in session:
                    session.pop("chat_history")
    
    return render_template("index.html", diagnosis=diagnosis, image_path=image_path)
@app.route("/chat", methods=["GET", "POST"])
def chat():
    # Initialize chat history if it doesn't exist
    if "chat_history" not in session:
        now = datetime.now().strftime("%I:%M %p").lstrip('0')
        session["chat_history"] = [
            ("Dr. Tarannum", "Hello! I'm Dr. Tarannum, a dermatological specialist. How can I assist you with your skin concerns today?", now)
        ]
    
    diagnosis = session.get("diagnosis", "No diagnosis yet.")
    image_path = session.get("image_path", None)
    
    # Handle image upload from chat page
    if request.method == "POST" and 'image' in request.files:
        file = request.files["image"]
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            image = Image.open(filepath)
            prompt = """
            Analyze this skin image.
            Tell me only:
            1. Whether it looks like a malignant condition 
            2. Short reason why you think so
            3. Recommended next steps
            Format this as a professional medical assessment.
            """
            diagnosis = analyze_skin_image(model, image, prompt)
            image_path = '/' + filepath
            
            # Save the diagnosis to the session
            session["diagnosis"] = diagnosis
            session["image_path"] = image_path
            
            # Clear chat history and add new greeting with diagnosis
            now = datetime.now().strftime("%I:%M %p").lstrip('0')
            session["chat_history"] = [
                ("Dr. Tarannum", f"I've analyzed your new image. {diagnosis} How can I help you further?", now)
            ]
            
            return redirect(url_for('chat'))
    
    # Handle text message
    elif request.method == "POST" and 'user_input' in request.form:
        user_message = request.form["user_input"]
        if user_message.strip():
            now = datetime.now().strftime("%I:%M %p").lstrip('0')
            session["chat_history"].append(("You", user_message, now))
            
            # Generate doctor's response
            prompt = f"""
            You are Dr. Tarannum, a friendly and professional dermatologist.
            Previous diagnosis for the patient: {diagnosis}
            
            User says: "{user_message}"
            
            Respond as Dr. Tarannum - be professional but warm. Keep responses concise
            but informative. Refer to the diagnosis when relevant. please generate and display refferals whenever they enter city.
            referrals format should be name and number.
            referral format: "Dr. [Name], [Phone Number]"
            """
            reply = chat_with_dr_tarannum(model, prompt)
            now = datetime.now().strftime("%I:%M %p").lstrip('0')
            session["chat_history"].append(("Dr. Tarannum", reply, now))
            
            # Store in session
            session.modified = True
    
    return render_template("chat.html", chat_history=session.get("chat_history", []), image_path=image_path)

if __name__ == "__main__":
    app.run(debug=True)