"""
Models Package.

SQLAlchemy ORM models that define the database schema. Every table model
inherits from the declarative Base defined here so that metadata is shared
and migrations/table creation stay consistent. The package re-exports lookup
tables (e.g. user_type_lk, subscription_plan_lk), core entities (user, profile,
session), payment and subscription models, and audit/transaction log models.

Usage:
    >>> from fast_database.persistence.models import Base
    >>> from fast_database.persistence.models.user import User
    >>> from fast_database.persistence.models.user_type_lk import UserTypeLk
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

from fast_database.persistence.models.plan import Plan
from fast_database.persistence.models.coupon import Coupon

# Schema lookup tables
from fast_database.persistence.models.user_type_lk import UserTypeLk
from fast_database.persistence.models.api_lk import ApiLk
from fast_database.persistence.models.subscription_plan_lk import SubscriptionPlanLk
from fast_database.persistence.models.status_lk import StatusLk
from fast_database.persistence.models.education_level_lk import EducationLevelLk
from fast_database.persistence.models.location_lk import LocationLk
from fast_database.persistence.models.language_lk import LanguageLk
from fast_database.persistence.models.gender_lk import GenderLk
from fast_database.persistence.models.payment_provider_lk import PaymentProviderLk
from fast_database.persistence.models.payment_status_lk import PaymentStatusLk
from fast_database.persistence.models.payment_method_type_lk import PaymentMethodTypeLk
from fast_database.persistence.models.reaction_type_lk import ReactionTypeLk
from fast_database.persistence.models.country_lk import CountryLk

# Schema core
from fast_database.persistence.models.user import User
from fast_database.persistence.models.user_signing_key import UserSigningKey
from fast_database.persistence.models.consent_record import ConsentRecord
from fast_database.persistence.models.idempotency_record import IdempotencyRecord
from fast_database.persistence.models.user_one_time_token import UserOneTimeToken
from fast_database.persistence.models.user_login_event import UserLoginEvent
from fast_database.persistence.models.outbox_event import OutboxEvent
from fast_database.persistence.models.system_setting import SystemSetting
from fast_database.persistence.models.user_mfa_factor import UserMfaFactor
from fast_database.persistence.models.data_export_request import DataExportRequest
from fast_database.persistence.models.security_event import SecurityEvent
from fast_database.persistence.models.usage_counter import UsageCounter
from fast_database.persistence.models.user_profile_photo import UserProfilePhoto
from fast_database.persistence.models.user_language import UserLanguage
from fast_database.persistence.models.profile import Profile
from fast_database.persistence.models.session import Session
from fast_database.persistence.models.interview_reminder import InterviewReminder
from fast_database.persistence.models.user_device import UserDevice
from fast_database.persistence.models.refresh_token import RefreshToken
from fast_database.persistence.models.notification_history import NotificationHistory
from fast_database.persistence.models.user_notification_preference import UserNotificationPreference
from fast_database.persistence.models.user_usage_alert_preference import UserUsageAlertPreference
from fast_database.persistence.models.organization import Organization, OrganizationMember, OrganizationInvite

# Schema subscription & payments
from fast_database.persistence.models.subscription import Subscription
from fast_database.persistence.models.user_subscription import UserSubscription
from fast_database.persistence.models.payment_transaction import PaymentTransaction
from fast_database.persistence.models.payment_refund import PaymentRefund
from fast_database.persistence.models.user_payment_method import UserPaymentMethod
from fast_database.persistence.models.invoice import Invoice

# Crowdfunding (campaigns, reward tiers, pledges)
from fast_database.persistence.models.crowdfunding import (
    CrowdfundingCampaign,
    CrowdfundingPledge,
    CrowdfundingReward,
)

# Industrial IoT / automation (facilities, assets, devices, telemetry — multi-domain)
from fast_database.persistence.models.industrial_iot import (
    IndustrialAsset,
    IndustrialFacility,
    IndustrialIoTDevice,
    IndustrialTelemetryChannel,
    IndustrialTelemetrySample,
)

# Healthcare (facilities, patients, practitioners, encounters — multi-domain)
from fast_database.persistence.models.healthcare import (
    ClinicalEncounter,
    ClinicalEncounterParticipant,
    HealthcareFacility,
    HealthcarePatient,
    HealthcarePractitioner,
)

# Commerce (generic catalog, cart, orders, fulfillment)
from fast_database.persistence.models.product import Product
from fast_database.persistence.models.cart import Cart, CartItem
from fast_database.persistence.models.order import Order, OrderItem
from fast_database.persistence.models.shipment import Shipment
from fast_database.persistence.models.shipment_tracking_log import ShipmentTrackingLog

# Pure.cam / personal ledger (API_AND_DATA_REFERENCE.md)
from fast_database.persistence.models.ledger_workspace import LedgerWorkspace
from fast_database.persistence.models.ledger_transaction import LedgerTransaction
from fast_database.persistence.models.ledger_linked_account import LedgerLinkedAccount
from fast_database.persistence.models.ledger_budget import LedgerBudget
from fast_database.persistence.models.ledger_balance_alert import LedgerBalanceAlert
from fast_database.persistence.models.ledger_recurring_transaction import LedgerRecurringTransaction
from fast_database.persistence.models.ledger_debt import LedgerDebt, LedgerDebtPayment, LedgerDebtCredit
from fast_database.persistence.models.ledger_goal import LedgerGoal, LedgerGoalContribution
from fast_database.persistence.models.ledger_emi_loan import LedgerEmiLoan
from fast_database.persistence.models.ledger_custom_category import LedgerCustomCategory
from fast_database.persistence.models.ledger_invoice_document import LedgerBusinessInfo, LedgerInvoiceDocument
from fast_database.persistence.models.ledger_scheduled_reminder import LedgerScheduledReminder
from fast_database.persistence.models.ledger_vault_entry import LedgerVaultEntry
from fast_database.persistence.models.stellar_contract import (
    StellarContract,
    StellarContractHours,
    StellarContractPayment,
)

# Schema audit
from fast_database.persistence.models.transaction_log import TransactionLog
from fast_database.persistence.models.audit_log import AuditLog

# Conversations (LLM threads)
from fast_database.persistence.models.conversation import Conversation, ConversationMessage

# User-to-user messaging (chats, read receipts, notification delivery)
from fast_database.persistence.models.messaging_chat import (
    Chat,
    ChatMessage,
    ChatMessageNotification,
    ChatParticipant,
    MessageReadReceipt,
)

# Webhooks (outbound + delivery log)
from fast_database.persistence.models.webhook import Webhook, WebhookDelivery

# Per-user encrypted LLM provider keys (BYOK)
from fast_database.persistence.models.user_provider_key import UserProviderKey

# Backward-compatible alias for code that still imports ``UserLlmProviderKey``
UserLlmProviderKey = UserProviderKey
