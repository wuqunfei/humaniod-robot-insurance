"""Unit tests for Policy model and schemas."""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from src.models.policy import (
    Policy,
    CoverageType,
    PolicyStatus,
    PaymentFrequency,
    RiskLevel,
    CoverageDetails,
    PolicyTerms,
    PolicyBase,
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyQuoteRequest,
    PolicyQuoteResponse,
    PolicyRenewalRequest,
    PolicyCancellationRequest
)


class TestCoverageDetails:
    """Test cases for CoverageDetails schema."""

    def test_valid_coverage_details(self):
        """Test creating valid coverage details."""
        coverage = CoverageDetails(
            coverage_type=CoverageType.PHYSICAL_DAMAGE,
            coverage_limit=Decimal('50000.00'),
            deductible=Decimal('1000.00'),
            premium_portion=Decimal('1200.00'),
            exclusions=["Normal wear and tear", "Intentional damage"],
            conditions=["Annual inspection required", "Proper maintenance records"]
        )
        
        assert coverage.coverage_type == CoverageType.PHYSICAL_DAMAGE
        assert coverage.coverage_limit == Decimal('50000.00')
        assert coverage.deductible == Decimal('1000.00')
        assert len(coverage.exclusions) == 2

    def test_invalid_negative_amounts(self):
        """Test validation of negative monetary amounts."""
        with pytest.raises(ValidationError) as exc_info:
            CoverageDetails(
                coverage_type=CoverageType.LIABILITY,
                coverage_limit=Decimal('-1000.00'),  # Invalid: negative
                deductible=Decimal('500.00'),
                premium_portion=Decimal('800.00')
            )
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_invalid_decimal_precision(self):
        """Test validation of decimal precision."""
        with pytest.raises(ValidationError) as exc_info:
            CoverageDetails(
                coverage_type=CoverageType.CYBER_SECURITY,
                coverage_limit=Decimal('25000.123'),  # Invalid: too many decimal places
                deductible=Decimal('500.00'),
                premium_portion=Decimal('600.00')
            )
        assert "cannot have more than 2 decimal places" in str(exc_info.value)

    def test_empty_exclusions_validation(self):
        """Test validation of empty strings in exclusions."""
        with pytest.raises(ValidationError) as exc_info:
            CoverageDetails(
                coverage_type=CoverageType.BUSINESS_INTERRUPTION,
                coverage_limit=Decimal('10000.00'),
                deductible=Decimal('250.00'),
                premium_portion=Decimal('400.00'),
                exclusions=["Valid exclusion", ""]  # Invalid: empty string
            )
        assert "List items must be non-empty strings" in str(exc_info.value)


