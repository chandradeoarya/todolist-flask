from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    """homepage"""
    return "Welcome to to-do API Service"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)