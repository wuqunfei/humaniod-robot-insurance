"""Robot entity models and schemas."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from src.core.database import Base


class RobotType(str, Enum):
    """Robot type enumeration."""
    HUMANOID = "humanoid"
    INDUSTRIAL = "industrial"
    SERVICE = "service"
    COMPANION = "companion"
    MEDICAL = "medical"


class RobotStatus(str, Enum):
    """Robot status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class UsageScenario(str, Enum):
    """Robot usage scenario enumeration."""
    DOMESTIC = "domestic"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    RESEARCH = "research"


# SQLAlchemy Model
class Robot(Base):
    """Robot database model."""
    
    __tablename__ = "robots"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    manufacturer_id = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False)
    robot_type = Column(SQLEnum(RobotType), nullable=False)
    status = Column(SQLEnum(RobotStatus), default=RobotStatus.ACTIVE)
    usage_scenario = Column(SQLEnum(UsageScenario), nullable=False)
    specifications = Column(JSON, nullable=False)
    owner_id = Column(String(255), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_diagnostic_date = Column(DateTime, nullable=True)
    diagnostic_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas
class RobotSpecifications(BaseModel):
    """Robot technical specifications."""
    height_cm: float = Field(..., gt=0, le=300, description="Robot height in centimeters")
    weight_kg: float = Field(..., gt=0, le=1000, description="Robot weight in kilograms")
    max_speed_kmh: float = Field(..., ge=0, le=50, description="Maximum speed in km/h")
    battery_capacity_kwh: float = Field(..., gt=0, le=100, description="Battery capacity in kWh")
    operating_temperature_min: float = Field(..., ge=-40, le=85, description="Minimum operating temperature in Celsius")
    operating_temperature_max: float = Field(..., ge=-40, le=85, description="Maximum operating temperature in Celsius")
    ip_rating: str = Field(..., pattern=r"^IP[0-9X][0-9X]$", description="IP rating for dust and water resistance")
    certifications: list[str] = Field(default_factory=list, description="Safety certifications")
    sensors: list[str] = Field(default_factory=list, description="List of sensors")
    actuators: list[str] = Field(default_factory=list, description="List of actuators")
    ai_capabilities: list[str] = Field(default_factory=list, description="AI and ML capabilities")
    connectivity: list[str] = Field(default_factory=list, description="Connectivity options")

    @field_validator('operating_temperature_max')
    @classmethod
    def validate_temperature_range(cls, v, info):
        """Validate that max temperature is greater than min temperature."""
        if info.data and 'operating_temperature_min' in info.data and v <= info.data['operating_temperature_min']:
            raise ValueError('Maximum operating temperature must be greater than minimum operating temperature')
        return v

    @field_validator('certifications', 'sensors', 'actuators', 'ai_capabilities', 'connectivity')
    @classmethod
    def validate_non_empty_strings(cls, v):
        """Validate that list items are non-empty strings."""
        if v:
            for item in v:
                if not isinstance(item, str) or not item.strip():
                    raise ValueError('List items must be non-empty strings')
        return v


class DiagnosticData(BaseModel):
    """Robot diagnostic data."""
    timestamp: datetime
    battery_level: float = Field(..., ge=0, le=100, description="Battery level percentage")
    temperature: float = Field(..., description="Operating temperature in Celsius")
    error_codes: list[str] = Field(default_factory=list, description="Active error codes")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    sensor_readings: Dict[str, Any] = Field(default_factory=dict, description="Sensor readings")
    operational_hours: float = Field(..., ge=0, description="Total operational hours")
    maintenance_alerts: list[str] = Field(default_factory=list, description="Maintenance alerts")


class RobotBase(BaseModel):
    """Base robot schema."""
    manufacturer_id: str = Field(..., min_length=1, max_length=255)
    model: str = Field(..., min_length=1, max_length=255)
    serial_number: str = Field(..., min_length=1, max_length=255)
    robot_type: RobotType
    usage_scenario: UsageScenario
    specifications: RobotSpecifications
    owner_id: str = Field(..., min_length=1, max_length=255)

    @field_validator('serial_number')
    @classmethod
    def validate_serial_number(cls, v):
        """Validate serial number format (alphanumeric with hyphens)."""
        if not re.match(r'^[A-Z0-9\-]+$', v.upper()):
            raise ValueError('Serial number must contain only alphanumeric characters and hyphens')
        return v.upper()

    @field_validator('manufacturer_id', 'owner_id')
    @classmethod
    def validate_ids(cls, v):
        """Validate ID format (no special characters except hyphens and underscores)."""
        if not re.match(r'^[A-Za-z0-9\-_]+$', v):
            raise ValueError('ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @model_validator(mode='after')
    def validate_robot_configuration(self):
        """Validate robot configuration based on type and usage scenario."""
        robot_type = self.robot_type
        usage_scenario = self.usage_scenario
        specifications = self.specifications

        if robot_type and usage_scenario and specifications:
            # Validate humanoid robots have appropriate specifications
            if robot_type == RobotType.HUMANOID:
                if specifications.height_cm < 50 or specifications.height_cm > 250:
                    raise ValueError('Humanoid robots must be between 50-250 cm in height')
                if specifications.weight_kg > 200:
                    raise ValueError('Humanoid robots must weigh less than 200 kg')

            # Validate industrial usage requires appropriate certifications
            if usage_scenario == UsageScenario.INDUSTRIAL:
                required_certs = ['ISO 10218', 'IEC 61508']
                if not any(cert in specifications.certifications for cert in required_certs):
                    raise ValueError('Industrial robots must have appropriate safety certifications')

            # Validate medical usage requires specific certifications
            if usage_scenario == UsageScenario.HEALTHCARE:
                if 'IEC 60601' not in specifications.certifications:
                    raise ValueError('Healthcare robots must have IEC 60601 certification')

        return self


class RobotCreate(RobotBase):
    """Schema for creating a robot."""
    pass


class RobotUpdate(BaseModel):
    """Schema for updating a robot."""
    status: Optional[RobotStatus] = None
    usage_scenario: Optional[UsageScenario] = None
    specifications: Optional[RobotSpecifications] = None
    diagnostic_data: Optional[DiagnosticData] = None


class RobotResponse(RobotBase):
    """Schema for robot response."""
    id: UUID
    status: RobotStatus
    registration_date: datetime
    last_diagnostic_date: Optional[datetime] = None
    diagnostic_data: Optional[DiagnosticData] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RobotListResponse(BaseModel):
    """Schema for robot list response."""
    robots: list[RobotResponse]
    total: int
    page: int
    size: int