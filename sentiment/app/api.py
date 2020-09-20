import argparse

import joblib
from flask import Flask, jsonify, request

from sentiment.util.config_reader import Config
from sentiment.util.exceptions import (SentimentModelException,
                                       SentimentStatException)
from sentiment.util.logging import Logger
from sentiment.util.request_counter import RequestStatistics

app = Flask(__name__)
model = None

# This is a simple in-memory cache to calculate API calling statistics. 
# Currently, this is just a PoC and this will not scale well for the actual production system.
# Maybe we want to reimplement this using a reliable persistent storage medium such as a key-value database. 
api_statistics = RequestStatistics()

logger = Logger()


@app.route('/api/v1/health', methods=['GET'])
def do_health_check():
    """This is a simple application health checking endpoint

    Returns:
        json: The message indicates the status of the application
    """
    api_statistics.register_new_call('health')
    return jsonify({'message': 'Application is up and running'}), 200


@app.route('/api/v1/predict', methods=['POST'])
def do_prediction():
    """This is our prediction REST endpoint.

    Returns:
        json: The message that contains sentiment type and score
    """
    api_statistics.register_new_call('predict')

    try:
        json = request.json
        if not json:
            message = 'can not decode json from post body. ' + \
                'probably you need to send Content-Type: application/json header'
            return jsonify({'message': message}), 422

        if ('request_id' not in json):
            return jsonify({'message': 'required parameter: request_id is missing'}), 422

        if ('text' not in json) or (len(json['text']) == 0):
            return jsonify({'message': 'required parameter: text is missing or empty'}), 422

        if ('language' not in json) or (len(json['language']) == 0):
            return jsonify({'message': 'required parameter: language is missing or empty'}), 422

        if ('encoding_type' not in json) or (len(json['encoding_type']) == 0):
            return jsonify({'message': 'required parameter: encoding_type is missing or empty'}), 422

        prediction = model.predict([json['text'].strip()])
        return _build_response_json(json['request_id'],
                                    json['language'], prediction), 200

    except Exception as ex:
        message = f'internal error has occurred. message: {ex}'
        logger.error(message)
        return jsonify({'message': message}), 500


@app.route('/api/v1/statistics', methods=['GET'])
def do_statistics():
    if 'api' in request.args:
        api = request.args.get('api')

        num_calls = api_statistics.num_calls_per_minute(api)
        return jsonify({'api': api, 'number of calls in current minute': num_calls}), 200

    return jsonify({'message': 'URL incorrect, correct format: /api/v1/statistics?api=<api_name>'}), 422


def load_ml_model(path):
    """Simple utility method for loading the trained ML model

    Args:
        path (str): location of the trained model

    Raises:
        SentimentModelException: if we can't load the model into memory we throw this exception
    """
    global model
    try:
        model = joblib.load(path)
    except Exception as ex:
        message = f'An exception has occurred while loading the model: {ex}'
        logger.error(message)
        raise SentimentModelException(message)


def _build_response_json(request_id, language, predictions):
    """Simple utility for creating the JSON response

    Args:
        request_id (str): request id
        language (str): language indicates in the request
        predictions (numpy array): prediction array received from ML model

    Returns:
        json: response encoded as a JSON object.
    """

    json = {
        "request_id": request_id,
        "sentiment": [
            {
                "sentiment_type": "toxic",
                "sentiment_score": float(predictions[0][0])
            },
            {
                "sentiment_type": "severe_toxic",
                "sentiment_score": float(predictions[0][1])
            },
            {
                "sentiment_type": "obscene",
                "sentiment_score": float(predictions[0][2])
            },
            {
                "sentiment_type": "threat",
                "sentiment_score": float(predictions[0][3])
            },
            {
                "sentiment_type": "insult",
                "sentiment_score": float(predictions[0][4])
            },
            {
                "sentiment_type": "identity_hate",
                "sentiment_score": float(predictions[0][5])
            }
        ],
        "language": language
    }
    return jsonify(json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Homebrew ML model serving server')
    parser.add_argument(
        '--port', help='The port on which Flask is running', required=True)
    parser.add_argument(
        '--mode', help='The mode the Flak server is running. Possible options: DEV, TEST, and DEPLOY', required=True)
    args = vars(parser.parse_args())

    logger.info(
        f"Flask will be running in {args['mode']} mode on {args['port']} port.")

    model_path = Config().ModelConfig().read('LOCATION')
    logger.info(f'loading model from: {model_path}')
    load_ml_model(model_path)

    app.run(host='0.0.0.0', port=args['port'],
            debug=False if args['mode'] == 'DEPLOY' else True)
