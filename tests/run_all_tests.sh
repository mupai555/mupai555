#!/bin/bash

# Run all tests for Omron extrapolation and LBM functionality

echo "================================================"
echo "MUPAI Test Suite - Omron & LBM Functionality"
echo "================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

FAILED=0

echo "1. Running Omron extrapolation tests..."
python tests/test_omron_extrapolation.py
if [ $? -ne 0 ]; then
    FAILED=$((FAILED + 1))
    echo "❌ Omron extrapolation tests FAILED"
else
    echo "✅ Omron extrapolation tests PASSED"
fi
echo ""

echo "2. Running session state integration tests..."
python tests/test_session_state_integration.py
if [ $? -ne 0 ]; then
    FAILED=$((FAILED + 1))
    echo "❌ Session state tests FAILED"
else
    echo "✅ Session state tests PASSED"
fi
echo ""

echo "3. Running full workflow tests..."
python tests/test_full_workflow.py
if [ $? -ne 0 ]; then
    FAILED=$((FAILED + 1))
    echo "❌ Full workflow tests FAILED"
else
    echo "✅ Full workflow tests PASSED"
fi
echo ""

echo "================================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED (19 tests across 3 suites)"
    echo "================================================"
    exit 0
else
    echo "❌ $FAILED test suite(s) FAILED"
    echo "================================================"
    exit 1
fi
