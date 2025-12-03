# tests/test_routers.py
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from main import app # Assuming app.main includes the router
from app.features.users.user_repository import UserRepository

client = TestClient(app)
AUTH_MIDDLEWARE_DISPATCH_TARGET = 'app.middleware.auth_middleware.AuthMiddleware.dispatch'


# --- ASYNCHRONOUS MOCK FUNCTION ---
# This is the replacement for the original dispatch method.
# It takes the necessary arguments and simply calls the next handler (the router).
async def mock_auth_middleware_dispatch(self, request, call_next):
    """Bypasses authentication logic and immediately passes control to the router."""
    
    request.state.user = {"id": 1, "username": "TestUser", "role": "user"}
    response = await call_next(request)
    return response



# ----------------------------------------------------
# Test Case 1: Get User by Id
# ----------------------------------------------------
@patch('app.features.users.users_route.UserRepository') 
@patch(AUTH_MIDDLEWARE_DISPATCH_TARGET, new=mock_auth_middleware_dispatch)
def test_get_user(MockUserRepository):
    # ARRANGE 1: Get the mock instance that represents the actual repository object (repo = ItemRepository())
    mock_repo_instance = MockUserRepository.return_value 
    
    expected_db_return = {
  "username": "JDOE",
  "id": 3,
  "is_active": True,
  "role": "user",
  "last_login": None,
  "created_at": "2025-12-03T20:28:33.686708",
  "updated_at": "2025-12-03T20:28:33.686708"
}
    
    # ARRANGE 2: Define what the mocked method should return
    mock_repo_instance.get_by_id.return_value = expected_db_return
    
    # ACT: Send a valid request
    targetId=1
    response = client.get(
       f"api/v1/users/{targetId}"
    )
    
    # ASSERT 1: Check HTTP response
    assert response.status_code == 200
    assert response.json()==expected_db_return
    # ASSERT 2: Verify the router called the mock repo correctly
    MockUserRepository.assert_called_once()
    mock_repo_instance.get_by_id.assert_called_once_with(1)


# ----------------------------------------------------
# Test Case 2: Get All users
# ----------------------------------------------------
@patch('app.features.users.users_route.UserRepository') 
@patch(AUTH_MIDDLEWARE_DISPATCH_TARGET, new=mock_auth_middleware_dispatch)
def test_get_users(MockUserRepository):
    # ARRANGE 1: Get the mock instance that represents the actual repository object (repo = ItemRepository())
    mock_repo_instance = MockUserRepository.return_value 
    
    expected_db_return = [{
  "username": "JDOE",
  "id": 3,
  "is_active": True,
  "role": "user",
  "last_login": None,
  "created_at": "2025-12-03T20:28:33.686708",
  "updated_at": "2025-12-03T20:28:33.686708"
},
{
  "username": "JANEDOE",
  "id": 4,
  "is_active": True,
  "role": "user",
  "last_login": None,
  "created_at": "2025-12-03T20:28:33.686708",
  "updated_at": "2025-12-03T20:28:33.686708"
}]
    
    # ARRANGE 2: Define what the mocked method should return
    mock_repo_instance.get_active_users.return_value = expected_db_return
    
    # ACT: Send a valid request
    targetId=1
    response = client.get(
       f"api/v1/users"
    )
    
    # ASSERT 1: Check HTTP response
    assert response.status_code == 200
    assert response.json()==expected_db_return
    # ASSERT 2: Verify the router called the mock repo correctly
    MockUserRepository.assert_called_once()
    mock_repo_instance.get_active_users.assert_called_once_with()




