"""Example scripts for testing GPSkilledGuardian functionality."""
import asyncio
from bot.utils.crypto_payments import CryptoRateConverter
from bot.utils.osrs_payments import OSRSGPPaymentProcessor


async def test_crypto_rates():
    """Test cryptocurrency rate conversion."""
    print("=== Testing Cryptocurrency Rates ===\n")
    
    # Test BTC rate
    print("Fetching BTC rate...")
    btc_rate = await CryptoRateConverter.get_btc_rate()
    if btc_rate:
        print(f"Current BTC price: ${btc_rate:,.2f}")
        
        # Convert $100 to BTC
        btc_amount = await CryptoRateConverter.usd_to_btc(100)
        if btc_amount:
            print(f"$100.00 = {btc_amount:.8f} BTC")
    else:
        print("Failed to fetch BTC rate")
    
    print()
    
    # Test LTC rate
    print("Fetching LTC rate...")
    ltc_rate = await CryptoRateConverter.get_ltc_rate()
    if ltc_rate:
        print(f"Current LTC price: ${ltc_rate:,.2f}")
        
        # Convert $100 to LTC
        ltc_amount = await CryptoRateConverter.usd_to_ltc(100)
        if ltc_amount:
            print(f"$100.00 = {ltc_amount:.8f} LTC")
    else:
        print("Failed to fetch LTC rate")
    
    print()


async def test_osrs_calculations():
    """Test OSRS GP calculations."""
    print("=== Testing OSRS GP Calculations ===\n")
    
    processor = OSRSGPPaymentProcessor(gp_rate=0.50)  # $0.50 per million GP
    
    # Test USD to GP conversion
    usd_amounts = [5.00, 10.00, 25.00, 50.00, 100.00]
    
    print(f"GP Rate: ${processor.gp_rate}/M\n")
    
    for usd in usd_amounts:
        gp = processor.calculate_gp_amount(usd)
        print(f"${usd:.2f} = {gp:,.0f} GP ({gp/1_000_000:.1f}M)")
    
    print()


async def test_rsn_validation():
    """Test RSN validation."""
    print("=== Testing RSN Validation ===\n")
    
    processor = OSRSGPPaymentProcessor(gp_rate=0.50)
    
    # Test with a well-known RSN
    test_rsns = ["Zezima", "Lynx Titan", "InvalidRSN12345"]
    
    for rsn in test_rsns:
        print(f"Validating RSN: {rsn}")
        is_valid = await processor.validate_rsn(rsn)
        
        if is_valid:
            stats = await processor.get_player_stats(rsn)
            if stats:
                print(f"  ✓ Valid - Total Level: {stats.get('level', 'N/A')}, "
                      f"Total XP: {stats.get('xp', 'N/A'):,}")
            else:
                print(f"  ✓ Valid (could not fetch stats)")
        else:
            print(f"  ✗ Invalid or not found")
        print()


async def main():
    """Run all example tests."""
    print("GPSkilledGuardian - Example Functionality Tests")
    print("=" * 50)
    print()
    
    # Test cryptocurrency rates
    try:
        await test_crypto_rates()
    except Exception as e:
        print(f"Error testing crypto rates: {e}\n")
    
    # Test OSRS calculations
    try:
        await test_osrs_calculations()
    except Exception as e:
        print(f"Error testing OSRS calculations: {e}\n")
    
    # Test RSN validation
    try:
        await test_rsn_validation()
    except Exception as e:
        print(f"Error testing RSN validation: {e}\n")
    
    print("=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
