"""Models Package.

SQLAlchemy ORM models that define the database schema. Every table model
inherits from the declarative Base defined here so that metadata is shared
and migrations/table creation stay consistent. The package re-exports lookup
tables (e.g. user_type_lk, subscription_plan_lk), core entities (user, profile,
session), payment and subscription models, and audit/transaction log models.

Usage:
    >>> from fastx_database.persistence.models import Base
    >>> from fastx_database.persistence.models.user import User
    >>> from fastx_database.persistence.models.user_type_lk import UserTypeLk
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

from fastx_database.persistence.models.plan import Plan
from fastx_database.persistence.models.coupon import Coupon

# Schema lookup tables
from fastx_database.persistence.models.user_type_lk import UserTypeLk
from fastx_database.persistence.models.api_lk import ApiLk
from fastx_database.persistence.models.subscription_plan_lk import SubscriptionPlanLk
from fastx_database.persistence.models.status_lk import StatusLk
from fastx_database.persistence.models.education_level_lk import EducationLevelLk
from fastx_database.persistence.models.location_lk import LocationLk
from fastx_database.persistence.models.language_lk import LanguageLk
from fastx_database.persistence.models.gender_lk import GenderLk
from fastx_database.persistence.models.payment_provider_lk import PaymentProviderLk
from fastx_database.persistence.models.payment_status_lk import PaymentStatusLk
from fastx_database.persistence.models.payment_method_type_lk import PaymentMethodTypeLk
from fastx_database.persistence.models.reaction_type_lk import ReactionTypeLk
from fastx_database.persistence.models.country_lk import CountryLk

# Schema core
from fastx_database.persistence.models.user import User
from fastx_database.persistence.models.user_signing_key import UserSigningKey
from fastx_database.persistence.models.consent_record import ConsentRecord
from fastx_database.persistence.models.idempotency_record import IdempotencyRecord
from fastx_database.persistence.models.user_one_time_token import UserOneTimeToken
from fastx_database.persistence.models.user_login_event import UserLoginEvent
from fastx_database.persistence.models.outbox_event import OutboxEvent
from fastx_database.persistence.models.system_setting import SystemSetting
from fastx_database.persistence.models.user_mfa_factor import UserMfaFactor
from fastx_database.persistence.models.data_export_request import DataExportRequest
from fastx_database.persistence.models.security_event import SecurityEvent
from fastx_database.persistence.models.usage_counter import UsageCounter
from fastx_database.persistence.models.user_profile_photo import UserProfilePhoto
from fastx_database.persistence.models.user_language import UserLanguage
from fastx_database.persistence.models.profile import Profile
from fastx_database.persistence.models.session import Session
from fastx_database.persistence.models.interview_reminder import InterviewReminder
from fastx_database.persistence.models.user_device import UserDevice
from fastx_database.persistence.models.refresh_token import RefreshToken
from fastx_database.persistence.models.notification_history import NotificationHistory
from fastx_database.persistence.models.user_notification_preference import (
    UserNotificationPreference,
)
from fastx_database.persistence.models.user_usage_alert_preference import (
    UserUsageAlertPreference,
)
from fastx_database.persistence.models.organization import (
    Organization,
    OrganizationMember,
    OrganizationInvite,
)

# Schema subscription & payments
from fastx_database.persistence.models.subscription import Subscription
from fastx_database.persistence.models.user_subscription import UserSubscription
from fastx_database.persistence.models.payment_transaction import PaymentTransaction
from fastx_database.persistence.models.payment_refund import PaymentRefund
from fastx_database.persistence.models.user_payment_method import UserPaymentMethod
from fastx_database.persistence.models.invoice import Invoice

# Crowdfunding (campaigns, reward tiers, pledges)
from fastx_database.persistence.models.crowdfunding import (
    CrowdfundingCampaign,
    CrowdfundingPledge,
    CrowdfundingReward,
)

# Industrial IoT / automation (facilities, assets, devices, telemetry — multi-domain)
from fastx_database.persistence.models.industrial_iot import (
    IndustrialAsset,
    IndustrialFacility,
    IndustrialIoTDevice,
    IndustrialTelemetryChannel,
    IndustrialTelemetrySample,
)

# Healthcare (facilities, patients, practitioners, encounters — multi-domain)
from fastx_database.persistence.models.healthcare import (
    ClinicalEncounter,
    ClinicalEncounterParticipant,
    HealthcareFacility,
    HealthcarePatient,
    HealthcarePractitioner,
)

# Commerce (generic catalog, cart, orders, fulfillment)
from fastx_database.persistence.models.product import Product
from fastx_database.persistence.models.cart import Cart, CartItem
from fastx_database.persistence.models.order import Order, OrderItem
from fastx_database.persistence.models.shipment import Shipment
from fastx_database.persistence.models.shipment_tracking_log import ShipmentTrackingLog

# Pure.cam / personal ledger (API_AND_DATA_REFERENCE.md)
from fastx_database.persistence.models.ledger_workspace import LedgerWorkspace
from fastx_database.persistence.models.ledger_transaction import LedgerTransaction
from fastx_database.persistence.models.ledger_linked_account import LedgerLinkedAccount
from fastx_database.persistence.models.ledger_budget import LedgerBudget
from fastx_database.persistence.models.ledger_balance_alert import LedgerBalanceAlert
from fastx_database.persistence.models.ledger_recurring_transaction import (
    LedgerRecurringTransaction,
)
from fastx_database.persistence.models.ledger_debt import (
    LedgerDebt,
    LedgerDebtPayment,
    LedgerDebtCredit,
)
from fastx_database.persistence.models.ledger_goal import (
    LedgerGoal,
    LedgerGoalContribution,
)
from fastx_database.persistence.models.ledger_emi_loan import LedgerEmiLoan
from fastx_database.persistence.models.ledger_custom_category import LedgerCustomCategory
from fastx_database.persistence.models.ledger_invoice_document import (
    LedgerBusinessInfo,
    LedgerInvoiceDocument,
)
from fastx_database.persistence.models.ledger_scheduled_reminder import (
    LedgerScheduledReminder,
)
from fastx_database.persistence.models.ledger_vault_entry import LedgerVaultEntry
from fastx_database.persistence.models.stellar_contract import (
    StellarContract,
    StellarContractHours,
    StellarContractPayment,
)

# Schema audit
from fastx_database.persistence.models.transaction_log import TransactionLog
from fastx_database.persistence.models.audit_log import AuditLog

# Conversations (LLM threads)
from fastx_database.persistence.models.conversation import (
    Conversation,
    ConversationMessage,
)

# User-to-user messaging (chats, read receipts, notification delivery)
from fastx_database.persistence.models.messaging_chat import (
    Chat,
    ChatMessage,
    ChatMessageNotification,
    ChatParticipant,
    MessageReadReceipt,
)

# Webhooks (outbound + delivery log)
from fastx_database.persistence.models.webhook import Webhook, WebhookDelivery

# Per-user encrypted LLM provider keys (BYOK)
from fastx_database.persistence.models.user_provider_key import UserProviderKey

# Backward-compatible alias for code that still imports ``UserLlmProviderKey``
UserLlmProviderKey = UserProviderKey

# =============================================================================
# Auto-register model migrations
# =============================================================================
# When models are imported, their migrations are automatically discovered
# and registered with the migration registry. This allows migrations to be
# imported alongside models.
#
# Usage:
#   >>> from fastx_database.persistence.models import User
#   >>> from fastx_database.migrations import get_model_migration
#   >>> migration = get_model_migration(User)
#   >>> migration.upgrade(engine)


def _auto_register_migrations():
    """Auto-discover and register migrations for all imported models."""
    try:
        from fastx_database.migrations.discovery import discover_model_migrations

        discover_model_migrations(auto_register=True)
    except Exception:
        # Silently fail if migrations module is not available
        pass


# Run auto-registration
_auto_register_migrations()

# Clean up to avoid polluting namespace
del _auto_register_migrations
