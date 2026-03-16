import pytest
from app.services.verifier.email_verifier import EmailVerifier
from app.services.verifier.profile_verifier import ProfileVerifier

@pytest.fixture
def email_verifier():
    return EmailVerifier()

@pytest.fixture
def profile_verifier():
    return ProfileVerifier()

def test_email_format_validation(email_verifier):
    assert email_verifier.verify_format("test@example.com") == True
    assert email_verifier.verify_format("invalid-email") == False
    assert email_verifier.verify_format("missing@domain") == False

def test_disposable_email_detection(email_verifier):
    assert email_verifier.check_disposable("tempmail.com") == True
    assert email_verifier.check_disposable("gmail.com") == False

def test_profile_verification_decision_maker(profile_verifier):
    profile = {"name": "Jane Doe", "role": "CEO"}
    result = profile_verifier.verify_profile(profile, "TestCo")
    
    assert result["status"] == "VERIFIED"
    assert result["confidence"] > 90

def test_profile_verification_non_decision_maker(profile_verifier):
    profile = {"name": "John Smith", "role": "Marketing Assistant"}
    result = profile_verifier.verify_profile(profile, "TestCo")
    
    assert result["status"] == "RISKY"
    assert result["confidence"] < 60

def test_email_association(profile_verifier):
    email = profile_verifier.associate_email("Jane Doe", "example.com")
    assert email == "jane.doe@example.com"