class TestPolicyTerms:
    """Test cases for PolicyTerms schema."""

    def get_valid_coverage_details(self):
        """Helper method to get valid coverage details."""
        return [
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,
                coverage_limit=Decimal('50000.00'),
                deductible=Decimal('1000.00'),
                premium_portion=Decimal('1200.00')
            ),
            CoverageDetails(
                coverage_type=CoverageType.LIABILITY,
                coverage_limit=Decimal('100000.00'),
                deductible=Decimal('500.00'),
                premium_portion=Decimal('800.00')
            )
        ]

    def test_valid_policy_terms(self):
        """Test creating valid policy terms."""
        terms = PolicyTerms(
            coverage_details=self.get_valid_coverage_details(),
            policy_conditions=["Robot must be registered", "Annual safety inspection required"],
            exclusions=["Acts of war", "Nuclear incidents"],
            claim_procedures=["Report within 24 hours", "Provide diagnostic data"],
            cancellation_terms="30 days written notice required for cancellation",
            renewal_terms="Automatic renewal unless cancelled 30 days prior",
            jurisdiction="US-CA",
            regulatory_compliance={"DOT": "Compliant", "FCC": "Certified"}
        )
        
        assert len(terms.coverage_details) == 2
        assert terms.jurisdiction == "US-CA"
        assert len(terms.policy_conditions) == 2

    def test_invalid_jurisdiction_format(self):
        """Test validation of invalid jurisdiction format."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyTerms(
                coverage_details=self.get_valid_coverage_details(),
                cancellation_terms="30 days written notice required",
                renewal_terms="Automatic renewal unless cancelled",
                jurisdiction="INVALID_FORMAT"  # Invalid format - too long
            )
        assert "String should have at most 10 characters" in str(exc_info.value)

    def test_invalid_jurisdiction_regex(self):
        """Test validation of invalid jurisdiction regex format."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyTerms(
                coverage_details=self.get_valid_coverage_details(),
                cancellation_terms="30 days written notice required",
                renewal_terms="Automatic renewal unless cancelled",
                jurisdiction="US123"  # Invalid format - contains numbers
            )
        assert "Jurisdiction must be in format like" in str(exc_info.value)

    def test_duplicate_coverage_types(self):
        """Test validation of duplicate coverage types."""
        duplicate_coverage = [
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,
                coverage_limit=Decimal('50000.00'),
                deductible=Decimal('1000.00'),
                premium_portion=Decimal('1200.00')
            ),
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,  # Duplicate
                coverage_limit=Decimal('25000.00'),
                deductible=Decimal('500.00'),
                premium_portion=Decimal('600.00')
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            PolicyTerms(
                coverage_details=duplicate_coverage,
                cancellation_terms="30 days written notice required",
                renewal_terms="Automatic renewal unless cancelled",
                jurisdiction="US"
            )
        assert "Duplicate coverage types are not allowed" in str(exc_info.value)

    def test_comprehensive_coverage_validation(self):
        """Test validation of comprehensive coverage rules."""
        comprehensive_with_others = [
            CoverageDetails(
                coverage_type=CoverageType.COMPREHENSIVE,
                coverage_limit=Decimal('100000.00'),
                deductible=Decimal('1000.00'),
                premium_portion=Decimal('2000.00')
            ),
            CoverageDetails(
                coverage_type=CoverageType.LIABILITY,  # Invalid with comprehensive
                coverage_limit=Decimal('50000.00'),
                deductible=Decimal('500.00'),
                premium_portion=Decimal('800.00')
            )
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            PolicyTerms(
                coverage_details=comprehensive_with_others,
                cancellation_terms="30 days written notice required",
                renewal_terms="Automatic renewal unless cancelled",
                jurisdiction="US"
            )
        assert "Comprehensive coverage cannot be combined with other coverage types" in str(exc_info.value)


class TestPolicyBase:
    """Test cases for PolicyBase schema."""

    def get_valid_policy_terms(self):
        """Helper method to get valid policy terms."""
        coverage_details = [
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,
                coverage_limit=Decimal('50000.00'),
                deductible=Decimal('1000.00'),
                premium_portion=Decimal('1200.00')
            )
        ]
        
        return PolicyTerms(
            coverage_details=coverage_details,
            cancellation_terms="30 days written notice required for cancellation",
            renewal_terms="Automatic renewal unless cancelled 30 days prior",
            jurisdiction="US"
        )

    def test_valid_policy_base(self):
        """Test creating valid policy base."""
        robot_id = uuid4()
        effective_date = date.today()
        expiration_date = effective_date + timedelta(days=365)
        
        policy = PolicyBase(
            robot_id=robot_id,
            customer_id="customer_123",
            coverage_types=[CoverageType.PHYSICAL_DAMAGE],
            premium_amount=Decimal('1200.00'),
            deductible_amount=Decimal('1000.00'),
            coverage_limit=Decimal('50000.00'),
            effective_date=effective_date,
            expiration_date=expiration_date,
            payment_frequency=PaymentFrequency.ANNUAL,
            risk_level=RiskLevel.MEDIUM,
            terms_and_conditions=self.get_valid_policy_terms(),
            auto_renewal=True
        )
        
        assert policy.robot_id == robot_id
        assert policy.customer_id == "customer_123"
        assert policy.premium_amount == Decimal('1200.00')
        assert policy.risk_level == RiskLevel.MEDIUM

    def test_invalid_customer_id(self):
        """Test validation of invalid customer ID."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer@123",  # Invalid: special character
                coverage_types=[CoverageType.LIABILITY],
                premium_amount=Decimal('1500.00'),
                deductible_amount=Decimal('500.00'),
                coverage_limit=Decimal('75000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=365),
                risk_level=RiskLevel.LOW,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Customer ID must contain only alphanumeric characters" in str(exc_info.value)

    def test_invalid_date_relationship(self):
        """Test validation of invalid date relationships."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.CYBER_SECURITY],
                premium_amount=Decimal('800.00'),
                deductible_amount=Decimal('250.00'),
                coverage_limit=Decimal('25000.00'),
                effective_date=date.today(),
                expiration_date=date.today() - timedelta(days=1),  # Invalid: before effective
                risk_level=RiskLevel.HIGH,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Expiration date must be after effective date" in str(exc_info.value)

    def test_policy_term_too_short(self):
        """Test validation of policy term too short."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.BUSINESS_INTERRUPTION],
                premium_amount=Decimal('600.00'),
                deductible_amount=Decimal('200.00'),
                coverage_limit=Decimal('15000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=15),  # Invalid: too short
                risk_level=RiskLevel.MEDIUM,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Policy term must be at least 30 days" in str(exc_info.value)

    def test_deductible_too_high(self):
        """Test validation of deductible too high compared to coverage."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.PRODUCT_RECALL],
                premium_amount=Decimal('1000.00'),
                deductible_amount=Decimal('30000.00'),  # Invalid: > 50% of coverage
                coverage_limit=Decimal('50000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=365),
                risk_level=RiskLevel.LOW,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Deductible cannot exceed 50% of coverage limit" in str(exc_info.value)

    def test_premium_too_high(self):
        """Test validation of premium too high compared to coverage."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.LIABILITY],
                premium_amount=Decimal('25000.00'),  # Invalid: > 20% of coverage
                deductible_amount=Decimal('1000.00'),
                coverage_limit=Decimal('100000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=365),
                risk_level=RiskLevel.CRITICAL,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Premium amount exceeds reasonable threshold" in str(exc_info.value)

    def test_premium_too_low_for_risk_level(self):
        """Test validation of premium too low for risk level."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.COMPREHENSIVE],
                premium_amount=Decimal('50.00'),  # Invalid: too low for critical risk
                deductible_amount=Decimal('500.00'),
                coverage_limit=Decimal('75000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=365),
                risk_level=RiskLevel.CRITICAL,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Premium too low for critical risk level" in str(exc_info.value)

    def test_comprehensive_coverage_validation(self):
        """Test validation of comprehensive coverage rules."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyBase(
                robot_id=uuid4(),
                customer_id="customer_123",
                coverage_types=[CoverageType.COMPREHENSIVE, CoverageType.LIABILITY],  # Invalid combination
                premium_amount=Decimal('2000.00'),
                deductible_amount=Decimal('1000.00'),
                coverage_limit=Decimal('100000.00'),
                effective_date=date.today(),
                expiration_date=date.today() + timedelta(days=365),
                risk_level=RiskLevel.MEDIUM,
                terms_and_conditions=self.get_valid_policy_terms()
            )
        assert "Comprehensive coverage cannot be combined with other coverage types" in str(exc_info.value)


class TestPolicyQuoteRequest:
    """Test cases for PolicyQuoteRequest schema."""

    def test_valid_quote_request(self):
        """Test creating valid quote request."""
        quote_request = PolicyQuoteRequest(
            robot_id=uuid4(),
            customer_id="customer_456",
            coverage_types=[CoverageType.PHYSICAL_DAMAGE, CoverageType.LIABILITY],
            desired_coverage_limit=Decimal('75000.00'),
            preferred_deductible=Decimal('1500.00'),
            policy_term_months=12,
            payment_frequency=PaymentFrequency.QUARTERLY
        )
        
        assert len(quote_request.coverage_types) == 2
        assert quote_request.policy_term_months == 12
        assert quote_request.payment_frequency == PaymentFrequency.QUARTERLY

    def test_invalid_policy_term(self):
        """Test validation of invalid policy term."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyQuoteRequest(
                robot_id=uuid4(),
                customer_id="customer_456",
                coverage_types=[CoverageType.CYBER_SECURITY],
                desired_coverage_limit=Decimal('25000.00'),
                policy_term_months=72,  # Invalid: > 60 months
                payment_frequency=PaymentFrequency.MONTHLY
            )
        assert "policy_term_months" in str(exc_info.value)

    def test_comprehensive_with_others_validation(self):
        """Test validation of comprehensive coverage with others."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyQuoteRequest(
                robot_id=uuid4(),
                customer_id="customer_456",
                coverage_types=[CoverageType.COMPREHENSIVE, CoverageType.PHYSICAL_DAMAGE],
                desired_coverage_limit=Decimal('100000.00'),
                policy_term_months=12
            )
        assert "Comprehensive coverage cannot be combined with other coverage types" in str(exc_info.value)


class TestPolicyRenewalRequest:
    """Test cases for PolicyRenewalRequest schema."""

    def test_valid_renewal_request(self):
        """Test creating valid renewal request."""
        renewal = PolicyRenewalRequest(
            policy_id=uuid4(),
            new_expiration_date=date.today() + timedelta(days=365),
            premium_adjustment=Decimal('100.00'),
            coverage_changes=[CoverageType.PHYSICAL_DAMAGE, CoverageType.CYBER_SECURITY]
        )
        
        assert renewal.premium_adjustment == Decimal('100.00')
        assert len(renewal.coverage_changes) == 2

    def test_invalid_renewal_date(self):
        """Test validation of invalid renewal date."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyRenewalRequest(
                policy_id=uuid4(),
                new_expiration_date=date.today() - timedelta(days=1)  # Invalid: in the past
            )
        assert "Renewal expiration date must be in the future" in str(exc_info.value)


