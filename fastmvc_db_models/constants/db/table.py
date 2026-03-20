"""
Database Table Name Constants Module.

This module defines constants for database table names. Using these
constants instead of string literals prevents typos and enables
easy refactoring of table names.

Usage:
    >>> from constants.db.table import Table
    >>> class User(Base):
    ...     __tablename__ = Table.USER
"""




from typing import Final


class Table:
    """
    Database table name constants.

    This class provides centralized constants for all database table names
    used in the application. Using these constants ensures consistency
    and makes table name changes easier to manage.

    Attributes:
        USER (str): Table name for user accounts.

    Example:
        >>> from constants.db.table import Table
        >>> from sqlalchemy import Column, Integer, String
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>>
        >>> Base = declarative_base()
        >>>
        >>> class User(Base):
        ...     __tablename__ = Table.USER
        ...     id = Column(Integer, primary_key=True)
        ...     email = Column(String, unique=True)

    Note:
        Add new table name constants here as the application grows.
        Follow the pattern: TABLE_NAME: Final[str] = "table_name"
    """




    USER: Final[str] = "user"
    """Table name for user accounts and authentication data."""


    SESSION: Final[str] = "sessions"
    """Table name for interview sessions."""


    DOCUMENT: Final[str] = "documents"
    """Table name for uploaded documents (resume/JD)."""


    AUDIT: Final[str] = "audit_log"
    """Table name for audit log (actor, action, resource, timestamp, metadata)."""


    WEBHOOK: Final[str] = "webhooks"
    """Table name for webhook endpoint config (URL, secret, events)."""


    WEBHOOK_DELIVERY: Final[str] = "webhook_deliveries"
    """Table name for webhook delivery log (idempotency, retries)."""


    PLAN: Final[str] = "plans"
    """Table name for plan/entitlement limits (sessions_per_month, models_allowed)."""


    SUBSCRIPTION: Final[str] = "subscriptions"
    """Table name for user subscriptions to plans."""


    INVOICE: Final[str] = "invoices"
    """Table name for billing invoices (Stripe or other provider)."""


    COUPON: Final[str] = "coupons"
    """Table name for promo/coupon codes."""


    API_KEY: Final[str] = "api_keys"
    """Table name for server-to-server API keys (per user, hashed key, scopes)."""


    CONSENT: Final[str] = "consent_records"
    """Table name for ToS/Privacy consent (user_id, type, version, accepted_at)."""


    ORGANIZATION: Final[str] = "organizations"
    """Table name for organizations (workspaces)."""


    ORGANIZATION_MEMBER: Final[str] = "organization_members"
    """Table name for user-org membership (user_id, organization_id, role)."""


    ORGANIZATION_INVITE: Final[str] = "organization_invites"
    """Table name for pending invites (email, organization_id, role, token)."""


    # Lookup tables (schema.dbml)
    USER_TYPE_LK: Final[str] = "user_type_lk"
    API_LK: Final[str] = "api_lk"
    SUBSCRIPTION_PLAN_LK: Final[str] = "subscription_plan_lk"
    STATUS_LK: Final[str] = "status_lk"
    EDUCATION_LEVEL_LK: Final[str] = "education_level_lk"
    LOCATION_LK: Final[str] = "location_lk"
    LANGUAGE_LK: Final[str] = "language_lk"
    GENDER_LK: Final[str] = "gender_lk"
    PAYMENT_PROVIDER_LK: Final[str] = "payment_provider_lk"
    PAYMENT_STATUS_LK: Final[str] = "payment_status_lk"
    PAYMENT_METHOD_TYPE_LK: Final[str] = "payment_method_type_lk"
    REACTION_TYPE_LK: Final[str] = "reaction_type_lk"
    COUNTRY_LK: Final[str] = "country_lk"

    # Core (schema.dbml)
    USER_PROFILE_PHOTO: Final[str] = "user_profile_photo"
    USER_LANGUAGE: Final[str] = "user_language"
    PROFILE: Final[str] = "profile"
    USER_DEVICE: Final[str] = "user_device"
    REFRESH_TOKEN: Final[str] = "refresh_token"
    USER_SUBSCRIPTION: Final[str] = "user_subscription"
    PAYMENT_TRANSACTION: Final[str] = "payment_transaction"
    PAYMENT_REFUND: Final[str] = "payment_refund"
    USER_PAYMENT_METHOD: Final[str] = "user_payment_method"
    TRANSACTION_LOG: Final[str] = "transaction_log"
    NOTIFICATION_HISTORY: Final[str] = "notification_history"
    USER_NOTIFICATION_PREFERENCE: Final[str] = "user_notification_preference"
    USER_USAGE_ALERT_PREFERENCE: Final[str] = "user_usage_alert_preference"
    INTERVIEW_REMINDER: Final[str] = "interview_reminder"
    """Table for user-scheduled interview reminders (scheduled_at, reminder_minutes_before)."""

    CONVERSATION: Final[str] = "conversations"
    """Table for LLM conversations (user_id, optional session_id, title, created_at)."""

    CONVERSATION_MESSAGE: Final[str] = "conversation_messages"
    """Table for conversation messages (conversation_id, role, content, created_at)."""
