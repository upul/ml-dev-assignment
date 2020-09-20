import json
import time

import pytest

from sentiment.app.api import app as flask_app
from sentiment.app.api import load_ml_model
from sentiment.util.config_reader import Config


@pytest.fixture
def app():
    model_path = Config().ModelConfig().read('LOCATION')
    load_ml_model(model_path)
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(app, client):
    res = client.get('/api/v1/health')
    assert res.status_code == 200
    expected = {'message': 'Application is up and running'}
    assert expected == json.loads(res.get_data(as_text=True))


def test_predict_happy_path(app, client):
    data = {"request_id": 1234, "text": "hello",
            "language": "en-US", "encoding_type": "UTF-8"}
    res = client.post('/api/v1/predict',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 200

    res = json.loads(res.get_data(as_text=True))
    assert 'request_id' in res, 'response does not contain request_id'
    assert 'sentiment' in res, 'response does not contain sentiment'
    assert len(res['sentiment']
               ) == 6, 'sentiment array should contain six sentiment types'


def test_predict_missing_request_id(app, client):
    data = {"text": "hello",
            "language": "en-US", "encoding_type": "UTF-8"}
    res = client.post('/api/v1/predict',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 422

    expected = {'message': 'required parameter: request_id is missing'}
    assert expected == json.loads(res.get_data(as_text=True))


def test_predict_missing_text(app, client):
    data = {"request_id": 1234,
            "language": "en-US", "encoding_type": "UTF-8"}
    res = client.post('/api/v1/predict',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 422

    expected = {'message': 'required parameter: text is missing or empty'}
    assert expected == json.loads(res.get_data(as_text=True))


def test_predict_missing_language(app, client):
    data = {"request_id": 1234, "text": "hello",
            "encoding_type": "UTF-8"}
    res = client.post('/api/v1/predict',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 422

    expected = {'message': 'required parameter: language is missing or empty'}
    assert expected == json.loads(res.get_data(as_text=True))


def test_predict_missing_encoding_type(app, client):
    data = {"request_id": 1234, "text": "hello", "language": "en-US"}
    res = client.post('/api/v1/predict',
                      data=json.dumps(data),
                      content_type='application/json')
    assert res.status_code == 422

    expected = {
        'message': 'required parameter: encoding_type is missing or empty'}
    assert expected == json.loads(res.get_data(as_text=True))

def test_statistics_happy_path(app, client):
    # wait more than one min
    time.sleep(65)

    # three calls to health endpoint
    res = client.get('/api/v1/health')
    res = client.get('/api/v1/health')
    res = client.get('/api/v1/health')

    res = client.get('/api/v1/statistics?api=health')
    assert res.status_code == 200
    expected = {'api': 'health', 'number of calls in current minute': 3}
    assert expected == json.loads(res.get_data(as_text=True))

# TODO: (upul) more testing for the statistics end-point
# 1. time span more than one minute 
# 2. current update
# 3. etc. 
