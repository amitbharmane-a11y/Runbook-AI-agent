# AI Runbook Agent 🤖

An intelligent AI-powered system for managing, analyzing, and executing IT operations runbooks with integrated chatbot capabilities for customer care and incident response.

## ✨ What's Implemented

### ✅ Completed Features

#### 🔍 Runbook Analysis & Health Scoring
- **Automated Analysis**: Analyze runbooks against IT operations best practices
- **Health Scoring**: Comprehensive scoring across completeness, structure, safety, and clarity
- **Improvement Recommendations**: AI-generated suggestions for runbook enhancement
- **Standards Compliance**: Ensure runbooks follow industry standards

#### 💬 Intelligent Chatbot
- **Multi-Modal Support**: Handles runbook analysis, incident response, and customer care
- **Context Awareness**: Automatically detects query type and responds appropriately
- **Incident Response**: Uses runbooks to provide step-by-step incident resolution
- **Customer Care**: Professional support for user inquiries and assistance

#### 📊 Dashboard & Reporting
- **Health Overview**: Visual dashboard showing overall runbook health
- **Individual Analysis**: Detailed breakdown for each runbook
- **Interactive Charts**: Plotly-powered visualizations
- **Real-time Analysis**: Live scoring and recommendations

#### 🚀 Incident Response
- **Automated Resolution**: Use runbooks to respond to IT alerts
- **Safety First**: Built-in confirmation for destructive actions
- **Rollback Procedures**: Always include recovery steps
- **Variable Injection**: Automatically handle placeholders in commands

### 🏗️ System Architecture

The system consists of four main components:

1. **Analyzer** (`src/analyzer.py`): Core analysis engine for runbook health scoring
2. **Agent** (`src/agent.py`): Incident response agent using runbook knowledge
3. **Chatbot** (`src/chatbot.py`): Multi-modal conversational interface
4. **Web Interface** (`app.py`): Streamlit-based dashboard and chat interface

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-runbook-agent
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   # Get your API key from: https://aistudio.google.com/app/apikey
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

5. **Test the installation**
   ```bash
   python test_basic.py
   ```

## Usage

### Command Line Interface

```bash
# Ingest runbooks into the vector database
python cli.py --ingest

# Analyze all runbooks for health and best practices
python cli.py --analyze

# Analyze a specific runbook
python cli.py --analyze-file runbooks/database_latency.md

# Test incident response
python cli.py --alert "Database Latency High"

# Launch the web interface
python cli.py --web
```

### Web Interface

Launch the Streamlit web application:
```bash
python cli.py --web
```

Or directly:
```bash
streamlit run app.py
```

The web interface provides:
- **Chatbot**: Interactive AI assistant for all queries
- **Dashboard**: Visual health monitoring and analytics
- **Runbook Analysis**: Detailed individual runbook reviews

## Runbook Format

Runbooks should be written in Markdown format with the following structure:

```markdown
---
title: Issue Title
version: 1.0
service_owner: Team Name
severity: High
trigger_criteria: condition_description
---

# Issue Title

## Diagnosis
1. Check current status
   ```bash
   command_to_run
   ```

## Remediation
1. Step-by-step resolution
   ```bash
   resolution_command
   ```

## Rollback
1. Recovery procedures
   ```bash
   rollback_command
   ```
```

## Health Scoring Criteria

### Completeness (25%)
- Clear trigger criteria
- Step-by-step procedures
- Validation steps
- Escalation contacts

### Structure (25%)
- Proper frontmatter metadata
- Required sections (Diagnosis, Remediation, Rollback)
- Version control
- Service owner identification

### Safety (25%)
- Destructive action warnings
- Confirmation requirements
- Safety precautions
- Rollback procedures

### Clarity (25%)
- Clear, concise language
- Proper formatting
- Consistent terminology
- Prerequisites documentation

## Chatbot Modes

### Analysis Mode
Activated by keywords: analyze, health, score, review, assess, improve, recommend
- Provides detailed runbook health analysis
- Generates improvement recommendations
- Shows compliance with best practices

### Incident Response Mode
Activated by keywords: incident, alert, error, failure, latency, timeout, crash
- Uses runbook knowledge base for resolution
- Provides step-by-step incident response
- Includes safety confirmations and rollback procedures

### Customer Care Mode (Default)
Handles general inquiries, support requests, and guidance
- Professional customer service responses
- Directs users to appropriate features
- Provides system usage guidance

## API Integration

The system uses:
- **Google Gemini Pro**: For intelligent analysis and chatbot responses
- **LangChain**: Framework for LLM orchestration and memory
- **ChromaDB**: Vector database for runbook storage and retrieval
- **Sentence Transformers**: For semantic similarity and embeddings

## Development

### Project Structure
```
├── src/
│   ├── agent.py          # Incident response agent
│   ├── analyzer.py       # Runbook analysis engine
│   ├── chatbot.py        # Multi-modal chatbot
│   └── ingest.py         # Runbook ingestion pipeline
├── runbooks/             # Runbook storage directory
├── cli.py               # Command line interface
├── app.py               # Streamlit web application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Runbooks

1. Place Markdown files in the `runbooks/` directory
2. Run ingestion: `python cli.py --ingest`
3. Analyze health: `python cli.py --analyze`

### Extending the Analyzer

To add new analysis criteria, modify `src/analyzer.py`:

```python
def _analyze_custom_criteria(self, content: str) -> Tuple[float, List[str]]:
    # Your custom analysis logic
    pass
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

For support and questions:
- Check the chatbot interface
- Review the analysis dashboard
- Contact your IT operations team

---

**Built with ❤️ for IT Operations Excellence**