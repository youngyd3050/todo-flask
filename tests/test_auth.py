def test_register_login_logout(client):
    # 注册
    resp = client.post('/register', data={
        'username': 'u1', 'email': 'u1@mail.com',
        'password': '123', 'confirm': '123'
    }, follow_redirects=True)
    assert b'注册成功' in resp.data

    # 登录
    resp = client.post('/login', data={'username': 'u1', 'password': '123'}, follow_redirects=True)
    assert b'Hi, u1' in resp.data

    # 退出
    resp = client.get('/logout', follow_redirects=True)
    assert b'登录' in resp.data