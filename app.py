from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    """homepage"""
    return "Welcome to to-do API Service"

@app.route('/todos', methods=['GET'])
def get_tasks():
    """api route to retrieve all tasks"""
    return jsonify({ 'tasks': [{'name': 'get milk'}, {'name': 'get bread'}]})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
