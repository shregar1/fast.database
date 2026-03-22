"""
Models Package.

SQLAlchemy ORM models that define the database schema. Every table model
inherits from the declarative Base defined here so that metadata is shared
and migrations/table creation stay consistent. The package re-exports lookup
tables (e.g. user_type_lk, subscription_plan_lk), core entities (user, profile,
session), payment and subscription models, and audit/transaction log models.

Usage:
    >>> from fast_database.models import Base
    >>> from fast_database.models.user import User
    >>> from fast_database.models.user_type_lk import UserTypeLk
    >>>
    >>> # Create all tables (e.g. in migrations or tests)
    >>> Base.metadata.create_all(engine)
"""



from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Base.__doc__ = (
    "SQLAlchemy declarative base for all ORM models. "
    "Subclass this and set __tablename__ and Column attributes to define a table; "
    "the class is registered in Base.metadata for create_all() and migrations. "
    "Example: class MyModel(Base): __tablename__ = 'my_table'; id = Column(Integer, primary_key=True)"
)

from fast_database.models.plan import Plan
from fast_database.models.coupon import Coupon

# Schema lookup tables
from fast_database.models.user_type_lk import UserTypeLk
from fast_database.models.api_lk import ApiLk
from fast_database.models.subscription_plan_lk import SubscriptionPlanLk
from fast_database.models.status_lk import StatusLk
from fast_database.models.education_level_lk import EducationLevelLk
from fast_database.models.location_lk import LocationLk
from fast_database.models.language_lk import LanguageLk
from fast_database.models.gender_lk import GenderLk
from fast_database.models.payment_provider_lk import PaymentProviderLk
from fast_database.models.payment_status_lk import PaymentStatusLk
from fast_database.models.payment_method_type_lk import PaymentMethodTypeLk
from fast_database.models.reaction_type_lk import ReactionTypeLk
from fast_database.models.country_lk import CountryLk

# Schema core
from fast_database.models.user import User
from fast_database.models.user_signing_key import UserSigningKey
from fast_database.models.consent_record import ConsentRecord
from fast_database.models.idempotency_record import IdempotencyRecord
from fast_database.models.user_one_time_token import UserOneTimeToken
from fast_database.models.user_login_event import UserLoginEvent
from fast_database.models.outbox_event import OutboxEvent
from fast_database.models.system_setting import SystemSetting
from fast_database.models.user_mfa_factor import UserMfaFactor
from fast_database.models.data_export_request import DataExportRequest
from fast_database.models.security_event import SecurityEvent
from fast_database.models.usage_counter import UsageCounter
from fast_database.models.user_profile_photo import UserProfilePhoto
from fast_database.models.user_language import UserLanguage
from fast_database.models.profile import Profile
from fast_database.models.session import Session
from fast_database.models.interview_reminder import InterviewReminder
from fast_database.models.user_device import UserDevice
from fast_database.models.refresh_token import RefreshToken
from fast_database.models.notification_history import NotificationHistory
from fast_database.models.user_notification_preference import UserNotificationPreference
from fast_database.models.user_usage_alert_preference import UserUsageAlertPreference
from fast_database.models.organization import Organization, OrganizationMember, OrganizationInvite

# Schema subscription & payments
from fast_database.models.subscription import Subscription
from fast_database.models.user_subscription import UserSubscription
from fast_database.models.payment_transaction import PaymentTransaction
from fast_database.models.payment_refund import PaymentRefund
from fast_database.models.user_payment_method import UserPaymentMethod
from fast_database.models.invoice import Invoice

# Commerce (generic catalog, cart, orders, fulfillment)
from fast_database.models.product import Product
from fast_database.models.cart import Cart, CartItem
from fast_database.models.order import Order, OrderItem
from fast_database.models.shipment import Shipment
from fast_database.models.shipment_tracking_log import ShipmentTrackingLog

# Pure.cam / personal ledger (API_AND_DATA_REFERENCE.md)
from fast_database.models.ledger_workspace import LedgerWorkspace
from fast_database.models.ledger_transaction import LedgerTransaction
from fast_database.models.ledger_linked_account import LedgerLinkedAccount
from fast_database.models.ledger_budget import LedgerBudget
from fast_database.models.ledger_balance_alert import LedgerBalanceAlert
from fast_database.models.ledger_recurring_transaction import LedgerRecurringTransaction
from fast_database.models.ledger_debt import LedgerDebt, LedgerDebtPayment, LedgerDebtCredit
from fast_database.models.ledger_goal import LedgerGoal, LedgerGoalContribution
from fast_database.models.ledger_emi_loan import LedgerEmiLoan
from fast_database.models.ledger_custom_category import LedgerCustomCategory
from fast_database.models.ledger_invoice_document import LedgerBusinessInfo, LedgerInvoiceDocument
from fast_database.models.ledger_scheduled_reminder import LedgerScheduledReminder
from fast_database.models.ledger_vault_entry import LedgerVaultEntry
from fast_database.models.stellar_contract import (
    StellarContract,
    StellarContractHours,
    StellarContractPayment,
)

# Schema audit
from fast_database.models.transaction_log import TransactionLog
from fast_database.models.audit_log import AuditLog

# Conversations (LLM threads)
from fast_database.models.conversation import Conversation, ConversationMessage

# User-to-user messaging (chats, read receipts, notification delivery)
from fast_database.models.messaging_chat import (
    Chat,
    ChatMessage,
    ChatMessageNotification,
    ChatParticipant,
    MessageReadReceipt,
)

# Webhooks (outbound + delivery log)
from fast_database.models.webhook import Webhook, WebhookDelivery

# Per-user encrypted LLM provider keys (BYOK)
from fast_database.models.user_provider_key import UserProviderKey

# Backward-compatible alias for code that still imports ``UserLlmProviderKey``
UserLlmProviderKey = UserProviderKey
