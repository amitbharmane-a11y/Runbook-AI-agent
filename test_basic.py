#!/usr/bin/env python3
"""
Basic test script to verify the AI Runbook Agent functionality
without requiring API keys.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from analyzer import RunbookAnalyzer

def test_analyzer():
    """Test the runbook analyzer functionality"""
    print("Testing Runbook Analyzer...")

    analyzer = RunbookAnalyzer()

    # Test with existing runbook
    runbook_path = os.path.join(os.path.dirname(__file__), "runbooks", "database_latency.md")

    if os.path.exists(runbook_path):
        print(f"Analyzing {runbook_path}...")
        analysis = analyzer.analyze_runbook(runbook_path)

        print("\nAnalysis Results:")
        print(f"  Filename: {analysis.filename}")
        print(f"  Overall Score: {analysis.overall_score:.1f}%")
        print(f"  Completeness: {analysis.completeness_score:.1f}%")
        print(f"  Structure: {analysis.structure_score:.1f}%")
        print(f"  Safety: {analysis.safety_score:.1f}%")
        print(f"  Clarity: {analysis.clarity_score:.1f}%")
        print(f"  Issues Found: {len(analysis.issues)}")
        print(f"  Recommendations: {len(analysis.recommendations)}")

        if analysis.issues:
            print("\nKey Issues:")
            for issue in analysis.issues[:3]:
                print(f"  - {issue}")

        if analysis.recommendations:
            print("\nRecommendations:")
            for rec in analysis.recommendations[:3]:
                print(f"  - {rec}")

        print(f"\nMetadata: {analysis.metadata}")

        # Test batch analysis
        print("\nTesting batch analysis...")
        runbook_dir = os.path.join(os.path.dirname(__file__), "runbooks")
        analyses = analyzer.analyze_all_runbooks(runbook_dir)
        health_summary = analyzer.get_health_summary(analyses)

        print(f"Batch analysis completed for {len(analyses)} runbooks")
        print(f"Overall Health: {health_summary['overall_health']:.1f}%")
        return True
    else:
        print(f"Runbook file not found: {runbook_path}")
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from agent import RunbookAgent
        print("[OK] RunbookAgent imported successfully")

        # Chatbot import may fail due to optional dependencies
        try:
            from chatbot import RunbookChatbot
            print("[OK] RunbookChatbot imported successfully")
        except ImportError as e:
            print(f"[WARNING] RunbookChatbot import failed (optional): {e}")

        from ingest import ingest_runbooks
        print("[OK] ingest_runbooks imported successfully")

        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("AI RUNBOOK AGENT - BASIC TESTS")
    print("="*50)

    tests_passed = 0
    total_tests = 2

    # Test imports
    if test_imports():
        tests_passed += 1
    print()

    # Test analyzer
    if test_analyzer():
        tests_passed += 1
    print()

    print("="*50)
    print(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("SUCCESS: All basic functionality tests passed!")
        print("\nTo use the full system:")
        print("1. Set up GOOGLE_API_KEY in .env file")
        print("2. Run: python cli.py --ingest")
        print("3. Run: python cli.py --web")
    else:
        print("FAILED: Some tests failed. Please check the errors above.")

    print("="*50)

if __name__ == "__main__":
    main()