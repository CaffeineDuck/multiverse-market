from fastapi import HTTPException, status

class MultiverseMarketException(HTTPException):
    """Base exception for all market-related errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected error occurred"

class NotFoundException(MultiverseMarketException):
    """Resource not found."""
    status_code = status.HTTP_404_NOT_FOUND

class UserNotFoundException(NotFoundException):
    """User not found."""
    detail = "User not found"

class ItemNotFoundException(NotFoundException):
    """Item not found."""
    detail = "Item not found"

class UniverseNotFoundException(NotFoundException):
    """Universe not found."""
    detail = "Universe not found"

class InsufficientResourcesException(MultiverseMarketException):
    """Base class for insufficient resource errors."""
    status_code = status.HTTP_400_BAD_REQUEST

class InsufficientBalanceException(InsufficientResourcesException):
    """User has insufficient balance."""
    detail = "Insufficient balance"

class InsufficientStockException(InsufficientResourcesException):
    """Item has insufficient stock."""
    detail = "Insufficient stock"