from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Store highest score in memory (resets when server restarts)
highest_score = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/score', methods=['GET'])
def get_score():
    return jsonify({'highest_score': highest_score})

@app.route('/api/score', methods=['POST'])
def save_score():
    global highest_score
    data = request.get_json()
    new_score = data.get('score', 0)
    
    if new_score > highest_score:
        highest_score = new_score
        
    return jsonify({'highest_score': highest_score, 'success': True})

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)
