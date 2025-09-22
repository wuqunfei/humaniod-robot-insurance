"""Unit tests for Claim model and schemas."""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from src.models.claim import (
    Claim,
    IncidentType,
    ClaimStatus,
    ClaimPriority,
    DamageAssessment,
    DocumentType,
    AdjusterNote,
    SupportingDocument,
    ThirdPartyDetails,
    ClaimBase,
    ClaimCreate,
    ClaimUpdate,
    ClaimResponse,
    ClaimStatusUpdate,
    ClaimAssessmentRequest,
    ClaimSearchFilters
)


class TestAdjusterNote:
    """Test cases for AdjusterNote schema."""

    def test_valid_adjuster_note(self):
        """Test creating valid adjuster note."""
        note = AdjusterNote(
            timestamp=datetime.utcnow(),
            adjuster_id="adjuster_123",
            note="Initial assessment completed. Robot shows signs of water damage to main circuit board.",
            note_type="assessment"
        )
        
        assert note.adjuster_id == "adjuster_123"
        assert "water damage" in note.note
        assert note.note_type == "assessment"

    def test_invalid_adjuster_id(self):
        """Test validation of invalid adjuster ID."""
        with pytest.raises(ValidationError) as exc_info:
            AdjusterNote(
                timestamp=datetime.utcnow(),
                adjuster_id="adjuster@123",  # Invalid: special character
                note="Assessment note with sufficient length for validation",
                note_type="general"
            )
        assert "Adjuster ID must contain only alphanumeric characters" in str(exc_info.value)

    def test_note_too_short(self):
        """Test validation of note too short."""
        with pytest.raises(ValidationError) as exc_info:
            AdjusterNote(
                timestamp=datetime.utcnow(),
                adjuster_id="adjuster_123",
                note="Short",  # Invalid: too short
                note_type="general"
            )
        assert "note" in str(exc_info.value)

    def test_empty_note_validation(self):
        """Test validation of empty note."""
        with pytest.raises(ValidationError) as exc_info:
            AdjusterNote(
                timestamp=datetime.utcnow(),
                adjuster_id="adjuster_123",
                note="   ",  # Invalid: empty after strip - too short
                note_type="general"
            )
        assert "String should have at least 10 characters" in str(exc_info.value)


class TestSupportingDocument:
    """Test cases for SupportingDocument schema."""

    def test_valid_supporting_document(self):
        """Test creating valid supporting document."""
        doc = SupportingDocument(
            document_id="doc_12345",
            document_type=DocumentType.PHOTOS,
            filename="robot_damage_photo.jpg",
            file_size=1024000,  # 1MB
            upload_date=datetime.utcnow(),
            uploaded_by="customer_456",
            description="Photo showing damage to robot's left arm"
        )
        
        assert doc.document_type == DocumentType.PHOTOS
        assert doc.filename == "robot_damage_photo.jpg"
        assert doc.file_size == 1024000

    def test_invalid_filename(self):
        """Test validation of invalid filename."""
        with pytest.raises(ValidationError) as exc_info:
            SupportingDocument(
                document_id="doc_12345",
                document_type=DocumentType.DIAGNOSTIC_DATA,
                filename="../../../etc/passwd",  # Invalid: path traversal
                file_size=5000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_456"
            )
        assert "Filename contains invalid characters" in str(exc_info.value)

    def test_file_size_too_large(self):
        """Test validation of file size too large."""
        with pytest.raises(ValidationError) as exc_info:
            SupportingDocument(
                document_id="doc_12345",
                document_type=DocumentType.REPAIR_ESTIMATE,
                filename="large_document.pdf",
                file_size=60 * 1024 * 1024,  # 60MB - exceeds 50MB limit
                upload_date=datetime.utcnow(),
                uploaded_by="adjuster_789"
            )
        assert "File size cannot exceed 50MB" in str(exc_info.value)

    def test_zero_file_size(self):
        """Test validation of zero file size."""
        with pytest.raises(ValidationError) as exc_info:
            SupportingDocument(
                document_id="doc_12345",
                document_type=DocumentType.INVOICE,
                filename="empty_file.txt",
                file_size=0,  # Invalid: must be > 0
                upload_date=datetime.utcnow(),
                uploaded_by="customer_456"
            )
        assert "file_size" in str(exc_info.value)


