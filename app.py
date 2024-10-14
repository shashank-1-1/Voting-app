from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('voting.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Route to serve the HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to cast a vote
@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    animal = data.get('animal')

    # Validate the animal vote
    if animal not in ['cat', 'dog']:
        return jsonify({'error': 'Invalid animal'}), 400

    # Save the vote in the database
    conn = sqlite3.connect('voting.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO votes (animal) VALUES (?)', (animal,))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Vote for {animal} recorded'})

# Endpoint to get voting results
@app.route('/results', methods=['GET'])
def results():
    conn = sqlite3.connect('voting.db')
    cursor = conn.cursor()
    cursor.execute('SELECT animal, COUNT(*) as count FROM votes GROUP BY animal')
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a dictionary format: {'animal': count}
    results = {row[0]: row[1] for row in rows}
    return jsonify(results)

# Main block to run the application
if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(host='0.0.0.0', port=8080)