class TestPolicyCancellationRequest:
    """Test cases for PolicyCancellationRequest schema."""

    def test_valid_cancellation_request(self):
        """Test creating valid cancellation request."""
        cancellation = PolicyCancellationRequest(
            policy_id=uuid4(),
            cancellation_date=date.today() + timedelta(days=30),
            reason="Customer no longer owns the robot",
            refund_requested=True
        )
        
        assert cancellation.refund_requested is True
        assert "no longer owns" in cancellation.reason

    def test_invalid_cancellation_date(self):
        """Test validation of invalid cancellation date."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCancellationRequest(
                policy_id=uuid4(),
                cancellation_date=date.today() - timedelta(days=1),  # Invalid: in the past
                reason="Valid reason for cancellation"
            )
        assert "Cancellation date cannot be in the past" in str(exc_info.value)

    def test_invalid_reason_too_short(self):
        """Test validation of cancellation reason too short."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCancellationRequest(
                policy_id=uuid4(),
                cancellation_date=date.today() + timedelta(days=15),
                reason="Short"  # Invalid: too short
            )
        assert "reason" in str(exc_info.value)

    def test_empty_reason_validation(self):
        """Test validation of empty cancellation reason."""
        with pytest.raises(ValidationError) as exc_info:
            PolicyCancellationRequest(
                policy_id=uuid4(),
                cancellation_date=date.today() + timedelta(days=15),
                reason="   "  # Invalid: empty after strip - too short
            )
        assert "String should have at least 10 characters" in str(exc_info.value)