class TestThirdPartyDetails:
    """Test cases for ThirdPartyDetails schema."""

    def test_valid_third_party_details(self):
        """Test creating valid third party details."""
        details = ThirdPartyDetails(
            party_type="person",
            contact_name="John Smith",
            contact_phone="+1-555-123-4567",
            contact_email="john.smith@email.com",
            insurance_company="ABC Insurance Co.",
            policy_number="POL-123456789",
            damage_description="Minor scratches on vehicle door",
            estimated_liability=Decimal('2500.00')
        )
        
        assert details.party_type == "person"
        assert details.contact_name == "John Smith"
        assert details.estimated_liability == Decimal('2500.00')

    def test_invalid_phone_format(self):
        """Test validation of invalid phone format."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyDetails(
                party_type="person",
                contact_phone="invalid-phone!@#",  # Invalid: special characters
                estimated_liability=Decimal('1000.00')
            )
        assert "Invalid phone number format" in str(exc_info.value)

    def test_invalid_email_format(self):
        """Test validation of invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            ThirdPartyDetails(
                party_type="property",
                contact_email="invalid-email",  # Invalid: no @ or domain
                estimated_liability=Decimal('5000.00')
            )
        assert "Invalid email format" in str(exc_info.value)

    def test_valid_phone_formats(self):
        """Test various valid phone formats."""
        valid_phones = [
            "+1-555-123-4567",
            "555 123 4567",
            "(555) 123-4567",
            "+44 20 7946 0958",
            "555.123.4567"
        ]
        
        for phone in valid_phones:
            details = ThirdPartyDetails(
                party_type="person",
                contact_phone=phone,
                estimated_liability=Decimal('1000.00')
            )
            assert details.contact_phone == phone


class TestClaimBase:
    """Test cases for ClaimBase schema."""

    def get_valid_third_party_details(self):
        """Helper method to get valid third party details."""
        return ThirdPartyDetails(
            party_type="vehicle",
            contact_name="Jane Doe",
            contact_phone="555-987-6543",
            estimated_liability=Decimal('3000.00')
        )

    def test_valid_claim_base(self):
        """Test creating valid claim base."""
        claim = ClaimBase(
            policy_id=uuid4(),
            robot_id=uuid4(),
            customer_id="customer_789",
            incident_type=IncidentType.PHYSICAL_DAMAGE,
            incident_date=date.today() - timedelta(days=1),
            incident_description="Robot fell down stairs causing damage to left leg actuator and sensor array",
            incident_location="Customer's home, main staircase",
            estimated_damage_amount=Decimal('5000.00'),
            third_party_involved=False
        )
        
        assert claim.incident_type == IncidentType.PHYSICAL_DAMAGE
        assert "fell down stairs" in claim.incident_description
        assert claim.third_party_involved is False

    def test_invalid_customer_id(self):
        """Test validation of invalid customer ID."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer@789",  # Invalid: special character
                incident_type=IncidentType.MALFUNCTION,
                incident_date=date.today() - timedelta(days=2),
                incident_description="Robot malfunctioned during operation causing system failure"
            )
        assert "Customer ID must contain only alphanumeric characters" in str(exc_info.value)

    def test_incident_description_too_short(self):
        """Test validation of incident description too short."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.THEFT,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Stolen"  # Invalid: too short
            )
        assert "incident_description" in str(exc_info.value)

    def test_future_incident_date(self):
        """Test validation of future incident date."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.FIRE_DAMAGE,
                incident_date=date.today() + timedelta(days=1),  # Invalid: future date
                incident_description="Fire damage to robot's main processing unit and battery compartment"
            )
        assert "Incident date cannot be in the future" in str(exc_info.value)

    def test_excessive_damage_amount(self):
        """Test validation of excessive damage amount."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.ELECTRICAL_DAMAGE,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Electrical surge caused extensive damage to robot's internal systems",
                estimated_damage_amount=Decimal('50000000.00')  # Invalid: exceeds 10M limit
            )
        assert "Estimated damage amount exceeds maximum allowed" in str(exc_info.value)

    def test_third_party_consistency_missing_details(self):
        """Test validation of third party consistency - missing details."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.THIRD_PARTY_LIABILITY,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Robot collided with person causing injury requiring medical attention",
                third_party_involved=True,
                third_party_details=None  # Invalid: missing when third party involved
            )
        assert "Third party details must be provided when third party is involved" in str(exc_info.value)

    def test_third_party_consistency_unexpected_details(self):
        """Test validation of third party consistency - unexpected details."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.SOFTWARE_FAILURE,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Software failure caused robot to stop responding to commands",
                third_party_involved=False,
                third_party_details=self.get_valid_third_party_details()  # Invalid: provided when not involved
            )
        assert "Third party details should not be provided when no third party is involved" in str(exc_info.value)

    def test_valid_third_party_claim(self):
        """Test valid claim with third party involvement."""
        claim = ClaimBase(
            policy_id=uuid4(),
            robot_id=uuid4(),
            customer_id="customer_789",
            incident_type=IncidentType.THIRD_PARTY_LIABILITY,
            incident_date=date.today() - timedelta(days=1),
            incident_description="Robot accidentally bumped into parked vehicle causing minor damage to paint",
            third_party_involved=True,
            third_party_details=self.get_valid_third_party_details()
        )
        
        assert claim.third_party_involved is True
        assert claim.third_party_details is not None
        assert claim.third_party_details.estimated_liability == Decimal('3000.00')


