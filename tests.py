from app import priceValidation


def add(x, y):
    """Summaa"""
    return x + y


def multiply(x, y):
    """Kerro"""
    return x * y


def test_addition():
    """Testaa summaus"""
    assert add(3, 5) == 8


def test_multiplication():
    """Testaa kertolasku"""
    assert multiply(4, 6) == 24


# Test case for when last_price is None
def test_last_price_none():
    assert priceValidation(100, None) == False


# Test case for when deviation is within the allowed range
def test_deviation_within_range():
    assert priceValidation(90, 100) == True


# Test case for when deviation exceeds the allowed range
def test_deviation_exceeds_range():
    assert priceValidation(70, 100) == False
