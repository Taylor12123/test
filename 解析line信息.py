from flask import Flask, request

import json

app = Flask(__name__)


@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    json_data = json.loads(body)
    print(json_data)               # 印出 json_data
    return 'OK'
if __name__ == "__main__":
  app.run()