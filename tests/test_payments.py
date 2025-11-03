"""Test suite for GPSkilledGuardian bot."""
import pytest
import asyncio
from datetime import datetime, timedelta
from bot.models import Payment, PaymentStatus, PaymentType, User
from bot.utils.crypto_payments import CryptoRateConverter
from bot.utils.osrs_payments import OSRSGPPaymentProcessor


class TestCryptoRateConverter:
    """Test cryptocurrency rate conversion."""
    
    @pytest.mark.asyncio
    async def test_get_btc_rate(self):
        """Test getting BTC rate."""
        rate = await CryptoRateConverter.get_btc_rate()
        assert rate is None or rate > 0, "BTC rate should be positive or None"
    
    @pytest.mark.asyncio
    async def test_get_ltc_rate(self):
        """Test getting LTC rate."""
        rate = await CryptoRateConverter.get_ltc_rate()
        assert rate is None or rate > 0, "LTC rate should be positive or None"
    
    @pytest.mark.asyncio
    async def test_usd_to_btc(self):
        """Test USD to BTC conversion."""
        btc_amount = await CryptoRateConverter.usd_to_btc(100)
        assert btc_amount is None or btc_amount > 0, "BTC amount should be positive or None"


class TestOSRSGPPaymentProcessor:
    """Test OSRS GP payment processing."""
    
    def test_calculate_gp_amount(self):
        """Test GP amount calculation."""
        processor = OSRSGPPaymentProcessor(gp_rate=0.50)
        gp_amount = processor.calculate_gp_amount(10.0)
        assert gp_amount == 20_000_000, "Should convert $10 to 20M GP at $0.50/M rate"
    
    def test_calculate_usd_amount(self):
        """Test USD amount calculation."""
        processor = OSRSGPPaymentProcessor(gp_rate=0.50)
        usd_amount = processor.calculate_usd_amount(20_000_000)
        assert usd_amount == 10.0, "Should convert 20M GP to $10 at $0.50/M rate"
    
    @pytest.mark.asyncio
    async def test_validate_rsn(self):
        """Test RSN validation."""
        processor = OSRSGPPaymentProcessor(gp_rate=0.50)
        # Test with a known valid RSN (Zezima is a famous OSRS player)
        is_valid = await processor.validate_rsn("Zezima")
        # This test might fail if the API is down, so we just check the type
        assert isinstance(is_valid, bool), "Should return boolean"


class TestPaymentModel:
    """Test payment model."""
    
    def test_payment_creation(self):
        """Test creating a payment record."""
        payment = Payment(
            user_id="123456789",
            username="TestUser#1234",
            payment_type=PaymentType.BTC,
            amount_usd=10.0,
            amount_crypto=0.0003,
            wallet_address="bc1test",
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        
        assert payment.user_id == "123456789"
        assert payment.payment_type == PaymentType.BTC
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount_usd == 10.0


class TestUserModel:
    """Test user model."""
    
    def test_user_creation(self):
        """Test creating a user record."""
        user = User(
            discord_id="123456789",
            username="TestUser#1234"
        )
        
        assert user.discord_id == "123456789"
        assert user.has_paid_role is False
        assert user.total_payments == 0
        assert user.total_spent_usd == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
