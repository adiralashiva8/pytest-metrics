import pytest
import time

from _pytest.runner import pytest_sessionstart
from _pytest.runner import pytest_runtest_setup
from _pytest.runner import runtestprotocol
from _pytest.runner import pytest_runtest_teardown
from _pytest.runner import pytest_runtest_teardown

def pytest_addoption(parser):
    group = parser.getgroup('metrics')
    group.addoption(
        '--metrics_enable',
        action='store',
        dest='metrics_enable',
        default="True",
        help='Enable or disable metrics report'
    )
    group.addoption(
        '--metrics_logo',
        action='store',
        dest='metrics_logo',
        default="",
        help='Logo to use in metrics report'
    )

def pytest_sessionstart(session):
    print "Execution session starts here - Will execute only once at first"

def pytest_runtest_setup(item):
    print "Test setup - Test starts here"

def pytest_runtest_protocol(item, log=True, nextitem=None):
    # Provide's test case execution details
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            # get test case name and test case status
            print '\n%s --- %s' % (item.name, report.outcome)
    return True

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Error message if test case failed
        print rep.longreprtext

def pytest_runtest_teardown(item, nextitem):
    print "Test teardown - Test ends here"

def pytest_sessionfinish(session):
    print "Execution session ends here - Will execute only once at last"

@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    duration = time.time() - terminalreporter._sessionstarttime
    yield

    passed_tests = len(terminalreporter.stats.get('passed', ""))
    failed_tests = len(terminalreporter.stats.get('failed', ""))
    skipped_tests = len(terminalreporter.stats.get('skipped', ""))
    error_tests = len(terminalreporter.stats.get('error', ""))
    xfailed_tests = len(terminalreporter.stats.get('xfailed', ""))
    xpassed_tests = len(terminalreporter.stats.get('xpassed', ""))

    total_tests = passed_tests + failed_tests + skipped_tests + error_tests + xfailed_tests + xpassed_tests
    print "Total Tests - ", total_tests