class TestPolicyBusinessRules:
    """Test cases for policy business rules and edge cases."""

    def test_low_risk_minimum_premium(self):
        """Test minimum premium for low risk level."""
        robot_id = uuid4()
        effective_date = date.today()
        expiration_date = effective_date + timedelta(days=365)
        
        coverage_details = [
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,
                coverage_limit=Decimal('25000.00'),
                deductible=Decimal('500.00'),
                premium_portion=Decimal('100.00')
            )
        ]
        
        terms = PolicyTerms(
            coverage_details=coverage_details,
            cancellation_terms="30 days written notice required",
            renewal_terms="Automatic renewal unless cancelled",
            jurisdiction="US"
        )
        
        policy = PolicyBase(
            robot_id=robot_id,
            customer_id="low_risk_customer",
            coverage_types=[CoverageType.PHYSICAL_DAMAGE],
            premium_amount=Decimal('100.00'),  # Meets minimum for low risk
            deductible_amount=Decimal('500.00'),
            coverage_limit=Decimal('25000.00'),
            effective_date=effective_date,
            expiration_date=expiration_date,
            risk_level=RiskLevel.LOW,
            terms_and_conditions=terms
        )
        
        assert policy.risk_level == RiskLevel.LOW
        assert policy.premium_amount == Decimal('100.00')

    def test_critical_risk_minimum_premium(self):
        """Test minimum premium for critical risk level."""
        robot_id = uuid4()
        effective_date = date.today()
        expiration_date = effective_date + timedelta(days=365)
        
        coverage_details = [
            CoverageDetails(
                coverage_type=CoverageType.COMPREHENSIVE,
                coverage_limit=Decimal('200000.00'),
                deductible=Decimal('2000.00'),
                premium_portion=Decimal('5000.00')
            )
        ]
        
        terms = PolicyTerms(
            coverage_details=coverage_details,
            cancellation_terms="30 days written notice required",
            renewal_terms="Automatic renewal unless cancelled",
            jurisdiction="US"
        )
        
        policy = PolicyBase(
            robot_id=robot_id,
            customer_id="critical_risk_customer",
            coverage_types=[CoverageType.COMPREHENSIVE],
            premium_amount=Decimal('5000.00'),  # Meets minimum for critical risk
            deductible_amount=Decimal('2000.00'),
            coverage_limit=Decimal('200000.00'),
            effective_date=effective_date,
            expiration_date=expiration_date,
            risk_level=RiskLevel.CRITICAL,
            terms_and_conditions=terms
        )
        
        assert policy.risk_level == RiskLevel.CRITICAL
        assert policy.premium_amount == Decimal('5000.00')

    def test_multiple_coverage_types_validation(self):
        """Test validation with multiple valid coverage types."""
        robot_id = uuid4()
        effective_date = date.today()
        expiration_date = effective_date + timedelta(days=365)
        
        coverage_details = [
            CoverageDetails(
                coverage_type=CoverageType.PHYSICAL_DAMAGE,
                coverage_limit=Decimal('50000.00'),
                deductible=Decimal('1000.00'),
                premium_portion=Decimal('1200.00')
            ),
            CoverageDetails(
                coverage_type=CoverageType.LIABILITY,
                coverage_limit=Decimal('100000.00'),
                deductible=Decimal('500.00'),
                premium_portion=Decimal('800.00')
            ),
            CoverageDetails(
                coverage_type=CoverageType.CYBER_SECURITY,
                coverage_limit=Decimal('25000.00'),
                deductible=Decimal('250.00'),
                premium_portion=Decimal('400.00')
            )
        ]
        
        terms = PolicyTerms(
            coverage_details=coverage_details,
            cancellation_terms="30 days written notice required",
            renewal_terms="Automatic renewal unless cancelled",
            jurisdiction="US"
        )
        
        policy = PolicyBase(
            robot_id=robot_id,
            customer_id="multi_coverage_customer",
            coverage_types=[CoverageType.PHYSICAL_DAMAGE, CoverageType.LIABILITY, CoverageType.CYBER_SECURITY],
            premium_amount=Decimal('2400.00'),
            deductible_amount=Decimal('1000.00'),
            coverage_limit=Decimal('175000.00'),
            effective_date=effective_date,
            expiration_date=expiration_date,
            risk_level=RiskLevel.MEDIUM,
            terms_and_conditions=terms
        )
        
        assert len(policy.coverage_types) == 3
        assert CoverageType.PHYSICAL_DAMAGE in policy.coverage_types
        assert CoverageType.LIABILITY in policy.coverage_types
        assert CoverageType.CYBER_SECURITY in policy.coverage_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])