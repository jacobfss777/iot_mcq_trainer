from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    with open(os.path.join(os.path.dirname(__file__), 'questions.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    flat = []
    for topic in data:
        for q in topic['questions']:
            q['topic'] = topic['topicName']
            q['answer'] = q.pop('correctAnswer', q.get('answer'))
            flat.append(q)
    return jsonify(flat)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
