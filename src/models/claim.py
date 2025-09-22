"""Claim entity models and schemas."""

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


class IncidentType(str, Enum):
    """Incident type enumeration."""
    PHYSICAL_DAMAGE = "physical_damage"
    MALFUNCTION = "malfunction"
    THIRD_PARTY_LIABILITY = "third_party_liability"
    CYBER_SECURITY_BREACH = "cyber_security_breach"
    THEFT = "theft"
    FIRE_DAMAGE = "fire_damage"
    WATER_DAMAGE = "water_damage"
    ELECTRICAL_DAMAGE = "electrical_damage"
    SOFTWARE_FAILURE = "software_failure"
    OPERATOR_ERROR = "operator_error"


class ClaimStatus(str, Enum):
    """Claim status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATING = "investigating"
    PENDING_DOCUMENTATION = "pending_documentation"
    APPROVED = "approved"
    DENIED = "denied"
    SETTLED = "settled"
    CLOSED = "closed"
    REOPENED = "reopened"


class ClaimPriority(str, Enum):
    """Claim priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DamageAssessment(str, Enum):
    """Damage assessment enumeration."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    TOTAL_LOSS = "total_loss"


class DocumentType(str, Enum):
    """Document type enumeration."""
    INCIDENT_REPORT = "incident_report"
    PHOTOS = "photos"
    DIAGNOSTIC_DATA = "diagnostic_data"
    REPAIR_ESTIMATE = "repair_estimate"
    POLICE_REPORT = "police_report"
    WITNESS_STATEMENT = "witness_statement"
    MEDICAL_REPORT = "medical_report"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    OTHER = "other"


# SQLAlchemy Model
class Claim(Base):
    """Claim database model."""
    
    __tablename__ = "claims"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    claim_number = Column(String(50), unique=True, nullable=False)
    policy_id = Column(PGUUID(as_uuid=True), nullable=False)
    robot_id = Column(PGUUID(as_uuid=True), nullable=False)
    customer_id = Column(String(255), nullable=False)
    incident_type = Column(SQLEnum(IncidentType), nullable=False)
    incident_date = Column(Date, nullable=False)
    reported_date = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT)
    priority = Column(SQLEnum(ClaimPriority), default=ClaimPriority.MEDIUM)
    damage_assessment = Column(SQLEnum(DamageAssessment), nullable=True)
    incident_description = Column(Text, nullable=False)
    incident_location = Column(String(500), nullable=True)
    estimated_damage_amount = Column(Numeric(12, 2), nullable=True)
    settlement_amount = Column(Numeric(12, 2), nullable=True)
    deductible_amount = Column(Numeric(10, 2), nullable=True)
    adjuster_id = Column(String(255), nullable=True)
    adjuster_notes = Column(JSON, nullable=True)  # List of notes with timestamps
    supporting_documents = Column(JSON, nullable=True)  # List of document references
    diagnostic_data = Column(JSON, nullable=True)
    third_party_involved = Column(Boolean, default=False)
    third_party_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas
class AdjusterNote(BaseModel):
    """Adjuster note with timestamp."""
    timestamp: datetime
    adjuster_id: str = Field(..., min_length=1, max_length=255)
    note: str = Field(..., min_length=10, max_length=2000)
    note_type: str = Field(default="general", description="Type of note (general, assessment, decision)")

    @field_validator('adjuster_id')
    @classmethod
    def validate_adjuster_id(cls, v):
        """Validate adjuster ID format."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Adjuster ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('note')
    @classmethod
    def validate_note(cls, v):
        """Validate note content."""
        if not v.strip():
            raise ValueError('Note cannot be empty')
        return v.strip()


class SupportingDocument(BaseModel):
    """Supporting document reference."""
    document_id: str = Field(..., min_length=1, max_length=255)
    document_type: DocumentType
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0, description="File size in bytes")
    upload_date: datetime
    uploaded_by: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        """Validate filename format."""
        # Basic filename validation - no path separators or dangerous characters
        if not re.match(r'^[A-Za-z0-9\-_\.\s]+$', v):
            raise ValueError('Filename contains invalid characters')
        if '..' in v or v.startswith('.'):
            raise ValueError('Invalid filename format')
        return v

    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        """Validate file size limits."""
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError('File size cannot exceed 50MB')
        return v


