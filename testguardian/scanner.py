def list_tests():
    """
    Simulates scanning test repository.
    Returns list of test names.
    """
    return [
        "test_login_valid_user",
        "test_login_invalid_password",
        "test_legacy_api_v1",
        "test_unused_feature_flag",
    ]
