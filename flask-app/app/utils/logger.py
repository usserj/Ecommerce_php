"""Structured logging configuration for the application."""
import logging
import sys
from datetime import datetime
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logs."""

    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        if hasattr(record, 'order_id'):
            log_data['order_id'] = record.order_id

        if hasattr(record, 'product_id'):
            log_data['product_id'] = record.product_id

        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        return json.dumps(log_data)


def setup_logging(app):
    """Configure structured logging for the application."""
    # Create logger
    logger = logging.getLogger('ecommerce')
    logger.setLevel(logging.INFO if not app.debug else logging.DEBUG)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)

    # File handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())
    logger.addHandler(error_handler)

    # File handler for all logs
    info_handler = logging.FileHandler('logs/app.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(StructuredFormatter())
    logger.addHandler(info_handler)

    # Set app logger
    app.logger = logger

    return logger


def log_payment_event(logger, event_type, order_id, amount, method, status, user_id=None, error=None):
    """Log payment-related events with structured data."""
    extra = {
        'order_id': order_id,
        'user_id': user_id
    }

    message = f"Payment {event_type}: Order #{order_id}, Amount ${amount}, Method {method}, Status {status}"

    if error:
        logger.error(message, extra=extra, exc_info=error)
    else:
        logger.info(message, extra=extra)


def log_order_state_change(logger, order_id, old_state, new_state, user_id=None):
    """Log order state changes."""
    extra = {
        'order_id': order_id,
        'user_id': user_id
    }

    logger.info(
        f"Order state changed: Order #{order_id} from '{old_state}' to '{new_state}'",
        extra=extra
    )


def log_stock_change(logger, product_id, old_stock, new_stock, reason, order_id=None):
    """Log stock changes for audit trail."""
    extra = {
        'product_id': product_id,
        'order_id': order_id
    }

    logger.info(
        f"Stock changed: Product #{product_id} from {old_stock} to {new_stock}. Reason: {reason}",
        extra=extra
    )


def log_user_action(logger, user_id, action, details=None):
    """Log user actions."""
    extra = {'user_id': user_id}

    message = f"User action: {action}"
    if details:
        message += f" - {details}"

    logger.info(message, extra=extra)


def log_error(logger, error_type, error_message, context=None, exc_info=None):
    """Log application errors with context."""
    extra = context or {}

    logger.error(
        f"{error_type}: {error_message}",
        extra=extra,
        exc_info=exc_info
    )
