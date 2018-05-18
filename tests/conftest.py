import pytest

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
                      default=False, help="Run thorough, but much slower, tests")

def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(reason="Skipping slow test without --runslow option")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)
