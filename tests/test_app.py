import os
import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/ingest"
SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), 'sample.pdf')
SAMPLE_METADATA = {"author": "Aryan Raj Jaiswal", "category": "test"}

def test_ingest_document():
    with open(SAMPLE_PDF_PATH, 'rb') as file:
        files = {'file': ('sample.pdf', file, 'application/pdf')}
        data = {'metadata': str(SAMPLE_METADATA)}
        response = requests.post(BASE_URL, files=files, data=data)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['message'] == 'Document ingested successfully'
        assert 'document_id' in response_json

def test_invalid_metadata():
    with open(SAMPLE_PDF_PATH, 'rb') as file:
        files = {'file': ('sample.pdf', file, 'application/pdf')}
        data = {'metadata': 'invalid_metadata'}
        response = requests.post(BASE_URL, files=files, data=data)
        assert response.status_code == 400
        response_json = response.json()
        assert 'detail' in response_json

def test_missing_file():
    response = requests.post(BASE_URL, data={'metadata': str(SAMPLE_METADATA)})
    assert response.status_code == 422
    response_json = response.json()
    assert response_json['detail'][0]['msg'] == 'Field required'
    assert response_json['detail'][0]['loc'] == ['body', 'file']

def test_missing_metadata():
    with open(SAMPLE_PDF_PATH, 'rb') as file:
        files = {'file': ('sample.pdf', file, 'application/pdf')}
        response = requests.post(BASE_URL, files=files)
        assert response.status_code == 422
        response_json = response.json()
        assert response_json['detail'][0]['msg'] == 'Field required'
        assert response_json['detail'][0]['loc'] == ['body', 'metadata']
