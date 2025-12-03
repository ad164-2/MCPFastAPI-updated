# tests/test_repository.py (or conftest.py)
import pytest
from unittest.mock import patch, Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.features.users.user_entity import User
from app.features.users.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError
from app.core.base.entity import Base

# Fixture to create an in-memory SQLite database and tear it down
@pytest.fixture
def db_session():
    # 1. SETUP: Create an in-memory SQLite engine
    # 'sqlite:///:memory:' means the DB exists only in RAM for the test duration
    engine = create_engine("sqlite:///:memory:") 
    
    # 2. SETUP: Create all tables defined in Base (our Item table)
    Base.metadata.create_all(engine)
    
    # 3. SETUP: Create a session
    session = Session(engine)

    # 4. YIELD: Pass the session to the test function
    yield session 

    # 5. TEARDOWN: Close and clean up the session/engine
    session.close()
    Base.metadata.drop_all(engine)
    

# ----------------------------------------------------
# Actual Test Cases
# ----------------------------------------------------

@patch('app.core.base.repository.SessionLocal') 
def test_create_and_get_by_username(MockSessionLocal, db_session: Session):
    MockSessionLocal.return_value = db_session
    repo = UserRepository() 

    # ACT: Use the repository method (which uses the injected test session)
    new_user = repo.create_user(username="TestUser", password_hash="dfdsfsdfsd",role="user")

    # ASSERT 1: Verify the session was called (i.e., the BaseRepo ran its __init__)
    MockSessionLocal.assert_called_once()
    
    # ASSERT 2: Verify the user was written to the test database
    retrieved_user = repo.get_by_username(username="TestUser")
    assert retrieved_user.username == "TestUser"
    assert retrieved_user.role == "user"
    assert retrieved_user.password_hash == "dfdsfsdfsd"
    assert retrieved_user.is_active==True


@patch('app.core.base.repository.SessionLocal') 
def test_get_by_incorrect_username(MockSessionLocal, db_session: Session):
    
    MockSessionLocal.return_value = db_session
    
    repo = UserRepository() 

    # ASSERT 1: Verify using Incorrect User doesnt exist
    retrieved_item = repo.get_by_username(username="TestUser2")

    MockSessionLocal.assert_called_once()
    
    assert retrieved_item is None


@patch('app.core.base.repository.SessionLocal') 
def test_Activate_DeActivate_User(MockSessionLocal, db_session: Session):
    #
    MockSessionLocal.return_value = db_session
    repo = UserRepository() 

    # ACT: Use the repository method (which uses the injected test session)
    new_user = repo.create_user(username="TestUser2", password_hash="dfdsfsdfsd",role="user")

    # ASSERT 1: Verify the session was called (i.e., the BaseRepo ran its __init__)
    MockSessionLocal.assert_called_once()
    
    # ASSERT 2: Verify the user was written to the test database
    retrieved_user = repo.get_by_username(username="TestUser2")
    user_id=retrieved_user.id
    assert retrieved_user.username == "TestUser2"
    assert retrieved_user.role == "user"
    assert retrieved_user.password_hash == "dfdsfsdfsd"
    assert retrieved_user.is_active==True

    #Deactivate the User
    updated_user = repo.deactivate_user(user_id)

    retrieved_user = repo.get_by_username(username="TestUser2")
    # ASSERT 3: Verify the user was deactivated
    assert retrieved_user.is_active==False

    #Activate the User Again
    updated_user = repo.activate_user(user_id)

    retrieved_user = repo.get_by_username(username="TestUser2")
    # ASSERT 4: Verify the user is reactivated
    assert retrieved_user.is_active==True


