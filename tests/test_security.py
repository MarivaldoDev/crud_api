from security import create_access_token, settings
from jwt import decode


def test_jwt():
    data = {"sub": "test"}
    token = create_access_token(data)
    
    result = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert result['sub'] == data['sub']
    assert result['exp']