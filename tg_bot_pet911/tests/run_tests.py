#!/usr/bin/env python
import os
import sys
import asyncio
import pytest

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def run_tests():
    """Run all tests using pytest."""
    # Run tests with pytest
    return pytest.main(['-xvs', os.path.dirname(__file__)])


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 