class ThirdPartyDetails(BaseModel):
    """Third party involvement details."""
    party_type: str = Field(..., description="Type of third party (person, property, vehicle, etc.)")
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=255)
    insurance_company: Optional[str] = Field(None, max_length=255)
    policy_number: Optional[str] = Field(None, max_length=100)
    damage_description: Optional[str] = Field(None, max_length=1000)
    estimated_liability: Optional[Decimal] = Field(None, ge=0)

    @field_validator('contact_phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is not None:
            # Basic phone validation - digits, spaces, hyphens, parentheses, plus, dots
            if not re.match(r'^[\+\d\s\-\(\)\.]+$', v):
                raise ValueError('Invalid phone number format')
        return v

    @field_validator('contact_email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if v is not None:
            # Basic email validation
            if not re.match(r'^[A-Za-z0-9\.\-_]+@[A-Za-z0-9\.\-_]+\.[A-Za-z]{2,}$', v):
                raise ValueError('Invalid email format')
        return v


class ClaimBase(BaseModel):
    """Base claim schema."""
    policy_id: UUID = Field(..., description="Policy ID")
    robot_id: UUID = Field(..., description="Robot ID")
    customer_id: str = Field(..., min_length=1, max_length=255)
    incident_type: IncidentType
    incident_date: date = Field(..., description="Date when incident occurred")
    incident_description: str = Field(..., min_length=20, max_length=5000)
    incident_location: Optional[str] = Field(None, max_length=500)
    estimated_damage_amount: Optional[Decimal] = Field(None, ge=0)
    third_party_involved: bool = Field(default=False)
    third_party_details: Optional[ThirdPartyDetails] = None

    @field_validator('customer_id')
    @classmethod
    def validate_customer_id(cls, v):
        """Validate customer ID format."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Customer ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('incident_description')
    @classmethod
    def validate_incident_description(cls, v):
        """Validate incident description."""
        if not v.strip():
            raise ValueError('Incident description cannot be empty')
        return v.strip()

    @field_validator('estimated_damage_amount')
    @classmethod
    def validate_estimated_damage(cls, v):
        """Validate estimated damage amount."""
        if v is not None:
            if v.as_tuple().exponent < -2:
                raise ValueError('Damage amount cannot have more than 2 decimal places')
            if v > Decimal('10000000'):  # 10 million max
                raise ValueError('Estimated damage amount exceeds maximum allowed')
        return v

    @model_validator(mode='after')
    def validate_incident_date(self):
        """Validate incident date is not in the future."""
        if self.incident_date > date.today():
            raise ValueError('Incident date cannot be in the future')
        return self

    @model_validator(mode='after')
    def validate_third_party_consistency(self):
        """Validate third party details consistency."""
        if self.third_party_involved and self.third_party_details is None:
            raise ValueError('Third party details must be provided when third party is involved')
        if not self.third_party_involved and self.third_party_details is not None:
            raise ValueError('Third party details should not be provided when no third party is involved')
        return self


class ClaimCreate(ClaimBase):
    """Schema for creating a claim."""
    priority: ClaimPriority = Field(default=ClaimPriority.MEDIUM)
    supporting_documents: List[SupportingDocument] = Field(default_factory=list)
    diagnostic_data: Optional[Dict[str, Any]] = Field(None, description="Robot diagnostic data at time of incident")

    @field_validator('supporting_documents')
    @classmethod
    def validate_supporting_documents(cls, v):
        """Validate supporting documents."""
        if len(v) > 20:  # Reasonable limit
            raise ValueError('Cannot attach more than 20 supporting documents')
        
        # Check for duplicate document IDs
        doc_ids = [doc.document_id for doc in v]
        if len(doc_ids) != len(set(doc_ids)):
            raise ValueError('Duplicate document IDs are not allowed')
        
        return v


class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""
    status: Optional[ClaimStatus] = None
    priority: Optional[ClaimPriority] = None
    damage_assessment: Optional[DamageAssessment] = None
    incident_description: Optional[str] = Field(None, min_length=20, max_length=5000)
    incident_location: Optional[str] = Field(None, max_length=500)
    estimated_damage_amount: Optional[Decimal] = Field(None, ge=0)
    settlement_amount: Optional[Decimal] = Field(None, ge=0)
    deductible_amount: Optional[Decimal] = Field(None, ge=0)
    adjuster_id: Optional[str] = Field(None, min_length=1, max_length=255)
    third_party_details: Optional[ThirdPartyDetails] = None

    @field_validator('incident_description')
    @classmethod
    def validate_incident_description(cls, v):
        """Validate incident description."""
        if v is not None and not v.strip():
            raise ValueError('Incident description cannot be empty')
        return v.strip() if v else v

    @field_validator('estimated_damage_amount', 'settlement_amount', 'deductible_amount')
    @classmethod
    def validate_monetary_amounts(cls, v):
        """Validate monetary amounts."""
        if v is not None:
            if v.as_tuple().exponent < -2:
                raise ValueError('Monetary amounts cannot have more than 2 decimal places')
            if v > Decimal('10000000'):  # 10 million max
                raise ValueError('Amount exceeds maximum allowed')
        return v

    @field_validator('adjuster_id')
    @classmethod
    def validate_adjuster_id(cls, v):
        """Validate adjuster ID format."""
        if v is not None and not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Adjuster ID must contain only alphanumeric characters, hyphens, and underscores')
        return v


class ClaimResponse(ClaimBase):
    """Schema for claim response."""
    id: UUID
    claim_number: str
    status: ClaimStatus
    priority: ClaimPriority
    damage_assessment: Optional[DamageAssessment] = None
    reported_date: datetime
    settlement_amount: Optional[Decimal] = None
    deductible_amount: Optional[Decimal] = None
    adjuster_id: Optional[str] = None
    adjuster_notes: List[AdjusterNote] = Field(default_factory=list)
    supporting_documents: List[SupportingDocument] = Field(default_factory=list)
    diagnostic_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClaimListResponse(BaseModel):
    """Schema for claim list response."""
    claims: List[ClaimResponse]
    total: int
    page: int
    size: int


class ClaimStatusUpdate(BaseModel):
    """Schema for claim status updates."""
    claim_id: UUID
    new_status: ClaimStatus
    adjuster_id: str = Field(..., min_length=1, max_length=255)
    notes: str = Field(..., min_length=10, max_length=2000)
    settlement_amount: Optional[Decimal] = Field(None, ge=0)

    @field_validator('adjuster_id')
    @classmethod
    def validate_adjuster_id(cls, v):
        """Validate adjuster ID format."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Adjuster ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        """Validate notes content."""
        if not v.strip():
            raise ValueError('Notes cannot be empty')
        return v.strip()

    @field_validator('settlement_amount')
    @classmethod
    def validate_settlement_amount(cls, v):
        """Validate settlement amount."""
        if v is not None:
            if v.as_tuple().exponent < -2:
                raise ValueError('Settlement amount cannot have more than 2 decimal places')
            if v > Decimal('10000000'):  # 10 million max
                raise ValueError('Settlement amount exceeds maximum allowed')
        return v

    @model_validator(mode='after')
    def validate_status_settlement_consistency(self):
        """Validate status and settlement amount consistency."""
        if self.new_status == ClaimStatus.SETTLED and self.settlement_amount is None:
            raise ValueError('Settlement amount is required when status is set to settled')
        if self.new_status != ClaimStatus.SETTLED and self.settlement_amount is not None:
            raise ValueError('Settlement amount should only be provided when status is settled')
        return self


class ClaimAssessmentRequest(BaseModel):
    """Schema for claim assessment request."""
    claim_id: UUID
    adjuster_id: str = Field(..., min_length=1, max_length=255)
    damage_assessment: DamageAssessment
    assessment_notes: str = Field(..., min_length=20, max_length=2000)
    repair_estimate: Optional[Decimal] = Field(None, ge=0)
    replacement_cost: Optional[Decimal] = Field(None, ge=0)
    recommended_action: str = Field(..., min_length=10, max_length=1000)

    @field_validator('adjuster_id')
    @classmethod
    def validate_adjuster_id(cls, v):
        """Validate adjuster ID format."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('Adjuster ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('assessment_notes', 'recommended_action')
    @classmethod
    def validate_text_fields(cls, v):
        """Validate text fields."""
        if not v.strip():
            raise ValueError('Text fields cannot be empty')
        return v.strip()

    @field_validator('repair_estimate', 'replacement_cost')
    @classmethod
    def validate_cost_estimates(cls, v):
        """Validate cost estimates."""
        if v is not None:
            if v.as_tuple().exponent < -2:
                raise ValueError('Cost estimates cannot have more than 2 decimal places')
            if v > Decimal('10000000'):  # 10 million max
                raise ValueError('Cost estimate exceeds maximum allowed')
        return v

    @model_validator(mode='after')
    def validate_total_loss_consistency(self):
        """Validate total loss assessment consistency."""
        if self.damage_assessment == DamageAssessment.TOTAL_LOSS:
            if self.repair_estimate is not None:
                raise ValueError('Repair estimate should not be provided for total loss assessment')
            if self.replacement_cost is None:
                raise ValueError('Replacement cost is required for total loss assessment')
        return self


class ClaimSearchFilters(BaseModel):
    """Schema for claim search filters."""
    status: Optional[List[ClaimStatus]] = None
    incident_type: Optional[List[IncidentType]] = None
    priority: Optional[List[ClaimPriority]] = None
    damage_assessment: Optional[List[DamageAssessment]] = None
    adjuster_id: Optional[str] = None
    customer_id: Optional[str] = None
    policy_id: Optional[UUID] = None
    robot_id: Optional[UUID] = None
    incident_date_from: Optional[date] = None
    incident_date_to: Optional[date] = None
    reported_date_from: Optional[datetime] = None
    reported_date_to: Optional[datetime] = None
    min_damage_amount: Optional[Decimal] = Field(None, ge=0)
    max_damage_amount: Optional[Decimal] = Field(None, ge=0)

    @model_validator(mode='after')
    def validate_date_ranges(self):
        """Validate date range consistency."""
        if (self.incident_date_from is not None and 
            self.incident_date_to is not None and 
            self.incident_date_from > self.incident_date_to):
            raise ValueError('Incident date from cannot be after incident date to')
        
        if (self.reported_date_from is not None and 
            self.reported_date_to is not None and 
            self.reported_date_from > self.reported_date_to):
            raise ValueError('Reported date from cannot be after reported date to')
        
        if (self.min_damage_amount is not None and 
            self.max_damage_amount is not None and 
            self.min_damage_amount > self.max_damage_amount):
            raise ValueError('Minimum damage amount cannot be greater than maximum damage amount')
        
        return self