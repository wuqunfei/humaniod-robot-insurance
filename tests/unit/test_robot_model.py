"""Unit tests for Robot model and schemas."""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from src.models.robot import (
    Robot,
    RobotType,
    RobotStatus,
    UsageScenario,
    RobotSpecifications,
    DiagnosticData,
    RobotBase,
    RobotCreate,
    RobotUpdate,
    RobotResponse
)


class TestRobotSpecifications:
    """Test cases for RobotSpecifications schema."""

    def test_valid_specifications(self):
        """Test creating valid robot specifications."""
        specs = RobotSpecifications(
            height_cm=180.0,
            weight_kg=75.0,
            max_speed_kmh=5.0,
            battery_capacity_kwh=2.5,
            operating_temperature_min=-10.0,
            operating_temperature_max=40.0,
            ip_rating="IP54",
            certifications=["ISO 10218", "IEC 61508"],
            sensors=["camera", "lidar", "accelerometer"],
            actuators=["servo_motor", "linear_actuator"],
            ai_capabilities=["object_recognition", "path_planning"],
            connectivity=["wifi", "bluetooth", "ethernet"]
        )
        
        assert specs.height_cm == 180.0
        assert specs.weight_kg == 75.0
        assert specs.ip_rating == "IP54"
        assert len(specs.certifications) == 2

    def test_invalid_height(self):
        """Test validation of invalid height values."""
        with pytest.raises(ValidationError) as exc_info:
            RobotSpecifications(
                height_cm=0,  # Invalid: must be > 0
                weight_kg=75.0,
                max_speed_kmh=5.0,
                battery_capacity_kwh=2.5,
                operating_temperature_min=-10.0,
                operating_temperature_max=40.0,
                ip_rating="IP54"
            )
        assert "height_cm" in str(exc_info.value)

    def test_invalid_weight(self):
        """Test validation of invalid weight values."""
        with pytest.raises(ValidationError) as exc_info:
            RobotSpecifications(
                height_cm=180.0,
                weight_kg=1500.0,  # Invalid: exceeds max limit
                max_speed_kmh=5.0,
                battery_capacity_kwh=2.5,
                operating_temperature_min=-10.0,
                operating_temperature_max=40.0,
                ip_rating="IP54"
            )
        assert "weight_kg" in str(exc_info.value)

    def test_invalid_ip_rating(self):
        """Test validation of invalid IP rating format."""
        with pytest.raises(ValidationError) as exc_info:
            RobotSpecifications(
                height_cm=180.0,
                weight_kg=75.0,
                max_speed_kmh=5.0,
                battery_capacity_kwh=2.5,
                operating_temperature_min=-10.0,
                operating_temperature_max=40.0,
                ip_rating="INVALID"  # Invalid format
            )
        assert "ip_rating" in str(exc_info.value)

    def test_temperature_range_validation(self):
        """Test validation of temperature range."""
        with pytest.raises(ValidationError) as exc_info:
            RobotSpecifications(
                height_cm=180.0,
                weight_kg=75.0,
                max_speed_kmh=5.0,
                battery_capacity_kwh=2.5,
                operating_temperature_min=40.0,
                operating_temperature_max=30.0,  # Invalid: max < min
                ip_rating="IP54"
            )
        assert "Maximum operating temperature must be greater than minimum" in str(exc_info.value)

    def test_empty_list_items_validation(self):
        """Test validation of empty strings in lists."""
        with pytest.raises(ValidationError) as exc_info:
            RobotSpecifications(
                height_cm=180.0,
                weight_kg=75.0,
                max_speed_kmh=5.0,
                battery_capacity_kwh=2.5,
                operating_temperature_min=-10.0,
                operating_temperature_max=40.0,
                ip_rating="IP54",
                certifications=["ISO 10218", ""]  # Invalid: empty string
            )
        assert "List items must be non-empty strings" in str(exc_info.value)


