from app.config import get_config


def test_create_feedback_bad_request_data(test_client):
    # arrange
    missing = ["desc", "page", "browser", "browser_version", "width", "height", "os"]
    data = {
        "title": "A bug has been found!",
    }

    # act
    response = test_client.post(f'{get_config().BASE_PATH}/feedback', json=data)

    # assert
    assert response.status_code == 422
    for idx, detail in enumerate(response.json()['detail']):
        assert missing[idx] in detail['loc']
        assert detail['msg'] == 'field required'
        assert detail['type'] == 'value_error.missing'


def test_create_feedback_failure(test_client, monkeypatch):
    # arrange
    data = {
        "title": "A bug has been found!",
        "desc": "The bug is really bad!",
        "page": "/path/to/page",
        "browser": "firefox",
        "browser_version": "88.0",
        "width": "1000",
        "height": "800",
        "os": "unix"
    }
    monkeypatch.setenv('GITHUB_ACCESS_TOKEN', '')

    # act
    response = test_client.post(f'{get_config().BASE_PATH}/feedback', json=data)

    # assert
    assert response.status_code == 500
    assert response.json()['detail'] == 'Error creating user feedback.'

    # assert isinstance(exc_info.value, HTTPException)
    # assert exc_info.value.status_code == 500
    # assert exc_info.value.detail == "Error creating user feedback."
