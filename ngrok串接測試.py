from flask import Flask

app = Flask(__name__)

@app.route("/", methods=['POST'])
def home():
    return "<h1>hello world</h1>"

app.run()