class TestDiagnosticData:
    """Test cases for DiagnosticData schema."""

    def test_valid_diagnostic_data(self):
        """Test creating valid diagnostic data."""
        diagnostic = DiagnosticData(
            timestamp=datetime.utcnow(),
            battery_level=85.5,
            temperature=25.0,
            error_codes=["E001", "W002"],
            performance_metrics={"cpu_usage": 45.2, "memory_usage": 67.8},
            sensor_readings={"camera": "active", "lidar": "active"},
            operational_hours=1250.5,
            maintenance_alerts=["Battery replacement due in 100 hours"]
        )
        
        assert diagnostic.battery_level == 85.5
        assert diagnostic.temperature == 25.0
        assert len(diagnostic.error_codes) == 2
        assert diagnostic.operational_hours == 1250.5

    def test_invalid_battery_level(self):
        """Test validation of invalid battery level."""
        with pytest.raises(ValidationError) as exc_info:
            DiagnosticData(
                timestamp=datetime.utcnow(),
                battery_level=150.0,  # Invalid: > 100
                temperature=25.0,
                operational_hours=1250.5
            )
        assert "battery_level" in str(exc_info.value)

    def test_negative_operational_hours(self):
        """Test validation of negative operational hours."""
        with pytest.raises(ValidationError) as exc_info:
            DiagnosticData(
                timestamp=datetime.utcnow(),
                battery_level=85.5,
                temperature=25.0,
                operational_hours=-10.0  # Invalid: negative
            )
        assert "operational_hours" in str(exc_info.value)


class TestRobotBase:
    """Test cases for RobotBase schema."""

    def get_valid_specifications(self):
        """Helper method to get valid specifications."""
        return RobotSpecifications(
            height_cm=180.0,
            weight_kg=75.0,
            max_speed_kmh=5.0,
            battery_capacity_kwh=2.5,
            operating_temperature_min=-10.0,
            operating_temperature_max=40.0,
            ip_rating="IP54",
            certifications=["ISO 10218", "IEC 61508"]
        )

    def test_valid_robot_base(self):
        """Test creating valid robot base."""
        robot = RobotBase(
            manufacturer_id="ACME_ROBOTICS",
            model="Humanoid-X1",
            serial_number="HX1-2024-001",
            robot_type=RobotType.HUMANOID,
            usage_scenario=UsageScenario.COMMERCIAL,
            specifications=self.get_valid_specifications(),
            owner_id="customer_123"
        )
        
        assert robot.manufacturer_id == "ACME_ROBOTICS"
        assert robot.model == "Humanoid-X1"
        assert robot.serial_number == "HX1-2024-001"
        assert robot.robot_type == RobotType.HUMANOID

    def test_serial_number_validation(self):
        """Test serial number format validation."""
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="ACME_ROBOTICS",
                model="Humanoid-X1",
                serial_number="HX1@2024#001",  # Invalid: special characters
                robot_type=RobotType.HUMANOID,
                usage_scenario=UsageScenario.COMMERCIAL,
                specifications=self.get_valid_specifications(),
                owner_id="customer_123"
            )
        assert "Serial number must contain only alphanumeric characters and hyphens" in str(exc_info.value)

    def test_serial_number_case_normalization(self):
        """Test serial number is converted to uppercase."""
        robot = RobotBase(
            manufacturer_id="ACME_ROBOTICS",
            model="Humanoid-X1",
            serial_number="hx1-2024-001",  # lowercase
            robot_type=RobotType.HUMANOID,
            usage_scenario=UsageScenario.COMMERCIAL,
            specifications=self.get_valid_specifications(),
            owner_id="customer_123"
        )
        
        assert robot.serial_number == "HX1-2024-001"  # Should be uppercase

    def test_id_validation(self):
        """Test ID format validation."""
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="ACME@ROBOTICS",  # Invalid: special character
                model="Humanoid-X1",
                serial_number="HX1-2024-001",
                robot_type=RobotType.HUMANOID,
                usage_scenario=UsageScenario.COMMERCIAL,
                specifications=self.get_valid_specifications(),
                owner_id="customer_123"
            )
        assert "ID must contain only alphanumeric characters, hyphens, and underscores" in str(exc_info.value)

    def test_humanoid_height_validation(self):
        """Test humanoid robot height validation."""
        specs = self.get_valid_specifications()
        specs.height_cm = 30.0  # Too short for humanoid
        
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="ACME_ROBOTICS",
                model="Humanoid-X1",
                serial_number="HX1-2024-001",
                robot_type=RobotType.HUMANOID,
                usage_scenario=UsageScenario.COMMERCIAL,
                specifications=specs,
                owner_id="customer_123"
            )
        assert "Humanoid robots must be between 50-250 cm in height" in str(exc_info.value)

    def test_humanoid_weight_validation(self):
        """Test humanoid robot weight validation."""
        specs = self.get_valid_specifications()
        specs.weight_kg = 250.0  # Too heavy for humanoid
        
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="ACME_ROBOTICS",
                model="Humanoid-X1",
                serial_number="HX1-2024-001",
                robot_type=RobotType.HUMANOID,
                usage_scenario=UsageScenario.COMMERCIAL,
                specifications=specs,
                owner_id="customer_123"
            )
        assert "Humanoid robots must weigh less than 200 kg" in str(exc_info.value)

    def test_industrial_certification_validation(self):
        """Test industrial robot certification validation."""
        specs = self.get_valid_specifications()
        specs.certifications = ["CE", "FCC"]  # Missing required industrial certifications
        
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="ACME_ROBOTICS",
                model="Industrial-Y2",
                serial_number="IY2-2024-001",
                robot_type=RobotType.INDUSTRIAL,
                usage_scenario=UsageScenario.INDUSTRIAL,
                specifications=specs,
                owner_id="factory_456"
            )
        assert "Industrial robots must have appropriate safety certifications" in str(exc_info.value)

    def test_healthcare_certification_validation(self):
        """Test healthcare robot certification validation."""
        specs = self.get_valid_specifications()
        specs.certifications = ["ISO 10218", "CE"]  # Missing IEC 60601
        
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="MEDICAL_ROBOTICS",
                model="MedBot-Z3",
                serial_number="MZ3-2024-001",
                robot_type=RobotType.MEDICAL,
                usage_scenario=UsageScenario.HEALTHCARE,
                specifications=specs,
                owner_id="hospital_789"
            )
        assert "Healthcare robots must have IEC 60601 certification" in str(exc_info.value)


