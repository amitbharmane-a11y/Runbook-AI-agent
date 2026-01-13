import sys
import os
import argparse
import subprocess
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from agent import RunbookAgent
from ingest import ingest_runbooks
from analyzer import RunbookAnalyzer

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="AI Runbook Agent CLI")
    parser.add_argument("--ingest", action="store_true", help="Ingest runbooks into Vector DB")
    parser.add_argument("--alert", type=str, help="Simulate an alert (e.g., 'Database Latency High')")
    parser.add_argument("--analyze", action="store_true", help="Analyze all runbooks for health and best practices")
    parser.add_argument("--analyze-file", type=str, help="Analyze a specific runbook file")
    parser.add_argument("--web", action="store_true", help="Launch the web interface (Streamlit)")

    args = parser.parse_args()

    if args.ingest:
        ingest_runbooks()
        print("Ingestion complete.")
        return

    if args.analyze:
        print("Analyzing all runbooks...")
        analyzer = RunbookAnalyzer()
        runbook_dir = os.path.join(os.path.dirname(__file__), "runbooks")
        analyses = analyzer.analyze_all_runbooks(runbook_dir)

        if not analyses:
            print("No runbooks found in the runbooks directory.")
            return

        health_summary = analyzer.get_health_summary(analyses)

        print("\n" + "="*60)
        print("RUNBOOK HEALTH ANALYSIS REPORT")
        print("="*60)
        print(f"Runbooks Analyzed: {len(analyses)}")
        print(f"Overall Health Score: {health_summary['overall_health']:.1f}%")
        print(f"Average Completeness: {health_summary['average_completeness']:.1f}%")
        print(f"Average Structure: {health_summary['average_structure']:.1f}%")
        print(f"Average Safety: {health_summary['average_safety']:.1f}%")
        print(f"Average Clarity: {health_summary['average_clarity']:.1f}%")
        print("\n" + "-"*60)
        print("INDIVIDUAL RUNBOOK SCORES")
        print("-"*60)

        for analysis in analyses:
            print(f"\n{analysis.filename}")
            print(f"  Overall Score: {analysis.overall_score:.1f}%")
            print(f"  Issues Found: {len(analysis.issues)}")
            if analysis.issues:
                print("  Key Issues:")
                for issue in analysis.issues[:3]:  # Show first 3 issues
                    print(f"    - {issue}")
            if analysis.recommendations:
                print("  Recommendations:")
                for rec in analysis.recommendations[:3]:  # Show first 3 recommendations
                    print(f"    - {rec}")
        print("\n" + "="*60)
        return

    if args.analyze_file:
        if not os.path.exists(args.analyze_file):
            print(f"Error: File '{args.analyze_file}' not found.")
            return

        print(f"Analyzing runbook: {args.analyze_file}")
        analyzer = RunbookAnalyzer()
        analysis = analyzer.analyze_runbook(args.analyze_file)

        print("\n" + "="*60)
        print(f"RUNBOOK ANALYSIS: {analysis.filename}")
        print("="*60)
        print(f"Overall Score: {analysis.overall_score:.1f}%")
        print(f"Completeness: {analysis.completeness_score:.1f}%")
        print(f"Structure: {analysis.structure_score:.1f}%")
        print(f"Safety: {analysis.safety_score:.1f}%")
        print(f"Clarity: {analysis.clarity_score:.1f}%")
        print(f"\nIssues Found: {len(analysis.issues)}")
        if analysis.issues:
            for issue in analysis.issues:
                print(f"  - {issue}")

        print(f"\nRecommendations: {len(analysis.recommendations)}")
        if analysis.recommendations:
            for rec in analysis.recommendations:
                print(f"  - {rec}")

        if analysis.metadata:
            print("\nMetadata:")
            for key, value in analysis.metadata.items():
                print(f"  {key}: {value}")
        print("\n" + "="*60)
        return

    if args.web:
        print("Launching web interface...")
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error launching web interface: {e}")
            print("Make sure Streamlit is installed: pip install streamlit")
        except KeyboardInterrupt:
            print("\nWeb interface stopped.")
        return

    if args.alert:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("Error: GOOGLE_API_KEY not set in .env file.")
            print("Please follow these steps:")
            print("1. Go to https://aistudio.google.com/app/apikey")
            print("2. Create a new API key.")
            print("3. Open the .env file in this directory.")
            print("4. Paste your key: GOOGLE_API_KEY=AIzr...")
            return

        print(f"Received Alert: {args.alert}")
        print("Analyzing...")

        try:
            agent = RunbookAgent()
            response = agent.handle_alert(args.alert)
            print("\n" + "="*50)
            print("AGENT RESPONSE")
            print("="*50)
            print(response)
            print("="*50)
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()
        print("\n" + "="*50)
        print("QUICK START GUIDE")
        print("="*50)
        print("1. Set up your Google API key:")
        print("   - Create .env file with: GOOGLE_API_KEY=your_key_here")
        print()
        print("2. Ingest runbooks:")
        print("   python cli.py --ingest")
        print()
        print("3. Analyze runbooks:")
        print("   python cli.py --analyze")
        print()
        print("4. Launch web interface:")
        print("   python cli.py --web")
        print()
        print("5. Test incident response:")
        print("   python cli.py --alert 'Database Latency High'")
        print("="*50)

if __name__ == "__main__":
    main()
