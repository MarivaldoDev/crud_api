from security import create_access_token, SECRET_KEY, ALGORITHM
from jwt import decode


def test_jwt():
    data = {"sub": "test"}
    token = create_access_token(data)
    
    result = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert result['sub'] == data['sub']
    assert result['exp']