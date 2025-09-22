"""Simple unit tests for Robot model schemas without database dependencies."""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from src.models.robot import (
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])