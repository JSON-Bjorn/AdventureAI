# External imports
from functools import wraps
from typing import Callable, Optional, Dict, Any
import time
from datetime import datetime
from fastapi import HTTPException, Request, status, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from uuid import UUID

# Internal imports
from app.api.logger.logger import get_logger
from app.api.v1.endpoints.token_validation import (
    get_token,
    validate_token,
)
from app.api.v1.database.models import RateLimit
from app.db_setup import get_db

# Logger
logger = get_logger("app.api.endpoints.rate_limiting")

# For hiding the Authorization header in Swagger UI
authorization_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_rate_limit_key(
    request: Request,
    user_id: Optional[UUID] = None,
    endpoint_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates a rate limit key based on user identity (if authenticated) or IP.

    Args:
        request: The FastAPI request object
        user_id: User ID if authenticated, None otherwise
        endpoint_path: The endpoint path (default: request.url.path)

    Returns:
        Dict with rate limit key information:
        - user_id: UUID or None
        - ip_address: String or None
        - endpoint_path: String
    """
    # Get client IP
    client_ip = request.client.host

    # Get endpoint path, defaulting to the request path
    if not endpoint_path:
        endpoint_path = request.url.path

    # Create rate limit key dict
    if user_id:
        # For authenticated users, use user_id
        return {
            "user_id": user_id,
            "ip_address": None,
            "endpoint_path": endpoint_path,
        }
    else:
        # For unauthenticated users, use IP address
        return {
            "user_id": None,
            "ip_address": client_ip,
            "endpoint_path": endpoint_path,
        }


def check_and_update_rate_limit(
    db: Session, key: Dict[str, Any], limit: int, window_seconds: int = 60
) -> Dict[str, Any]:
    """
    Checks if a request exceeds the rate limit and updates the database.
    This function handles cleaning up old timestamps and adding the new timestamp
    if the request is under the limit.

    Args:
        db: Database session
        key: Rate limit key dictionary with user_id/ip_address and endpoint_path
        limit: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds

    Returns:
        Dict with rate limit information:
        - exceeded: Whether the rate limit was exceeded
        - reset_time: Time until the rate limit resets (in seconds)
        - total: Total limit
        - remaining: Remaining requests allowed
    """
    current_time = int(time.time())
    cutoff_time = current_time - window_seconds

    # Build query based on whether we're using user_id or ip_address
    if key["user_id"]:
        stmt = select(RateLimit).where(
            RateLimit.user_id == key["user_id"],
            RateLimit.endpoint_path == key["endpoint_path"],
        )
    else:
        stmt = select(RateLimit).where(
            RateLimit.ip_address == key["ip_address"],
            RateLimit.endpoint_path == key["endpoint_path"],
        )

    result = db.execute(stmt)
    rate_limit_record = result.scalar_one_or_none()

    if rate_limit_record:
        # Clean up old timestamps
        valid_timestamps = [
            ts for ts in rate_limit_record.requests if ts > cutoff_time
        ]

        # Check if limit exceeded
        if len(valid_timestamps) >= limit:
            # Calculate reset time based on oldest timestamp
            if valid_timestamps:
                oldest_timestamp = min(valid_timestamps)
                reset_time = oldest_timestamp + window_seconds - current_time
            else:
                reset_time = window_seconds

            return {
                "exceeded": True,
                "reset_time": max(1, int(reset_time)),
                "total": limit,
                "remaining": 0,
            }

        # Add current timestamp and update record
        valid_timestamps.append(current_time)

        # Update the record with new timestamps
        stmt = (
            update(RateLimit)
            .where(RateLimit.id == rate_limit_record.id)
            .values(requests=valid_timestamps, updated_at=datetime.now())
        )
        db.execute(stmt)
        db.commit()

        return {
            "exceeded": False,
            "reset_time": window_seconds,
            "total": limit,
            "remaining": limit - len(valid_timestamps),
        }
    else:
        # Create new rate limit record
        new_record = RateLimit(
            user_id=key["user_id"],
            ip_address=key["ip_address"],
            endpoint_path=key["endpoint_path"],
            requests=[current_time],
        )
        db.add(new_record)
        db.commit()

        return {
            "exceeded": False,
            "reset_time": window_seconds,
            "total": limit,
            "remaining": limit - 1,
        }


# A dependency that performs rate limiting for unauthenticated endpoints
def create_rate_limiter(
    authenticated_limit: int = 100,
    unauthenticated_limit: int = 20,
    window_seconds: int = 60,
):
    """
    Creates a dependency function that performs rate limiting for endpoints

    Example usage as a dependency:

    @router.get("/public-endpoint")
    async def public_endpoint(
        request: Request,
        db: Session = Depends(get_db),
        _: None = Depends(create_rate_limiter(100, 20))
    ):
        return {"message": "Rate-limited endpoint"}

    Args:
        authenticated_limit: Maximum requests per window for authenticated users
        unauthenticated_limit: Maximum requests per window for unauthenticated users
        window_seconds: Time window in seconds (default: 60)

    Returns:
        A dependency function for rate limiting
    """

    async def rate_limiter(
        request: Request,
        db: Session = Depends(get_db),
        auth_header: Optional[str] = Security(authorization_header),
    ):
        # Determine if request is authenticated by checking for a valid token
        user_id = None
        try:
            if auth_header:
                # Extract token using token_validation.py's function
                token = get_token(auth_header, None)
                if token:
                    # Validate token and get user_id
                    user_id = validate_token(token, db, get_id=True)
                    # Store the user_id in request state for potential use by other middlewares/dependencies
                    request.state.user_id = user_id
        except Exception as e:
            logger.warning(f"Authentication check failed: {str(e)}")
            # Continue as unauthenticated if token validation fails

        # Apply appropriate rate limit
        limit = authenticated_limit if user_id else unauthenticated_limit

        # Get rate limit key
        rate_limit_key = get_rate_limit_key(request, user_id)

        # Check rate limit and update database
        rate_limit_info = check_and_update_rate_limit(
            db=db,
            key=rate_limit_key,
            limit=limit,
            window_seconds=window_seconds,
        )

        # If limit exceeded, return 429 response
        if rate_limit_info["exceeded"]:
            reset_time = rate_limit_info["reset_time"]
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                },
            )

        # Store rate limit info in request state for headers
        request.state.rate_limit_info = {
            "limit": limit,
            "remaining": rate_limit_info["remaining"],
            "reset": int(time.time() + window_seconds),
        }

        # Return None since this is just a validation dependency
        return None

    return rate_limiter


# A dependency that performs rate limiting for authenticated endpoints
def create_authenticated_rate_limiter(
    authenticated_limit: int = 100,
    window_seconds: int = 60,
):
    """
    Creates a dependency function that performs rate limiting for authenticated endpoints.
    This should be used after authentication is performed and user_id is available.

    Example usage with authentication:

    @router.put("/user-endpoint")
    @requires_auth(get_id=True)
    async def user_endpoint(
        request: Request,
        db: Session = Depends(get_db),
        token: str = Depends(get_token),
        user_id: UUID = None,
        _: None = Depends(create_authenticated_rate_limiter(100))
    ):
        return {"message": "Rate-limited authenticated endpoint"}

    Args:
        authenticated_limit: Maximum requests per window for authenticated users
        window_seconds: Time window in seconds (default: 60)

    Returns:
        A dependency function for rate limiting authenticated requests
    """

    async def auth_rate_limiter(
        request: Request,
        db: Session = Depends(get_db),
    ):
        # Get user_id from request state (set by authentication)
        user_id = getattr(request.state, "user_id", None)

        if user_id is None:
            logger.warning(
                "No user_id found in request state. This rate limiter should be used after authentication."
            )
            # Fallback to IP-based limiting if somehow no user_id is available

        # Get rate limit key
        rate_limit_key = get_rate_limit_key(request, user_id)

        # Check rate limit and update database
        rate_limit_info = check_and_update_rate_limit(
            db=db,
            key=rate_limit_key,
            limit=authenticated_limit,
            window_seconds=window_seconds,
        )

        # If limit exceeded, return 429 response
        if rate_limit_info["exceeded"]:
            reset_time = rate_limit_info["reset_time"]
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Limit": str(authenticated_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                },
            )

        # Store rate limit info in request state for headers
        request.state.rate_limit_info = {
            "limit": authenticated_limit,
            "remaining": rate_limit_info["remaining"],
            "reset": int(time.time() + window_seconds),
        }

        # Return None since this is just a validation dependency
        return None

    return auth_rate_limiter


# Middleware to add rate limit headers to responses
async def add_rate_limit_headers(request: Request, call_next):
    """
    Middleware to add rate limit headers to responses.
    This should be added to your FastAPI app:

    app.middleware("http")(add_rate_limit_headers)
    """
    # Process the request and get the response
    response = await call_next(request)

    # Add rate limit headers if available
    rate_limit_info = getattr(request.state, "rate_limit_info", None)
    if rate_limit_info:
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(
            rate_limit_info["remaining"]
        )
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])

    return response


# For backward compatibility, keeping the decorator pattern
def rate_limit(
    authenticated_limit: int = 100,
    unauthenticated_limit: int = 20,
    window_seconds: int = 60,
):
    """
    Rate limiting decorator that restricts the number of requests per time window.

    NOTE: Using dependencies is the preferred approach in FastAPI for cleaner Swagger docs.
    Please consider using create_rate_limiter() instead.

    This decorator can be used on any endpoint, whether it requires authentication or not.
    It uses token_validation.py functions to extract and validate tokens.

    Example:
        @router.get("/public-endpoint")
        @rate_limit(authenticated_limit=100, unauthenticated_limit=20)
        async def public_endpoint(request: Request, db: Session = Depends(get_db)):
            return {"message": "This is a public endpoint"}

    Args:
        authenticated_limit: Maximum requests per window for authenticated users
        unauthenticated_limit: Maximum requests per window for unauthenticated users
        window_seconds: Time window in seconds (default: 60)

    Returns:
        Callable: Decorated function with rate limiting applied
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            request: Request, db: Session = Depends(get_db), *args, **kwargs
        ):
            # Create and use the rate limiter
            rate_limiter = create_rate_limiter(
                authenticated_limit, unauthenticated_limit, window_seconds
            )
            await rate_limiter(request, db)

            # Execute the endpoint function
            response = await func(request, db=db, *args, **kwargs)

            # Add rate limit headers to response
            if isinstance(response, JSONResponse) and hasattr(
                request.state, "rate_limit_info"
            ):
                info = request.state.rate_limit_info
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(
                    info["remaining"]
                )
                response.headers["X-RateLimit-Reset"] = str(info["reset"])

            return response

        return wrapper

    return decorator


