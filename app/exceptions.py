"""Application-specific exceptions for the Library Management System."""

class LibraryException(Exception):
    """Base exception for all Library API business rules."""
    pass

class ResourceNotFoundError(LibraryException):
    """Raised when a requested Member or Book does not exist."""
    pass

class DuplicateResourceError(LibraryException):
    """Raised when an email, membership ID, or ISBN already exists."""
    pass

class BusinessRuleError(LibraryException):
    """Raised when an operation violates a business rule."""
    pass