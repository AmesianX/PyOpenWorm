from __future__ import print_function
from _pytest.runner import runtestprotocol
# This (Python) file is executed before the py.test suite runs.

# This line specifies where to look for plugins, using python dot notation w.r.t. current directory.
pytest_plugins = 'tests.pytest_profile'


def pytest_runtest_logstart(nodeid, location):
    print(str(nodeid) + '...', end='')

def pytest_runtest_logfinish(nodeid, location):
    print()


