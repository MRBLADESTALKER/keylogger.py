from flask import Flask, request
import requests

app = Flask(name)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.data.decode('utf-8')
    # Process the data and send to Telegram
    send_to_telegram(data, "@mrbladestalker0093")
    return "Data received", 200

if name == 'main':
    app.run(host='0.0.0.0', port=5000)