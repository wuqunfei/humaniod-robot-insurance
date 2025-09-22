"""Policy entity models and schemas."""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum, Numeric, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from src.core.database import Base


class CoverageType(str, Enum):
    """Coverage type enumeration."""
    PHYSICAL_DAMAGE = "physical_damage"
    LIABILITY = "liability"
    CYBER_SECURITY = "cyber_security"
    BUSINESS_INTERRUPTION = "business_interruption"
    PRODUCT_RECALL = "product_recall"
    COMPREHENSIVE = "comprehensive"


class PolicyStatus(str, Enum):
    """Policy status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING_RENEWAL = "pending_renewal"


class PaymentFrequency(str, Enum):
    """Payment frequency enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# SQLAlchemy Model
class Policy(Base):
    """Policy database model."""
    
    __tablename__ = "policies"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_number = Column(String(50), unique=True, nullable=False)
    robot_id = Column(PGUUID(as_uuid=True), nullable=False)
    customer_id = Column(String(255), nullable=False)
    coverage_types = Column(JSON, nullable=False)  # List of coverage types
    premium_amount = Column(Numeric(10, 2), nullable=False)
    deductible_amount = Column(Numeric(10, 2), nullable=False)
    coverage_limit = Column(Numeric(12, 2), nullable=False)
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.DRAFT)
    payment_frequency = Column(SQLEnum(PaymentFrequency), default=PaymentFrequency.ANNUAL)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    terms_and_conditions = Column(JSON, nullable=False)
    underwriter_notes = Column(Text, nullable=True)
    auto_renewal = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas
class CoverageDetails(BaseModel):
    """Coverage details for specific coverage type."""
    coverage_type: CoverageType
    coverage_limit: Decimal = Field(..., gt=0, description="Maximum coverage amount")
    deductible: Decimal = Field(..., ge=0, description="Deductible amount")
    premium_portion: Decimal = Field(..., gt=0, description="Premium portion for this coverage")
    exclusions: List[str] = Field(default_factory=list, description="Coverage exclusions")
    conditions: List[str] = Field(default_factory=list, description="Special conditions")

    @field_validator('coverage_limit', 'deductible', 'premium_portion')
    @classmethod
    def validate_monetary_amounts(cls, v):
        """Validate monetary amounts are properly formatted."""
        if v < 0:
            raise ValueError('Monetary amounts must be non-negative')
        # Ensure no more than 2 decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError('Monetary amounts cannot have more than 2 decimal places')
        return v

    @field_validator('exclusions', 'conditions')
    @classmethod
    def validate_text_lists(cls, v):
        """Validate text lists contain non-empty strings."""
        if v:
            for item in v:
                if not isinstance(item, str) or not item.strip():
                    raise ValueError('List items must be non-empty strings')
        return v


class PolicyTerms(BaseModel):
    """Policy terms and conditions."""
    coverage_details: List[CoverageDetails] = Field(..., min_length=1, description="Coverage details")
    policy_conditions: List[str] = Field(default_factory=list, description="General policy conditions")
    exclusions: List[str] = Field(default_factory=list, description="General exclusions")
    claim_procedures: List[str] = Field(default_factory=list, description="Claim filing procedures")
    cancellation_terms: str = Field(..., min_length=10, description="Cancellation policy")
    renewal_terms: str = Field(..., min_length=10, description="Renewal policy")
    jurisdiction: str = Field(..., min_length=2, max_length=10, description="Legal jurisdiction")
    regulatory_compliance: Dict[str, str] = Field(default_factory=dict, description="Regulatory compliance info")

    @field_validator('policy_conditions', 'exclusions', 'claim_procedures')
    @classmethod
    def validate_text_lists(cls, v):
        """Validate text lists contain non-empty strings."""
        if v:
            for item in v:
                if not isinstance(item, str) or not item.strip():
                    raise ValueError('List items must be non-empty strings')
        return v

    @field_validator('jurisdiction')
    @classmethod
    def validate_jurisdiction(cls, v):
        """Validate jurisdiction format."""
        if not re.match(r'^[A-Z]{2,3}(-[A-Z]{2,3})?$', v.upper()):
            raise ValueError('Jurisdiction must be in format like "US", "CA", "EU-DE"')
        return v.upper()

    @model_validator(mode='after')
    def validate_coverage_consistency(self):
        """Validate coverage details consistency."""
        coverage_types = [cd.coverage_type for cd in self.coverage_details]
        
        # Check for duplicate coverage types
        if len(coverage_types) != len(set(coverage_types)):
            raise ValueError('Duplicate coverage types are not allowed')
        
        # Validate comprehensive coverage rules
        if CoverageType.COMPREHENSIVE in coverage_types:
            if len(coverage_types) > 1:
                raise ValueError('Comprehensive coverage cannot be combined with other coverage types')
        
        return self