class TestClaimCreate:
    """Test cases for ClaimCreate schema."""

    def get_valid_supporting_documents(self):
        """Helper method to get valid supporting documents."""
        return [
            SupportingDocument(
                document_id="doc_001",
                document_type=DocumentType.PHOTOS,
                filename="damage_photo_1.jpg",
                file_size=1024000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_789"
            ),
            SupportingDocument(
                document_id="doc_002",
                document_type=DocumentType.DIAGNOSTIC_DATA,
                filename="robot_diagnostics.json",
                file_size=50000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_789"
            )
        ]

    def test_valid_claim_create(self):
        """Test creating valid claim create."""
        claim = ClaimCreate(
            policy_id=uuid4(),
            robot_id=uuid4(),
            customer_id="customer_789",
            incident_type=IncidentType.WATER_DAMAGE,
            incident_date=date.today() - timedelta(days=2),
            incident_description="Water leak in ceiling caused extensive damage to robot's electronics",
            incident_location="Office building, 3rd floor",
            estimated_damage_amount=Decimal('8000.00'),
            third_party_involved=False,
            priority=ClaimPriority.HIGH,
            supporting_documents=self.get_valid_supporting_documents(),
            diagnostic_data={"battery_level": 0, "system_status": "error", "error_codes": ["E001", "E005"]}
        )
        
        assert claim.priority == ClaimPriority.HIGH
        assert len(claim.supporting_documents) == 2
        assert claim.diagnostic_data["system_status"] == "error"

    def test_too_many_supporting_documents(self):
        """Test validation of too many supporting documents."""
        # Create 21 documents (exceeds limit of 20)
        docs = []
        for i in range(21):
            docs.append(SupportingDocument(
                document_id=f"doc_{i:03d}",
                document_type=DocumentType.PHOTOS,
                filename=f"photo_{i}.jpg",
                file_size=100000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_789"
            ))
        
        with pytest.raises(ValidationError) as exc_info:
            ClaimCreate(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.OPERATOR_ERROR,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Operator error caused robot to collide with wall damaging sensors",
                supporting_documents=docs
            )
        assert "Cannot attach more than 20 supporting documents" in str(exc_info.value)

    def test_duplicate_document_ids(self):
        """Test validation of duplicate document IDs."""
        docs = [
            SupportingDocument(
                document_id="doc_001",  # Duplicate ID
                document_type=DocumentType.PHOTOS,
                filename="photo_1.jpg",
                file_size=100000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_789"
            ),
            SupportingDocument(
                document_id="doc_001",  # Duplicate ID
                document_type=DocumentType.INCIDENT_REPORT,
                filename="report.pdf",
                file_size=200000,
                upload_date=datetime.utcnow(),
                uploaded_by="customer_789"
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            ClaimCreate(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id="customer_789",
                incident_type=IncidentType.CYBER_SECURITY_BREACH,
                incident_date=date.today() - timedelta(days=1),
                incident_description="Security breach compromised robot's control systems and data",
                supporting_documents=docs
            )
        assert "Duplicate document IDs are not allowed" in str(exc_info.value)


class TestClaimStatusUpdate:
    """Test cases for ClaimStatusUpdate schema."""

    def test_valid_status_update(self):
        """Test creating valid status update."""
        update = ClaimStatusUpdate(
            claim_id=uuid4(),
            new_status=ClaimStatus.APPROVED,
            adjuster_id="adjuster_456",
            notes="Claim approved after thorough investigation. All documentation verified."
        )
        
        assert update.new_status == ClaimStatus.APPROVED
        assert update.adjuster_id == "adjuster_456"
        assert "approved after thorough" in update.notes

    def test_settled_status_requires_settlement_amount(self):
        """Test validation that settled status requires settlement amount."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimStatusUpdate(
                claim_id=uuid4(),
                new_status=ClaimStatus.SETTLED,
                adjuster_id="adjuster_456",
                notes="Claim settled with customer agreement on repair costs",
                settlement_amount=None  # Invalid: required for settled status
            )
        assert "Settlement amount is required when status is set to settled" in str(exc_info.value)

    def test_non_settled_status_with_settlement_amount(self):
        """Test validation that non-settled status should not have settlement amount."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimStatusUpdate(
                claim_id=uuid4(),
                new_status=ClaimStatus.APPROVED,
                adjuster_id="adjuster_456",
                notes="Claim approved pending final documentation review",
                settlement_amount=Decimal('5000.00')  # Invalid: not settled status
            )
        assert "Settlement amount should only be provided when status is settled" in str(exc_info.value)

    def test_valid_settled_status_update(self):
        """Test valid settled status update."""
        update = ClaimStatusUpdate(
            claim_id=uuid4(),
            new_status=ClaimStatus.SETTLED,
            adjuster_id="adjuster_456",
            notes="Claim settled. Payment processed for approved repair costs minus deductible.",
            settlement_amount=Decimal('4500.00')
        )
        
        assert update.new_status == ClaimStatus.SETTLED
        assert update.settlement_amount == Decimal('4500.00')


class TestClaimAssessmentRequest:
    """Test cases for ClaimAssessmentRequest schema."""

    def test_valid_assessment_request(self):
        """Test creating valid assessment request."""
        assessment = ClaimAssessmentRequest(
            claim_id=uuid4(),
            adjuster_id="adjuster_789",
            damage_assessment=DamageAssessment.MODERATE,
            assessment_notes="Moderate damage to robot's mobility system. Left leg actuator needs replacement.",
            repair_estimate=Decimal('3500.00'),
            replacement_cost=Decimal('15000.00'),
            recommended_action="Proceed with repair as cost is significantly less than replacement"
        )
        
        assert assessment.damage_assessment == DamageAssessment.MODERATE
        assert assessment.repair_estimate == Decimal('3500.00')
        assert "Proceed with repair" in assessment.recommended_action

    def test_total_loss_assessment_validation(self):
        """Test validation of total loss assessment."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimAssessmentRequest(
                claim_id=uuid4(),
                adjuster_id="adjuster_789",
                damage_assessment=DamageAssessment.TOTAL_LOSS,
                assessment_notes="Robot is beyond economical repair due to extensive damage",
                repair_estimate=Decimal('20000.00'),  # Invalid: should not provide for total loss
                replacement_cost=Decimal('25000.00'),
                recommended_action="Recommend total loss settlement"
            )
        assert "Repair estimate should not be provided for total loss assessment" in str(exc_info.value)

    def test_total_loss_missing_replacement_cost(self):
        """Test validation of total loss missing replacement cost."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimAssessmentRequest(
                claim_id=uuid4(),
                adjuster_id="adjuster_789",
                damage_assessment=DamageAssessment.TOTAL_LOSS,
                assessment_notes="Robot is beyond economical repair due to fire damage",
                replacement_cost=None,  # Invalid: required for total loss
                recommended_action="Recommend total loss settlement based on replacement value"
            )
        assert "Replacement cost is required for total loss assessment" in str(exc_info.value)

    def test_valid_total_loss_assessment(self):
        """Test valid total loss assessment."""
        assessment = ClaimAssessmentRequest(
            claim_id=uuid4(),
            adjuster_id="adjuster_789",
            damage_assessment=DamageAssessment.TOTAL_LOSS,
            assessment_notes="Extensive fire damage has destroyed all major components. Robot is not economically repairable.",
            replacement_cost=Decimal('45000.00'),
            recommended_action="Recommend total loss settlement at current market value"
        )
        
        assert assessment.damage_assessment == DamageAssessment.TOTAL_LOSS
        assert assessment.replacement_cost == Decimal('45000.00')
        assert assessment.repair_estimate is None


