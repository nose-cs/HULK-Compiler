import glob
import unittest

red = "\033[31m"
green = "\033[32m"
refresh = "\033[0m"


def run_tests():
    test_suite = unittest.TestSuite()
    test_file_strings = glob.glob('test_*.py', recursive=True)

    # remove .py extension
    module_strings = [file[0:len(file) - 3] for file in test_file_strings]

    # Import all test modules
    [__import__(module) for module in module_strings]

    # Load test suites from each module
    suites = [unittest.TestLoader().loadTestsFromName(module) for module in module_strings]
    [test_suite.addTest(suite) for suite in suites]

    # Run the tests
    result = unittest.TestResult()
    test_suite.run(result)
    return result


def print_colored(color, message):
    print(color + message + refresh)


def print_title(color, message):
    print()
    print_colored(color, f"{'=' * 70}{message}{'=' * 70}")
    print()


def print_results(results):
    color = green if results.wasSuccessful() else red

    print_title(color, "Results")
    print(f"Tests run: {results.testsRun}")
    print(f"Test passed: {results.testsRun - len(results.errors) - len(results.failures)}")
    print(f"Was successful: {results.wasSuccessful()}")

    if results.errors:
        print_title(red, "Errors")
        for error in results.errors:
            print(f"Error in {error[0]}: {error[1]}")
    if results.failures:
        print_title(red, "Failures")
        for failure in results.failures:
            print(f"Failure in {failure[0]}: {failure[1]}")
