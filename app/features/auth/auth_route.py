"""
Authentication API endpoints - login and registration only
"""

from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from app.features.auth.auth_schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.features.users.user_repository import UserRepository
from app.features.auth.jwt import create_access_token
from app.features.auth.auth_utils import hash_password, verify_password
from app.core.utils import get_logger, ValidationException

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(request: Request, user_data: UserCreate):
    """Register a new user."""
    try:
        logger.info(f"Registering new user: {user_data.username}")
        repo = UserRepository()
        
        # Check if user already exists
        if repo.get_by_username(user_data.username):
            logger.warning(f"Registration failed: username exists: {user_data.username}")
            raise ValidationException("Username already exists")

        # allow admin to set role via payload
        user = repo.create_user(
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            role=user_data.role or "user"
        )
        user_response = UserResponse.model_validate(user)
        
        # Create token for the new user

        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=user_response.model_dump(mode="json"),
        )
    except ValidationException as e:
        logger.warning(f"Registration failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Registration failed"}
        )


@router.post("/login")
def login(login_data: UserLogin):
    """Login user and return access token."""
    try:
        logger.info(f"Login attempt: {login_data.username}")
        repo = UserRepository()

        # Authenticate user
        user = repo.get_by_username(login_data.username)
        if not user:
            logger.warning(f"Authentication failed: user not found: {login_data.username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"}
            )

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive: {login_data.username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"}
            )

        if not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password: {login_data.username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"}
            )

        # Update last login
        repo.update_last_login(user.id)
        logger.info(f"User authenticated: {login_data.username}")


        # Create token
        access_token = create_access_token(data={"sub": user.id,"username": user.username,"role": user.role})

        logger.info(f"User logged in: {user.username}")
        user_response = UserResponse.model_validate(user)
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=token_response.model_dump(mode="json"),
            headers={"X-Access-Token": access_token}

        )

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Login failed"}
        )
