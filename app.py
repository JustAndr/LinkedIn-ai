from flask import Flask, request, render_template_string
import requests
import dotenv
import os
dotenv.load_dotenv()

app = Flask(__name__)

# === STEP 1: PASTE YOUR GROQ API KEY HERE ===
# Go to: https://console.groq.com → API Keys → Create New → Copy
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_placeholder_for_testing")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def generate_post(idea, tone="professional"):
    prompt = f"""
    Write a high-engagement LinkedIn post (under 250 words) about: "{idea}"
    Tone: {tone}
    Structure:
    1. Hook (bold claim or question)
    2. 1-sentence insight
    3. CTA: "Save this if..."
    Use 2 emojis. End with 3 hashtags.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-8b-instant",  # Free, fast, & updated (replacement for deprecated model)
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Connection failed: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def home():
    post = None
    error = None

    if request.method == 'POST':
        idea = request.form['idea'].strip()
        tone = request.form['tone']

        if not idea:
            error = "Please enter an idea."
        else:
            post = generate_post(idea, tone)

    # === HTML PAGE (Beautiful & Mobile-Friendly) ===
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LinkedIn AI Post Generator</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
            body { font-family: 'Inter', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; color: #1a1a1a; }
            .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
            h1 { font-size: 28px; text-align: center; color: #0077b5; margin-bottom: 10px; }
            p { text-align: center; color: #666; margin-bottom: 25px; }
            input, select, button { width: 100%; padding: 14px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; font-size: 16px; }
            select { background: white; }
            button { background: #0077b5; color: white; border: none; font-weight: 600; cursor: pointer; transition: 0.2s; }
            button:hover { background: #005a8c; }
            .result { margin-top: 25px; padding: 20px; background: #f0f7ff; border-left: 5px solid #0077b5; border-radius: 8px; white-space: pre-wrap; font-size: 16px; line-height: 1.6; }
            .error { color: #d32f2f; text-align: center; font-weight: 600; }
            footer { text-align: center; margin-top: 40px; color: #888; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LinkedIn AI Post Generator</h1>
            <p>Turn any idea into a viral LinkedIn post in seconds.</p>

            <form method="POST">
                <input type="text" name="idea" placeholder="Your idea (e.g. I launched a SaaS)" required>
                <select name="tone">
                    <option value="professional">Professional</option>
                    <option value="witty">Witty</option>
                    <option value="bold">Bold</option>
                    <option value="humble">Humble</option>
                </select>
                <button type="submit">Generate Post</button>
            </form>

            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}

            {% if post %}
            <div class="result">{{ post }}</div>
            <p style="text-align:center; margin-top:15px;">
                <small>Copy & post to LinkedIn</small>
            </p>
            {% endif %}

            <footer>
                Built with <3 using Groq + Flask • <a href="https://x.com/yourusername" target="_blank">Follow updates</a>
            </footer>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, post=post, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)