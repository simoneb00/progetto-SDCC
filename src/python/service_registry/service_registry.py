import json

from flask import Flask, request

app = Flask(__name__)


@app.route('/service-registry', methods=['GET'])
def request_handler():
    country = request.args.get('country')
    with open('routing.json', 'r') as f:
        routing_data = json.load(f)
    try:
        port_number = routing_data[country]
        return_data = {'port_number': port_number}
    except KeyError:
        return json.dumps("No data available for this country"), 404

    return json.dumps(return_data), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
