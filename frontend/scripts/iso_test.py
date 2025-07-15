from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! This is a basic Flask test."

@app.route('/test')
def test():
    return "Test page works!"

if __name__ == "__main__":
    print("Starting basic Flask test...")
    app.run(debug=True, host='127.0.0.1', port=5000)