# For backward compatibility, keeping the decorator pattern
def optimized_rate_limit_with_auth(
    authenticated_limit: int = 100,
    window_seconds: int = 60,
):
    """
    An optimized version of rate limit decorator that works after authentication.

    NOTE: Using dependencies is the preferred approach in FastAPI for cleaner Swagger docs.
    Please consider using create_authenticated_rate_limiter() instead.

    This decorator should be used with endpoints that use the requires_auth decorator
    or endpoints where user_id is available in kwargs.

    Usage example:
        @router.put("/protected-endpoint")
        @requires_auth(get_id=True)
        @optimized_rate_limit_with_auth(authenticated_limit=100)
        async def protected_endpoint(
            request: Request,
            db: Session = Depends(get_db),
            token: str = Depends(get_token),
            user_id: UUID = None,
        ):
            return {"message": "This is a protected endpoint"}

    Args:
        authenticated_limit: Maximum requests per window for authenticated users
        window_seconds: Time window in seconds

    Returns:
        Callable: Decorated function with rate limiting applied
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            request: Request, db: Session = Depends(get_db), *args, **kwargs
        ):
            # Get user_id from kwargs (set by requires_auth or similar)
            user_id = kwargs.get("user_id")
            # Store it in request state for the rate limiter to use
            request.state.user_id = user_id

            # Create and use the rate limiter
            auth_rate_limiter = create_authenticated_rate_limiter(
                authenticated_limit, window_seconds
            )
            await auth_rate_limiter(request, db)

            # Execute the endpoint function
            response = await func(request, db=db, *args, **kwargs)

            # Add rate limit headers to response
            if isinstance(response, JSONResponse) and hasattr(
                request.state, "rate_limit_info"
            ):
                info = request.state.rate_limit_info
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(
                    info["remaining"]
                )
                response.headers["X-RateLimit-Reset"] = str(info["reset"])

            return response

        return wrapper

    return decorator


# Example using the dependency approach - much cleaner in Swagger UI
async def example_public_endpoint_with_dependency(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(create_rate_limiter(50, 5)),
):
    """This is a test endpoint demonstrating rate limiting with dependencies."""
    return {"message": "Hello, world!"}


# Example of the decorator pattern - less ideal for Swagger UI
@rate_limit(authenticated_limit=50, unauthenticated_limit=5)
async def example_public_endpoint(
    request: Request, db: Session = Depends(get_db)
):
    """This is a test endpoint demonstrating rate limiting with decorators."""
    return {"message": "Hello, world!"}


# Note for distributed deployments:
"""
IMPORTANT DISTRIBUTED DEPLOYMENT CONSIDERATIONS:

This database-backed implementation works across distributed environments with some considerations:

1. Database Performance:
   - Each request requires database reads and writes for rate limiting
   - High-traffic applications should monitor database performance
   - Consider database connection pooling and query optimization

2. Alternative Considerations:
   - Sticky sessions could still be beneficial for performance reasons
   - For extremely high traffic, a dedicated caching layer (Redis/Memcached) could offload the database
   - A separate rate limiting service could be used for very large deployments

3. Scaling Recommendations:
   - Start with this implementation as it's robust and secure
   - Monitor database performance under load
   - Consider database optimizations (indexes, etc.) if needed
   - Only introduce additional complexity when proven necessary by metrics

This implementation addresses the core security concerns by providing proper rate limiting
tied to user identity, preventing authentication bypass, and ensuring consistent
enforcement across distributed application instances.
"""
