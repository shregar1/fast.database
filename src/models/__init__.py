"""
Models Package.

SQLAlchemy ORM models that define the database schema. Every table model
inherits from the declarative Base defined here so that metadata is shared
and migrations/table creation stay consistent. The package re-exports lookup
tables (e.g. user_type_lk, subscription_plan_lk), core entities (user, profile,
session), payment and subscription models, and audit/transaction log models.

Usage:
    >>> from fastmvc_db_models.models import Base
    >>> from fastmvc_db_models.models.user import User
    >>> from fastmvc_db_models.models.user_type_lk import UserTypeLk
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

from src.models.plan import Plan
from src.models.coupon import Coupon

# Schema lookup tables
from src.models.user_type_lk import UserTypeLk
from src.models.api_lk import ApiLk
from src.models.subscription_plan_lk import SubscriptionPlanLk
from src.models.status_lk import StatusLk
from src.models.education_level_lk import EducationLevelLk
from src.models.location_lk import LocationLk
from src.models.language_lk import LanguageLk
from src.models.gender_lk import GenderLk
from src.models.payment_provider_lk import PaymentProviderLk
from src.models.payment_status_lk import PaymentStatusLk
from src.models.payment_method_type_lk import PaymentMethodTypeLk
from src.models.reaction_type_lk import ReactionTypeLk
from src.models.country_lk import CountryLk

# Schema core
from src.models.user import User
from src.models.user_profile_photo import UserProfilePhoto
from src.models.user_language import UserLanguage
from src.models.profile import Profile
from src.models.session import Session
from src.models.interview_reminder import InterviewReminder
from src.models.user_device import UserDevice
from src.models.refresh_token import RefreshToken
from src.models.notification_history import NotificationHistory
from src.models.user_notification_preference import UserNotificationPreference
from src.models.user_usage_alert_preference import UserUsageAlertPreference
from src.models.organization import Organization, OrganizationMember, OrganizationInvite

# Schema subscription & payments
from src.models.subscription import Subscription
from src.models.user_subscription import UserSubscription
from src.models.payment_transaction import PaymentTransaction
from src.models.payment_refund import PaymentRefund
from src.models.user_payment_method import UserPaymentMethod
from src.models.invoice import Invoice

# Commerce (generic catalog, cart, orders, fulfillment)
from src.models.product import Product
from src.models.cart import Cart, CartItem
from src.models.order import Order, OrderItem
from src.models.shipment import Shipment
from src.models.shipment_tracking_log import ShipmentTrackingLog

# Pure.cam / personal ledger (API_AND_DATA_REFERENCE.md)
from src.models.ledger_workspace import LedgerWorkspace
from src.models.ledger_transaction import LedgerTransaction
from src.models.ledger_linked_account import LedgerLinkedAccount
from src.models.ledger_budget import LedgerBudget
from src.models.ledger_balance_alert import LedgerBalanceAlert
from src.models.ledger_recurring_transaction import LedgerRecurringTransaction
from src.models.ledger_debt import LedgerDebt, LedgerDebtPayment, LedgerDebtCredit
from src.models.ledger_goal import LedgerGoal, LedgerGoalContribution
from src.models.ledger_emi_loan import LedgerEmiLoan
from src.models.ledger_custom_category import LedgerCustomCategory
from src.models.ledger_invoice_document import LedgerBusinessInfo, LedgerInvoiceDocument
from src.models.ledger_scheduled_reminder import LedgerScheduledReminder
from src.models.ledger_vault_entry import LedgerVaultEntry
from src.models.stellar_contract import (
    StellarContract,
    StellarContractHours,
    StellarContractPayment,
)

# Schema audit
from src.models.transaction_log import TransactionLog
from src.models.audit_log import AuditLog

# Conversations (LLM threads)
from src.models.conversation import Conversation, ConversationMessage

# User-to-user messaging (chats, read receipts, notification delivery)
from src.models.messaging_chat import (
    Chat,
    ChatMessage,
    ChatMessageNotification,
    ChatParticipant,
    MessageReadReceipt,
)

# Webhooks (outbound + delivery log)
from src.models.webhook import Webhook, WebhookDelivery
