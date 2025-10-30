def test_register_login_logout(client):
    # 注册
    resp = client.post('/register', data={
        'username': 'u1', 'email': 'u1@mail.com',
        'password': '123456', 'confirm': '123456'   # ≥6 位
    }, follow_redirects=True)
    text = resp.get_data(as_text=True)
    assert '注册成功' in text          # 中文 OK

    # 登录
    resp = client.post('/login', data={'username': 'u1', 'password': '123456'}, follow_redirects=True)
    text = resp.get_data(as_text=True)
    assert 'Hi, u1' in text

    # 退出
    resp = client.get('/logout', follow_redirects=True)
    text = resp.get_data(as_text=True)
    assert '登录' in text