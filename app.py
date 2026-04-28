from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask Demo v1.4\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
