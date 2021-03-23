import credentials
import requests
from flask import Flask, request
app = Flask(__name__)

ACESS_TOKEN = 'EAADzIkX32oYBAOVT2R7VXC2wyH4HM1jLzfuPaWYcpCn4P58NWyuzzaJuxMVtNeVrOTOk42NzWlAuJedXMR46PhkhAXu79ieZBu4aFqkrdPPMaJbkkMhaQFHyLxJDlRkXdEawMrroqLNaRg59g1qRWkznC1GWyCuYZCPX1pI5pEw1Dbc9s0dWOZAFAS92OQZD'
TOKEN = 'tokentest'

#@app.route('/')
#def hello_world():
#    return 'Hello, World!'



# Adds support for GET requests to our webhook
@app.route('/',methods=['GET'])
def webhook_authorization():
    verify_token = request.args.get("hub.verify_token")
    # Check if sent token is correct
    OUT = open("output.txt", 'w')
    OUT.write(str(verify_token))
    if verify_token == TOKEN:
        # Responds with the challenge token from the request
        return request.args.get("hub.challenge")
    return 'Unable to authorize.'


@app.route("/", methods=['POST'])
def webhook_handle():
    data = request.get_json()
    message = data['entry'][0]['messaging'][0]['message']
    sender_id = data['entry'][0]['messaging'][0]['sender']['id']
    if message['text']:
        request_body = {
                'recipient': {
                    'id': sender_id
                },
                'message': {"text":"hello, world!"}
            }
        response = requests.post('https://graph.facebook.com/v5.0/me/messages?access_token='+ACESS_TOKEN,json=request_body).json()
        return response
    return 'ok'

if __name__ == "__main__":
    app.run(threaded=True, port=5000)