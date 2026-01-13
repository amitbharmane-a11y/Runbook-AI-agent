#!/usr/bin/env python3
"""
Setup script for Ollama - Local LLM for AI Runbook Agent
This script will help you set up Ollama and download the required model.
"""

import subprocess
import sys
import os
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] Ollama command failed")
            return False
    except FileNotFoundError:
        print("[ERROR] Ollama is not installed")
        return False

def install_ollama():
    """Provide instructions for installing Ollama"""
    print("\nOllama Installation Instructions:")
    print("=" * 50)
    print("1. Download Ollama from: https://ollama.ai/download")
    print("2. Install the Windows version")
    print("3. Restart your terminal/command prompt")
    print("4. Run this script again")
    print()
    print("Or install via command line:")
    print("curl -fsSL https://ollama.ai/install.sh | sh")
    print("=" * 50)

def pull_model(model_name="llama3.2:3b"):
    """Pull the required model"""
    print(f"\nDownloading model: {model_name}")
    print("This may take several minutes depending on your internet connection...")

    try:
        process = subprocess.Popen(['ollama', 'pull', model_name],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Show progress
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"  {output.strip()}")

        if process.returncode == 0:
            print(f"[OK] Successfully downloaded {model_name}")
            return True
        else:
            print(f"[ERROR] Failed to download {model_name}")
            return False

    except Exception as e:
        print(f"[ERROR] Error downloading model: {e}")
        return False

def test_model(model_name="llama3.2:3b"):
    """Test if the model works"""
    print(f"\nTesting model: {model_name}")

    try:
        result = subprocess.run(['ollama', 'run', model_name, 'Hello, test message'],
                              input='Hello',
                              capture_output=True,
                              text=True,
                              timeout=30)

        if result.returncode == 0:
            print("[OK] Model test successful!")
            return True
        else:
            print(f"[ERROR] Model test failed: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("[WARNING] Model test timed out (but model may still work)")
        return True
    except Exception as e:
        print(f"[ERROR] Model test error: {e}")
        return False

def test_chatbot():
    """Test the chatbot with Ollama"""
    print("\nTesting AI Runbook Agent with Ollama...")

    try:
        # Import and test
        sys.path.append('src')
        from chatbot import RunbookChatbot

        chatbot = RunbookChatbot()

        if chatbot.llm_provider == "ollama":
            print("[OK] Chatbot initialized with Ollama")

            # Test a simple message
            response = chatbot.process_message("Hello! Can you help me?")

            if response and 'response' in response:
                print("[OK] Chatbot response test successful!")
                print(f"Response preview: {response['response'][:100]}...")
                return True
            else:
                print("[ERROR] Chatbot response test failed")
                return False
        else:
            print(f"[ERROR] Chatbot using {chatbot.llm_provider} instead of Ollama")
            return False

    except Exception as e:
        print(f"[ERROR] Chatbot test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("AI Runbook Agent - Ollama Setup")
    print("=" * 50)

    # Check if Ollama is installed
    if not check_ollama_installed():
        install_ollama()
        return

    # Pull the model
    if not pull_model("llama3.2:3b"):
        print("\nModel download failed. Please try again.")
        return

    # Test the model
    if not test_model("llama3.2:3b"):
        print("\nModel test had issues, but setup may still work.")

    # Test the chatbot
    if test_chatbot():
        print("\nSetup Complete! Your AI Runbook Agent is ready to use with Ollama!")
        print("\nTo run the system:")
        print("  python cli.py --web    # Start web interface")
        print("  python cli.py --analyze # Analyze runbooks")
        print("  python demo_chatbot.py # Test chatbot")
    else:
        print("\nSetup completed but chatbot test failed.")
        print("The system may still work - try running it manually.")

if __name__ == "__main__":
    main()