class TestRobotCreate:
    """Test cases for RobotCreate schema."""

    def test_robot_create_inherits_validation(self):
        """Test that RobotCreate inherits all validation from RobotBase."""
        specs = RobotSpecifications(
            height_cm=180.0,
            weight_kg=75.0,
            max_speed_kmh=5.0,
            battery_capacity_kwh=2.5,
            operating_temperature_min=-10.0,
            operating_temperature_max=40.0,
            ip_rating="IP54",
            certifications=["ISO 10218", "IEC 61508"]
        )
        
        robot_create = RobotCreate(
            manufacturer_id="ACME_ROBOTICS",
            model="Humanoid-X1",
            serial_number="HX1-2024-001",
            robot_type=RobotType.HUMANOID,
            usage_scenario=UsageScenario.COMMERCIAL,
            specifications=specs,
            owner_id="customer_123"
        )
        
        assert robot_create.manufacturer_id == "ACME_ROBOTICS"
        assert robot_create.serial_number == "HX1-2024-001"


class TestRobotUpdate:
    """Test cases for RobotUpdate schema."""

    def test_partial_update(self):
        """Test partial robot update."""
        update = RobotUpdate(
            status=RobotStatus.MAINTENANCE,
            usage_scenario=UsageScenario.RESEARCH
        )
        
        assert update.status == RobotStatus.MAINTENANCE
        assert update.usage_scenario == UsageScenario.RESEARCH
        assert update.specifications is None
        assert update.diagnostic_data is None

    def test_diagnostic_data_update(self):
        """Test updating diagnostic data."""
        diagnostic = DiagnosticData(
            timestamp=datetime.utcnow(),
            battery_level=75.0,
            temperature=28.5,
            operational_hours=1500.0
        )
        
        update = RobotUpdate(diagnostic_data=diagnostic)
        
        assert update.diagnostic_data.battery_level == 75.0
        assert update.diagnostic_data.temperature == 28.5

    def test_specifications_update(self):
        """Test updating specifications."""
        specs = RobotSpecifications(
            height_cm=185.0,
            weight_kg=80.0,
            max_speed_kmh=6.0,
            battery_capacity_kwh=3.0,
            operating_temperature_min=-15.0,
            operating_temperature_max=45.0,
            ip_rating="IP65",
            certifications=["ISO 10218", "IEC 61508", "CE"]
        )
        
        update = RobotUpdate(specifications=specs)
        
        assert update.specifications.height_cm == 185.0
        assert update.specifications.ip_rating == "IP65"
        assert len(update.specifications.certifications) == 3


