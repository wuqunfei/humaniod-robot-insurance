"""Custom exception classes for the application."""

from typing import Any, Dict, Optional


class BaseCustomException(Exception):
    """Base exception class for custom exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """Raised when input validation fails."""
    pass


class NotFoundError(BaseCustomException):
    """Raised when a requested resource is not found."""
    pass


class AuthenticationError(BaseCustomException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(BaseCustomException):
    """Raised when authorization fails."""
    pass


class BusinessLogicError(BaseCustomException):
    """Raised when business logic validation fails."""
    pass


class ExternalServiceError(BaseCustomException):
    """Raised when external service calls fail."""
    pass


class DatabaseError(BaseCustomException):
    """Raised when database operations fail."""
    pass


class ConfigurationError(BaseCustomException):
    """Raised when configuration is invalid."""
    pass


# Robot-specific exceptions
class RobotNotFoundError(NotFoundError):
    """Raised when a robot is not found."""
    pass


class InvalidRobotSpecificationError(ValidationError):
    """Raised when robot specifications are invalid."""
    pass


# Policy-specific exceptions
class PolicyNotFoundError(NotFoundError):
    """Raised when a policy is not found."""
    pass


class PolicyValidationError(ValidationError):
    """Raised when policy validation fails."""
    pass


class InsufficientCoverageError(BusinessLogicError):
    """Raised when coverage is insufficient for the request."""
    pass


# Claims-specific exceptions
class ClaimNotFoundError(NotFoundError):
    """Raised when a claim is not found."""
    pass


class InvalidClaimStatusError(BusinessLogicError):
    """Raised when claim status transition is invalid."""
    pass


class ClaimProcessingError(BusinessLogicError):
    """Raised when claim processing fails."""
    pass


# Risk assessment exceptions
class RiskAssessmentError(BusinessLogicError):
    """Raised when risk assessment fails."""
    pass


class InsufficientDataError(ValidationError):
    """Raised when insufficient data is provided for processing."""
    pass