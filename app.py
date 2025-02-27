from flask import Flask, request, render_template
import mysql.connector
from googletrans import Translator
import datetime

app = Flask(__name__)

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rout@2001@admin",
    database="dictionary_db"
)
cursor = db.cursor()

# Function to Translate English to Odia
def get_odia_meaning(word):
    try:
        translator = Translator()
        result = translator.translate(word, src="en", dest="or")  # "or" = Odia
        return result.text
    except Exception as e:
        return f"Error: {e}"

# Flask Route for Dictionary
@app.route("/", methods=["GET", "POST"])
def index():
    meaning = None
    history = []

    if request.method == "POST":
        word = request.form["word"].strip().lower()
        
        # Check if the word exists in the database
        cursor.execute("SELECT odia_meaning FROM words WHERE english_word=%s", (word,))
        result = cursor.fetchone()
        
        if result:
            meaning = result[0]
        else:
            # Fetch translation using Google Translate API
            meaning = get_odia_meaning(word)
            if meaning and "Error" not in meaning:
                cursor.execute("INSERT INTO words (english_word, odia_meaning) VALUES (%s, %s)", (word, meaning))
                db.commit()

        # Store the search history
        cursor.execute("INSERT INTO search_history (english_word, odia_meaning) VALUES (%s, %s)", (word, meaning))
        db.commit()

    # Retrieve past search history
    cursor.execute("SELECT english_word, odia_meaning, search_time FROM search_history ORDER BY search_time DESC LIMIT 5")
    history = cursor.fetchall()

    return render_template("index.html", meaning=meaning, history=history)

if __name__ == "__main__":
    app.run(debug=True)
