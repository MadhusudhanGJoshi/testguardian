from testguardian.scanner import list_tests

def test_list_tests_returns_list():
	tests = list_tests()
	assert isinstance(tests, list)
	assert len(tests)>0
