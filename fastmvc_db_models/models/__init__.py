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

from fastmvc_db_models.models.plan import Plan
from fastmvc_db_models.models.coupon import Coupon

# Schema lookup tables
from fastmvc_db_models.models.user_type_lk import UserTypeLk
from fastmvc_db_models.models.api_lk import ApiLk
from fastmvc_db_models.models.subscription_plan_lk import SubscriptionPlanLk
from fastmvc_db_models.models.status_lk import StatusLk
from fastmvc_db_models.models.education_level_lk import EducationLevelLk
from fastmvc_db_models.models.location_lk import LocationLk
from fastmvc_db_models.models.language_lk import LanguageLk
from fastmvc_db_models.models.gender_lk import GenderLk
from fastmvc_db_models.models.payment_provider_lk import PaymentProviderLk
from fastmvc_db_models.models.payment_status_lk import PaymentStatusLk
from fastmvc_db_models.models.payment_method_type_lk import PaymentMethodTypeLk
from fastmvc_db_models.models.reaction_type_lk import ReactionTypeLk
from fastmvc_db_models.models.country_lk import CountryLk

# Schema core
from fastmvc_db_models.models.user import User
from fastmvc_db_models.models.user_profile_photo import UserProfilePhoto
from fastmvc_db_models.models.user_language import UserLanguage
from fastmvc_db_models.models.profile import Profile
from fastmvc_db_models.models.session import Session
from fastmvc_db_models.models.interview_reminder import InterviewReminder
from fastmvc_db_models.models.user_device import UserDevice
from fastmvc_db_models.models.refresh_token import RefreshToken
from fastmvc_db_models.models.notification_history import NotificationHistory
from fastmvc_db_models.models.user_notification_preference import UserNotificationPreference
from fastmvc_db_models.models.user_usage_alert_preference import UserUsageAlertPreference
from fastmvc_db_models.models.organization import Organization, OrganizationMember, OrganizationInvite

# Schema subscription & payments
from fastmvc_db_models.models.subscription import Subscription
from fastmvc_db_models.models.user_subscription import UserSubscription
from fastmvc_db_models.models.payment_transaction import PaymentTransaction
from fastmvc_db_models.models.payment_refund import PaymentRefund
from fastmvc_db_models.models.user_payment_method import UserPaymentMethod
from fastmvc_db_models.models.invoice import Invoice

# Schema audit
from fastmvc_db_models.models.transaction_log import TransactionLog
from fastmvc_db_models.models.audit_log import AuditLog

# Conversations (LLM threads)
from fastmvc_db_models.models.conversation import Conversation, ConversationMessage

# Webhooks (outbound + delivery log)
from fastmvc_db_models.models.webhook import Webhook, WebhookDelivery
