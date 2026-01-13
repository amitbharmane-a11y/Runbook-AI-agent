#!/usr/bin/env python3
"""
Demo script to test the AI Runbook Chatbot functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from chatbot import RunbookChatbot

def demo_chatbot():
    """Demonstrate chatbot functionality"""
    print("AI Runbook Chatbot Demo")
    print("=" * 50)

    # Initialize chatbot
    chatbot = RunbookChatbot()

    # Test messages
    test_messages = [
        "Hello! Can you help me?",
        "What can you do?",
        "Analyze my runbooks",
        "I have a database latency issue",
        "How do I upload documents?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\nUser {i}: {message}")

        try:
            response = chatbot.process_message(message)
            print(f"Bot: {response['response'][:150]}...")
            print(f"Mode: {response['mode']}")
        except Exception as e:
            print(f"Error: {str(e)}")

        print("-" * 50)

    # Test with uploaded document simulation
    print("\nTesting with simulated uploaded document...")
    sample_doc = {
        'name': 'server_maintenance.md',
        'path': '/fake/path/server_maintenance.md',
        'content': '''
        # Server Maintenance Runbook

        ## Overview
        This runbook covers standard server maintenance procedures.

        ## Pre-Maintenance Checklist
        1. Notify stakeholders 48 hours in advance
        2. Schedule maintenance window during low-traffic hours
        3. Prepare rollback plan

        ## Emergency Contacts
        - Primary: infrastructure-team@company.com
        - Secondary: devops-lead@company.com
        '''
    }

    uploaded_docs = [sample_doc]

    test_message = "Who should I contact for server maintenance?"
    print(f"\nUser (with document): {test_message}")

    try:
        response = chatbot.process_message(test_message, uploaded_docs)
        print(f"Bot: {response['response'][:200]}...")
        print(f"Mode: {response['mode']}")
    except Exception as e:
        print(f"Error: {str(e)}")

    print("\nChatbot demo completed!")

if __name__ == "__main__":
    demo_chatbot()