class PolicyBase(BaseModel):
    """Base policy schema."""
    robot_id: UUID = Field(..., description="Robot ID")
    customer_id: str = Field(..., min_length=1, max_length=255, description="Customer ID")
    coverage_types: List[CoverageType] = Field(..., min_length=1, description="Coverage types")
    premium_amount: Decimal = Field(..., gt=0, description="Annual premium amount")
    deductible_amount: Decimal = Field(..., ge=0, description="Deductible amount")
    coverage_limit: Decimal = Field(..., gt=0, description="Total coverage limit")
    effective_date: date = Field(..., description="Policy effective date")
    expiration_date: date = Field(..., description="Policy expiration date")
    payment_frequency: PaymentFrequency = Field(default=PaymentFrequency.ANNUAL)
    risk_level: RiskLevel = Field(..., description="Risk assessment level")
    terms_and_conditions: PolicyTerms = Field(..., description="Policy terms")
    auto_renewal: bool = Field(default=True, description="Auto-renewal enabled")

    @field_validator('customer_id')
    @classmethod
    def validate_customer_id(cls, v):
        """Validate customer ID format."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Customer ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('premium_amount', 'deductible_amount', 'coverage_limit')
    @classmethod
    def validate_monetary_amounts(cls, v):
        """Validate monetary amounts."""
        if v < 0:
            raise ValueError('Monetary amounts must be non-negative')
        if v.as_tuple().exponent < -2:
            raise ValueError('Monetary amounts cannot have more than 2 decimal places')
        return v

    @field_validator('coverage_types')
    @classmethod
    def validate_coverage_types(cls, v):
        """Validate coverage types list."""
        if not v:
            raise ValueError('At least one coverage type must be specified')
        
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError('Duplicate coverage types are not allowed')
        
        # Validate comprehensive coverage rules
        if CoverageType.COMPREHENSIVE in v and len(v) > 1:
            raise ValueError('Comprehensive coverage cannot be combined with other coverage types')
        
        return v

    @model_validator(mode='after')
    def validate_policy_dates(self):
        """Validate policy date relationships."""
        if self.expiration_date <= self.effective_date:
            raise ValueError('Expiration date must be after effective date')
        
        # Policy term should be reasonable (between 1 month and 5 years)
        term_days = (self.expiration_date - self.effective_date).days
        if term_days < 30:
            raise ValueError('Policy term must be at least 30 days')
        if term_days > 1825:  # 5 years
            raise ValueError('Policy term cannot exceed 5 years')
        
        return self

    @model_validator(mode='after')
    def validate_deductible_vs_coverage(self):
        """Validate deductible is reasonable compared to coverage limit."""
        if self.deductible_amount > self.coverage_limit * Decimal('0.5'):
            raise ValueError('Deductible cannot exceed 50% of coverage limit')
        
        return self

    @model_validator(mode='after')
    def validate_premium_reasonableness(self):
        """Validate premium is reasonable compared to coverage."""
        # Premium should not exceed 20% of coverage limit annually
        max_premium = self.coverage_limit * Decimal('0.2')
        if self.premium_amount > max_premium:
            raise ValueError('Premium amount exceeds reasonable threshold (20% of coverage limit)')
        
        # Minimum premium based on risk level
        min_premiums = {
            RiskLevel.LOW: Decimal('100'),
            RiskLevel.MEDIUM: Decimal('250'),
            RiskLevel.HIGH: Decimal('500'),
            RiskLevel.CRITICAL: Decimal('1000')
        }
        
        if self.premium_amount < min_premiums[self.risk_level]:
            raise ValueError(f'Premium too low for {self.risk_level.value} risk level')
        
        return self


class PolicyCreate(PolicyBase):
    """Schema for creating a policy."""
    underwriter_notes: Optional[str] = Field(None, max_length=2000, description="Underwriter notes")

    @field_validator('underwriter_notes')
    @classmethod
    def validate_underwriter_notes(cls, v):
        """Validate underwriter notes."""
        if v is not None and not v.strip():
            raise ValueError('Underwriter notes cannot be empty if provided')
        return v


class PolicyUpdate(BaseModel):
    """Schema for updating a policy."""
    status: Optional[PolicyStatus] = None
    premium_amount: Optional[Decimal] = Field(None, gt=0)
    deductible_amount: Optional[Decimal] = Field(None, ge=0)
    coverage_limit: Optional[Decimal] = Field(None, gt=0)
    payment_frequency: Optional[PaymentFrequency] = None
    terms_and_conditions: Optional[PolicyTerms] = None
    underwriter_notes: Optional[str] = Field(None, max_length=2000)
    auto_renewal: Optional[bool] = None

    @field_validator('premium_amount', 'deductible_amount', 'coverage_limit')
    @classmethod
    def validate_monetary_amounts(cls, v):
        """Validate monetary amounts."""
        if v is not None:
            if v < 0:
                raise ValueError('Monetary amounts must be non-negative')
            if v.as_tuple().exponent < -2:
                raise ValueError('Monetary amounts cannot have more than 2 decimal places')
        return v

    @field_validator('underwriter_notes')
    @classmethod
    def validate_underwriter_notes(cls, v):
        """Validate underwriter notes."""
        if v is not None and not v.strip():
            raise ValueError('Underwriter notes cannot be empty if provided')
        return v


class PolicyResponse(PolicyBase):
    """Schema for policy response."""
    id: UUID
    policy_number: str
    status: PolicyStatus
    underwriter_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    """Schema for policy list response."""
    policies: List[PolicyResponse]
    total: int
    page: int
    size: int


class PolicyQuoteRequest(BaseModel):
    """Schema for policy quote request."""
    robot_id: UUID = Field(..., description="Robot ID")
    customer_id: str = Field(..., min_length=1, max_length=255)
    coverage_types: List[CoverageType] = Field(..., min_length=1)
    desired_coverage_limit: Decimal = Field(..., gt=0)
    preferred_deductible: Optional[Decimal] = Field(None, ge=0)
    policy_term_months: int = Field(..., ge=1, le=60, description="Policy term in months")
    payment_frequency: PaymentFrequency = Field(default=PaymentFrequency.ANNUAL)

    @field_validator('coverage_types')
    @classmethod
    def validate_coverage_types(cls, v):
        """Validate coverage types for quote."""
        if CoverageType.COMPREHENSIVE in v and len(v) > 1:
            raise ValueError('Comprehensive coverage cannot be combined with other coverage types')
        return v


class PolicyQuoteResponse(BaseModel):
    """Schema for policy quote response."""
    quote_id: UUID = Field(default_factory=uuid4)
    robot_id: UUID
    customer_id: str
    coverage_types: List[CoverageType]
    coverage_limit: Decimal
    recommended_deductible: Decimal
    estimated_premium: Decimal
    risk_level: RiskLevel
    risk_factors: List[str]
    quote_valid_until: datetime
    terms_summary: Dict[str, Any]
    
    class Config:
        from_attributes = True


class PolicyRenewalRequest(BaseModel):
    """Schema for policy renewal request."""
    policy_id: UUID
    new_expiration_date: date
    premium_adjustment: Optional[Decimal] = Field(None, description="Premium adjustment amount")
    coverage_changes: Optional[List[CoverageType]] = None
    terms_updates: Optional[PolicyTerms] = None

    @model_validator(mode='after')
    def validate_renewal_date(self):
        """Validate renewal date is in the future."""
        if self.new_expiration_date <= date.today():
            raise ValueError('Renewal expiration date must be in the future')
        return self


class PolicyCancellationRequest(BaseModel):
    """Schema for policy cancellation request."""
    policy_id: UUID
    cancellation_date: date
    reason: str = Field(..., min_length=10, max_length=500)
    refund_requested: bool = Field(default=False)

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        """Validate cancellation reason."""
        if not v.strip():
            raise ValueError('Cancellation reason cannot be empty')
        return v.strip()

    @model_validator(mode='after')
    def validate_cancellation_date(self):
        """Validate cancellation date."""
        if self.cancellation_date < date.today():
            raise ValueError('Cancellation date cannot be in the past')
        return self