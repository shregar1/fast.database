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


    USER_SIGNING_KEY: Final[str] = "user_signing_key"
    """Ed25519 keypair material per user (PEM public + Fernet-encrypted private); one row per user."""


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


    USER_LLM_PROVIDER_KEY: Final[str] = "user_llm_provider_keys"
    """Per-user encrypted LLM provider API keys (OpenAI, Anthropic, OpenRouter, Gemini, …)."""


    CONSENT: Final[str] = "consent_records"
    """Table name for ToS/Privacy consent (user_id, type, version, accepted_at)."""


    IDEMPOTENCY_RECORD: Final[str] = "idempotency_records"
    """HTTP / payment idempotency: dedupe writes and optionally cache replay responses."""


    USER_ONE_TIME_TOKEN: Final[str] = "user_one_time_tokens"
    """Single-use tokens: password reset, email verification, magic links (hashed at rest)."""


    USER_LOGIN_EVENT: Final[str] = "user_login_events"
    """Append-only login attempts (success/fail) for security analytics and lockout policies."""


    OUTBOX_EVENT: Final[str] = "outbox_events"
    """Transactional outbox for reliable async delivery (Kafka, webhooks, workers)."""


    SYSTEM_SETTING: Final[str] = "system_settings"
    """Namespaced key/value settings (feature toggles, limits) without redeploy; optional JSON or secret flag."""


    USER_MFA_FACTOR: Final[str] = "user_mfa_factors"
    """Second factors per user (TOTP, WebAuthn credentials); secrets stored encrypted or as opaque handles."""


    DATA_EXPORT_REQUEST: Final[str] = "data_export_requests"
    """GDPR / data-portability export jobs (status, artifact location, expiry)."""


    SECURITY_EVENT: Final[str] = "security_events"
    """High-signal security signals (lockouts, impossible travel, admin actions) for SIEM and dashboards."""


    USAGE_COUNTER: Final[str] = "usage_counters"
    """Idempotent daily/hourly usage buckets for quotas, billing, and rate-limit analytics."""


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
    REMINDER: Final[str] = "reminder"
    """Table for user-scheduled reminders (scheduled_at, reminder_minutes_before)."""

    CONVERSATION: Final[str] = "conversations"
    """Table for LLM conversations (user_id, optional session_id, title, created_at)."""

    CONVERSATION_MESSAGE: Final[str] = "conversation_messages"
    """Table for conversation messages (conversation_id, role, content, created_at)."""

    # User-to-user messaging (chats, read receipts, outbound message notifications)
    CHAT: Final[str] = "chats"
    """Chat thread or room (direct, group, channel); optional org scope."""

    CHAT_PARTICIPANT: Final[str] = "chat_participants"
    """Membership in a chat (role, mute, notification level, last-read cursor)."""

    CHAT_MESSAGE: Final[str] = "chat_messages"
    """User message in a chat (body, content type, reply, soft delete)."""

    MESSAGE_READ_RECEIPT: Final[str] = "message_read_receipts"
    """Per-user seen/read timestamp for a chat message (read receipts)."""

    CHAT_MESSAGE_NOTIFICATION: Final[str] = "chat_message_notifications"
    """Delivery log for push/email/SMS notifications tied to a chat message."""

    # Commerce (generic cart / catalog / order — reusable across industries)
    PRODUCT: Final[str] = "product"
    """Sellable catalog item (sku, pricing, inventory flags, JSON metadata)."""

    CART: Final[str] = "cart"
    """Shopping cart (user or guest, currency, status, cached totals)."""

    CART_ITEM: Final[str] = "cart_item"
    """Line in a cart (product ref, quantity, unit price snapshot, line metadata)."""

    COMMERCE_ORDER: Final[str] = "orders"
    """Customer order (order_number, addresses snapshot, totals, payment link)."""

    ORDER_ITEM: Final[str] = "order_item"
    """Line on a placed order (immutable price/title snapshots, fulfillment hint)."""

    SHIPMENT: Final[str] = "shipments"
    """Fulfillment shipment for an order (carrier, tracking, status, timestamps)."""

    SHIPMENT_TRACKING_LOG: Final[str] = "shipment_tracking_log"
    """Append-only carrier tracking events for a shipment (scans, status, raw payload)."""

    # Pure.cam / personal ledger (see API_AND_DATA_REFERENCE.md — sync + local shapes)
    LEDGER_WORKSPACE: Final[str] = "ledger_workspace"
    """User workspace (client id + name); scopes ledger rows."""

    LEDGER_TRANSACTION: Final[str] = "ledger_transaction"
    """Ledger transaction (INCOME/EXPENSE, splits, SMS link)."""

    LEDGER_LINKED_ACCOUNT: Final[str] = "ledger_linked_account"
    """SMS/notification import rule (sender pattern, body filter)."""

    LEDGER_BUDGET: Final[str] = "ledger_budget"
    """Category or total expense budget (MONTHLY/WEEKLY)."""

    LEDGER_BALANCE_ALERT: Final[str] = "ledger_balance_alert"
    """Low-balance threshold per workspace (at most one row per workspace)."""

    LEDGER_RECURRING_TRANSACTION: Final[str] = "ledger_recurring_transaction"
    """Recurring rent/subscription (WEEKLY/MONTHLY, next due date)."""

    LEDGER_DEBT: Final[str] = "ledger_debt"
    """IOU / informal debt (direction, amount, due)."""

    LEDGER_DEBT_PAYMENT: Final[str] = "ledger_debt_payment"
    """Payment applied to a ledger debt."""

    LEDGER_DEBT_CREDIT: Final[str] = "ledger_debt_credit"
    """Credit adjustment on a ledger debt."""

    LEDGER_GOAL: Final[str] = "ledger_goal"
    """Savings goal (target, deadline)."""

    LEDGER_GOAL_CONTRIBUTION: Final[str] = "ledger_goal_contribution"
    """Contribution toward a goal."""

    LEDGER_EMI_LOAN: Final[str] = "ledger_emi_loan"
    """EMI / loan tracker (principal, months, reminders)."""

    LEDGER_CUSTOM_CATEGORY: Final[str] = "ledger_custom_category"
    """User-defined expense/income category."""

    LEDGER_INVOICE_DOCUMENT: Final[str] = "ledger_invoice_document"
    """User invoice/bill document (line items JSON); not provider billing Invoice."""

    LEDGER_BUSINESS_INFO: Final[str] = "ledger_business_info"
    """Seller/business block for generated invoices (JSON snapshot)."""

    LEDGER_SCHEDULED_REMINDER: Final[str] = "ledger_scheduled_reminder"
    """Scheduled notification (daily/monthly, screen route, EMI link)."""

    LEDGER_VAULT_ENTRY: Final[str] = "ledger_vault_entry"
    """Vault item metadata / encrypted backup pointer (no plaintext secrets)."""

    STELLAR_CONTRACT: Final[str] = "stellar_contract"
    """Hourly client contract (SQLite contracts table shape)."""

    STELLAR_CONTRACT_HOURS: Final[str] = "stellar_contract_hours"
    """Logged hours per contract per month/year."""

    STELLAR_CONTRACT_PAYMENT: Final[str] = "stellar_contract_payment"
    """Payment recorded against a contract."""

    # Crowdfunding (campaigns, reward tiers, pledges / backings)
    CROWDFUNDING_CAMPAIGN: Final[str] = "crowdfunding_campaign"
    """Creator-launched funding round (goal, window, status, funded total)."""

    CROWDFUNDING_REWARD: Final[str] = "crowdfunding_reward"
    """Perk / reward tier attached to a campaign (minimum pledge, caps)."""

    CROWDFUNDING_PLEDGE: Final[str] = "crowdfunding_pledge"
    """Backer pledge toward a campaign (optional reward tier, payment lifecycle)."""

    # Industrial IoT / automation (generic multi-domain: factory, logistics, energy, …)
    INDUSTRIAL_FACILITY: Final[str] = "industrial_facility"
    """Physical or logical site (plant, warehouse, substation); optional org scope."""

    INDUSTRIAL_ASSET: Final[str] = "industrial_asset"
    """Equipment or logical node in a hierarchy under a facility (line, machine, cell)."""

    INDUSTRIAL_IOT_DEVICE: Final[str] = "industrial_iot_device"
    """Edge gateway, PLC, sensor hub, or connected controller."""

    INDUSTRIAL_TELEMETRY_CHANNEL: Final[str] = "industrial_telemetry_channel"
    """Logical signal / tag on a device (topic, OPC node, register)."""

    INDUSTRIAL_TELEMETRY_SAMPLE: Final[str] = "industrial_telemetry_sample"
    """Bounded telemetry point-in-time value (full historian often external TSDB)."""

    # Healthcare (generic multi-domain: acute, ambulatory, telehealth, lab, imaging, …)
    HEALTHCARE_FACILITY: Final[str] = "healthcare_facility"
    """Care delivery site (hospital, clinic, lab site); optional org scope."""

    HEALTHCARE_PATIENT: Final[str] = "healthcare_patient"
    """Patient / subject of care within an organization namespace."""

    HEALTHCARE_PRACTITIONER: Final[str] = "healthcare_practitioner"
    """Licensed or credentialed provider (physician, nurse, therapist, …)."""

    CLINICAL_ENCOUNTER: Final[str] = "clinical_encounter"
    """Visit, admission contact, telehealth session, or similar clinical interaction."""

    CLINICAL_ENCOUNTER_PARTICIPANT: Final[str] = "clinical_encounter_participant"
    """Practitioner participation on an encounter (role: attending, consultant, …)."""
