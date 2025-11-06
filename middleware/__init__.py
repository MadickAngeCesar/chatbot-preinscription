"""
Package middleware - Gestion centralisée de l'authentification, validation et logging
"""

from .auth_middleware import (
    login_required,
    admin_required,
    role_required,
    optional_auth,
    init_auth_middleware
)

from .validation_middleware import (
    validate_json,
    validate_query_params,
    validate_file_upload,
    validate_email,
    validate_password,
    validate_phone,
    sanitize_string,
    init_validation_middleware
)

from .logging_middleware import (
    init_logging_middleware,
    log_auth_attempt,
    log_user_action,
    log_security_event,
    log_database_error
)

from .error_handler import (
    init_error_handlers,
    APIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    format_validation_errors
)

__all__ = [
    # Auth
    'login_required',
    'admin_required',
    'role_required',
    'optional_auth',
    'init_auth_middleware',
    
    # Validation
    'validate_json',
    'validate_query_params',
    'validate_file_upload',
    'validate_email',
    'validate_password',
    'validate_phone',
    'sanitize_string',
    'init_validation_middleware',
    
    # Logging
    'init_logging_middleware',
    'log_auth_attempt',
    'log_user_action',
    'log_security_event',
    'log_database_error',
    
    # Error handling
    'init_error_handlers',
    'APIError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'DatabaseError',
    'format_validation_errors'
]