class TestClaimSearchFilters:
    """Test cases for ClaimSearchFilters schema."""

    def test_valid_search_filters(self):
        """Test creating valid search filters."""
        filters = ClaimSearchFilters(
            status=[ClaimStatus.SUBMITTED, ClaimStatus.UNDER_REVIEW],
            incident_type=[IncidentType.PHYSICAL_DAMAGE, IncidentType.MALFUNCTION],
            priority=[ClaimPriority.HIGH, ClaimPriority.URGENT],
            adjuster_id="adjuster_123",
            incident_date_from=date.today() - timedelta(days=30),
            incident_date_to=date.today(),
            min_damage_amount=Decimal('1000.00'),
            max_damage_amount=Decimal('10000.00')
        )
        
        assert len(filters.status) == 2
        assert ClaimStatus.SUBMITTED in filters.status
        assert filters.adjuster_id == "adjuster_123"

    def test_invalid_incident_date_range(self):
        """Test validation of invalid incident date range."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimSearchFilters(
                incident_date_from=date.today(),
                incident_date_to=date.today() - timedelta(days=1)  # Invalid: from > to
            )
        assert "Incident date from cannot be after incident date to" in str(exc_info.value)

    def test_invalid_damage_amount_range(self):
        """Test validation of invalid damage amount range."""
        with pytest.raises(ValidationError) as exc_info:
            ClaimSearchFilters(
                min_damage_amount=Decimal('5000.00'),
                max_damage_amount=Decimal('1000.00')  # Invalid: min > max
            )
        assert "Minimum damage amount cannot be greater than maximum damage amount" in str(exc_info.value)

    def test_invalid_reported_date_range(self):
        """Test validation of invalid reported date range."""
        now = datetime.utcnow()
        with pytest.raises(ValidationError) as exc_info:
            ClaimSearchFilters(
                reported_date_from=now,
                reported_date_to=now - timedelta(hours=1)  # Invalid: from > to
            )
        assert "Reported date from cannot be after reported date to" in str(exc_info.value)


class TestClaimBusinessRules:
    """Test cases for claim business rules and edge cases."""

    def test_cyber_security_breach_claim(self):
        """Test cyber security breach claim with appropriate details."""
        claim = ClaimBase(
            policy_id=uuid4(),
            robot_id=uuid4(),
            customer_id="enterprise_client_001",
            incident_type=IncidentType.CYBER_SECURITY_BREACH,
            incident_date=date.today() - timedelta(days=1),
            incident_description="Unauthorized access detected in robot's control system. Malicious code installed causing data exfiltration and system compromise.",
            incident_location="Corporate headquarters, robotics lab",
            estimated_damage_amount=Decimal('25000.00'),
            third_party_involved=False
        )
        
        assert claim.incident_type == IncidentType.CYBER_SECURITY_BREACH
        assert "Unauthorized access" in claim.incident_description
        assert claim.estimated_damage_amount == Decimal('25000.00')

    def test_operator_error_with_third_party_liability(self):
        """Test operator error claim with third party liability."""
        third_party = ThirdPartyDetails(
            party_type="property",
            contact_name="Building Manager",
            contact_phone="555-111-2222",
            contact_email="manager@building.com",
            damage_description="Robot collision caused damage to glass door and frame",
            estimated_liability=Decimal('1500.00')
        )
        
        claim = ClaimBase(
            policy_id=uuid4(),
            robot_id=uuid4(),
            customer_id="commercial_user_456",
            incident_type=IncidentType.OPERATOR_ERROR,
            incident_date=date.today() - timedelta(days=3),
            incident_description="Operator programming error caused robot to move outside designated area, resulting in collision with building infrastructure.",
            incident_location="Office complex, main lobby",
            estimated_damage_amount=Decimal('2500.00'),
            third_party_involved=True,
            third_party_details=third_party
        )
        
        assert claim.incident_type == IncidentType.OPERATOR_ERROR
        assert claim.third_party_involved is True
        assert claim.third_party_details.estimated_liability == Decimal('1500.00')

    def test_multiple_incident_types_coverage(self):
        """Test various incident types with appropriate validations."""
        incident_types = [
            IncidentType.PHYSICAL_DAMAGE,
            IncidentType.MALFUNCTION,
            IncidentType.THEFT,
            IncidentType.FIRE_DAMAGE,
            IncidentType.WATER_DAMAGE,
            IncidentType.ELECTRICAL_DAMAGE,
            IncidentType.SOFTWARE_FAILURE
        ]
        
        for incident_type in incident_types:
            claim = ClaimBase(
                policy_id=uuid4(),
                robot_id=uuid4(),
                customer_id=f"customer_{incident_type.value}",
                incident_type=incident_type,
                incident_date=date.today() - timedelta(days=1),
                incident_description=f"Incident of type {incident_type.value} occurred causing damage to robot systems and requiring immediate attention.",
                estimated_damage_amount=Decimal('3000.00'),
                third_party_involved=False
            )
            
            assert claim.incident_type == incident_type
            assert claim.customer_id == f"customer_{incident_type.value}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])