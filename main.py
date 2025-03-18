from flask import Flask, render_template, url_for
# from chat import chat_bp
from gemini_api import gemini_api_bp
# import requests
# response = requests.get("https://generativelanguage.googleapis.com/...", verify=False)


app = Flask(__name__)

# call out the other route() from any file
# app.register_blueprint(chat_bp, url_prefix="")
app.register_blueprint(gemini_api_bp, url_prefix="")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, port=8080)  # Runs on port 8080 instead of 5000
