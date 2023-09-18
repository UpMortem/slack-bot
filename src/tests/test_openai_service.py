import pytest

from services.openai_service import function1, function2, function3


def test_function1():
    # Call the function with some input
    result = function1("input1", "input2")
    # Assert that the output is as expected
    pytest.assume(result == "expected_output1")


def test_function2():
    # Call the function with some input
    result = function2("input1", "input2")
    # Assert that the output is as expected
    pytest.assume(result == "expected_output2")


def test_function3():
    # Call the function with some input
    result = function3("input1", "input2")
    # Assert that the output is as expected
    pytest.assume(result == "expected_output3")