class TestRobotResponse:
    """Test cases for RobotResponse schema."""

    def test_robot_response_creation(self):
        """Test creating robot response with all fields."""
        specs = RobotSpecifications(
            height_cm=180.0,
            weight_kg=75.0,
            max_speed_kmh=5.0,
            battery_capacity_kwh=2.5,
            operating_temperature_min=-10.0,
            operating_temperature_max=40.0,
            ip_rating="IP54",
            certifications=["ISO 10218", "IEC 61508"]
        )
        
        diagnostic = DiagnosticData(
            timestamp=datetime.utcnow(),
            battery_level=85.0,
            temperature=25.0,
            operational_hours=1000.0
        )
        
        now = datetime.utcnow()
        robot_id = uuid4()
        
        response = RobotResponse(
            id=robot_id,
            manufacturer_id="ACME_ROBOTICS",
            model="Humanoid-X1",
            serial_number="HX1-2024-001",
            robot_type=RobotType.HUMANOID,
            usage_scenario=UsageScenario.COMMERCIAL,
            specifications=specs,
            owner_id="customer_123",
            status=RobotStatus.ACTIVE,
            registration_date=now,
            last_diagnostic_date=now,
            diagnostic_data=diagnostic,
            created_at=now,
            updated_at=now
        )
        
        assert response.id == robot_id
        assert response.status == RobotStatus.ACTIVE
        assert response.diagnostic_data.battery_level == 85.0
        assert response.registration_date == now


class TestRobotBusinessRules:
    """Test cases for robot business rules and edge cases."""

    def test_companion_robot_specifications(self):
        """Test companion robot with appropriate specifications."""
        specs = RobotSpecifications(
            height_cm=60.0,  # Smaller companion robot
            weight_kg=15.0,
            max_speed_kmh=2.0,
            battery_capacity_kwh=0.5,
            operating_temperature_min=0.0,
            operating_temperature_max=35.0,
            ip_rating="IP42",
            certifications=["CE", "FCC"],
            sensors=["camera", "microphone", "touch_sensor"],
            ai_capabilities=["speech_recognition", "emotion_detection"]
        )
        
        robot = RobotBase(
            manufacturer_id="COMPANION_TECH",
            model="FriendBot-A1",
            serial_number="FB1-2024-001",
            robot_type=RobotType.COMPANION,
            usage_scenario=UsageScenario.DOMESTIC,
            specifications=specs,
            owner_id="family_001"
        )
        
        assert robot.robot_type == RobotType.COMPANION
        assert robot.usage_scenario == UsageScenario.DOMESTIC

    def test_service_robot_with_valid_certifications(self):
        """Test service robot with appropriate certifications."""
        specs = RobotSpecifications(
            height_cm=120.0,
            weight_kg=45.0,
            max_speed_kmh=8.0,
            battery_capacity_kwh=5.0,
            operating_temperature_min=-5.0,
            operating_temperature_max=50.0,
            ip_rating="IP54",
            certifications=["CE", "FCC", "UL"],
            sensors=["lidar", "camera", "ultrasonic"],
            ai_capabilities=["navigation", "object_recognition"]
        )
        
        robot = RobotBase(
            manufacturer_id="SERVICE_ROBOTICS",
            model="ServiceBot-S2",
            serial_number="SB2-2024-001",
            robot_type=RobotType.SERVICE,
            usage_scenario=UsageScenario.COMMERCIAL,
            specifications=specs,
            owner_id="business_002"
        )
        
        assert robot.robot_type == RobotType.SERVICE
        assert robot.specifications.max_speed_kmh == 8.0

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are caught."""
        with pytest.raises(ValidationError) as exc_info:
            RobotBase(
                manufacturer_id="INVALID@ID",  # Invalid ID
                model="",  # Empty model
                serial_number="invalid_serial!",  # Invalid serial
                robot_type=RobotType.HUMANOID,
                usage_scenario=UsageScenario.INDUSTRIAL,
                specifications=RobotSpecifications(
                    height_cm=0,  # Invalid height
                    weight_kg=300,  # Invalid weight for humanoid
                    max_speed_kmh=5.0,
                    battery_capacity_kwh=2.5,
                    operating_temperature_min=40.0,
                    operating_temperature_max=30.0,  # Invalid temperature range
                    ip_rating="INVALID",  # Invalid IP rating
                    certifications=[]  # Missing required certifications
                ),
                owner_id="owner_123"
            )
        
        error_str = str(exc_info.value)
        # Should contain multiple validation errors
        assert "manufacturer_id" in error_str or "model" in error_str or "serial_number" in error_str