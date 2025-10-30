from datetime import datetime

def test_add_task(client, user):
    client.post('/login', data={'username': 'test', 'password': '123'})
    resp = client.post('/add_modal', data={
        'title': '写代码', 'priority': 1, 'description': '测试',
        'start_time': '2025-11-01T09:00', 'end_time': '2025-11-01T18:00'
    }, follow_redirects=False)
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['ok'] is True