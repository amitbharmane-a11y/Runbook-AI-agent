import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add src to path for proper imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from chatbot import RunbookChatbot
from analyzer import RunbookAnalyzer

# Page configuration
st.set_page_config(
    page_title="AI Runbook Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = RunbookChatbot()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []

# Sidebar
st.sidebar.title("🤖 AI Runbook Agent")
st.sidebar.markdown("---")

# Document upload in sidebar (global)
st.sidebar.subheader("📤 Document Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload runbook documents:",
    type=['pdf', 'md', 'txt'],
    help="Upload documents for chatbot to reference"
)

if uploaded_file is not None:
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success(f"✅ {uploaded_file.name} uploaded!")

    # Store uploaded document in session state
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    st.session_state.uploaded_documents.append({
        'name': uploaded_file.name,
        'path': file_path,
        'content': uploaded_file.getvalue().decode('utf-8', errors='ignore')
    })

# Show uploaded documents in sidebar
if 'uploaded_documents' in st.session_state and st.session_state.uploaded_documents:
    st.sidebar.subheader("📋 Uploaded Documents")
    for i, doc in enumerate(st.session_state.uploaded_documents):
        st.sidebar.write(f"📄 {doc['name']}")

st.sidebar.markdown("---")

# Mode selector
mode = st.sidebar.radio(
    "Select Mode:",
    ["💬 Chatbot", "📊 Dashboard", "📋 Runbook Analysis"],
    help="Choose your interaction mode"
)

st.sidebar.markdown("---")

# Document Upload Section
st.sidebar.subheader("📄 Document Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload runbook or document",
    type=['md', 'txt', 'pdf', 'docx'],
    help="Upload documents for chatbot analysis"
)

if uploaded_file is not None:
    # Save uploaded file temporarily
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.sidebar.success(f"✅ {uploaded_file.name} uploaded successfully!")

    # Store uploaded document in session state
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = []
    st.session_state.uploaded_documents.append({
        'name': uploaded_file.name,
        'path': file_path,
        'content': uploaded_file.getvalue().decode('utf-8', errors='ignore')
    })

st.sidebar.markdown("---")

# Quick actions
st.sidebar.subheader("Quick Actions")
if st.sidebar.button("🔄 Analyze All Runbooks"):
    with st.spinner("Analyzing runbooks..."):
        analyzer = RunbookAnalyzer()
        runbook_dir = os.path.join(os.path.dirname(__file__), "runbooks")
        analyses = analyzer.analyze_all_runbooks(runbook_dir)
        health_summary = analyzer.get_health_summary(analyses)
        st.session_state.analysis_data = {
            "analyses": analyses,
            "health_summary": health_summary,
            "timestamp": datetime.now()
        }
    st.sidebar.success("Analysis complete!")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.session_state.chatbot.reset_conversation()
    st.sidebar.success("Chat history cleared!")

if st.sidebar.button("🗂️ Clear Uploaded Documents"):
    if 'uploaded_documents' in st.session_state:
        st.session_state.uploaded_documents = []
    # Clean up uploaded files
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if os.path.exists(upload_dir):
        import shutil
        shutil.rmtree(upload_dir)
    st.sidebar.success("Uploaded documents cleared!")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**About:**
This AI agent helps you:
- Analyze runbooks against best practices
- Respond to IT incidents
- Provide customer care support
- Generate improvement recommendations
""")

# Main content
if mode == "💬 Chatbot":
    st.title("💬 AI Runbook Chatbot")
    st.markdown("Chat with our AI agent for runbook analysis, incident response, and customer support.")

    # Document upload section
    st.subheader("📎 Upload Documents for Context")
    st.markdown("Upload runbooks, documentation, or other files to provide additional context for the chatbot.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=['txt', 'md', 'pdf', 'doc', 'docx'],
        accept_multiple_files=True,
        help="Upload documents that the chatbot can reference when answering your questions"
    )

    if uploaded_files:
        # Process uploaded files
        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        for uploaded_file in uploaded_files:
            file_path = os.path.join(upload_dir, uploaded_file.name)

            # Save the uploaded file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract text content based on file type
            content = ""
            if uploaded_file.name.endswith('.txt'):
                content = uploaded_file.getvalue().decode('utf-8')
            elif uploaded_file.name.endswith('.md'):
                content = uploaded_file.getvalue().decode('utf-8')
            elif uploaded_file.name.endswith('.pdf'):
                # For PDF, we'll use a simple text extraction
                try:
                    from pypdf import PdfReader
                    pdf_reader = PdfReader(file_path)
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text() + "\n"
                except Exception as e:
                    content = f"Error reading PDF: {str(e)}"
            else:
                # For other file types, try to read as text
                try:
                    content = uploaded_file.getvalue().decode('utf-8')
                except:
                    content = f"Unable to extract text from {uploaded_file.name}"

            # Add to session state
            doc_info = {
                'name': uploaded_file.name,
                'path': file_path,
                'content': content,
                'size': len(content)
            }

            # Check if document already exists
            existing_names = [doc['name'] for doc in st.session_state.uploaded_documents]
            if uploaded_file.name not in existing_names:
                st.session_state.uploaded_documents.append(doc_info)

        st.success(f"Successfully uploaded {len(uploaded_files)} document(s)!")

    # Display uploaded documents
    if st.session_state.uploaded_documents:
        st.subheader("📋 Uploaded Documents")
        for i, doc in enumerate(st.session_state.uploaded_documents):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {doc['name']}")
            with col2:
                st.write(f"{len(doc['content'])} chars")
            with col3:
                if st.button(f"Remove {i}", key=f"remove_{i}"):
                    # Remove file from disk
                    if os.path.exists(doc['path']):
                        os.remove(doc['path'])
                    # Remove from session state
                    st.session_state.uploaded_documents.pop(i)
                    st.rerun()

    st.markdown("---")

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "mode" in message:
                    st.caption(f"Mode: {message['mode']}")

    # Chat input
    if prompt := st.chat_input("Ask me about runbooks, incidents, or need help..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get uploaded documents for context
        uploaded_documents = st.session_state.get('uploaded_documents', [])

        # Get bot response with uploaded documents context
        with st.spinner("Thinking..."):
            try:
                response_data = st.session_state.chatbot.process_message(prompt, uploaded_documents)

                # Add bot response to chat history
                bot_message = {
                    "role": "assistant",
                    "content": response_data["response"],
                    "mode": response_data.get("mode", "general")
                }
                st.session_state.messages.append(bot_message)

                # Store analysis data if available
                if "analysis_data" in response_data:
                    st.session_state.analysis_data = response_data["analysis_data"]

            except Exception as e:
                # Handle errors gracefully
                error_message = {
                    "role": "assistant",
                    "content": f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question or contact support if the issue persists.",
                    "mode": "error"
                }
                st.session_state.messages.append(error_message)

        # Rerun to display the new messages
        st.rerun()

        # Rerun to display the new messages
        st.rerun()

elif mode == "📊 Dashboard":
    st.title("📊 Runbook Health Dashboard")

    if st.session_state.analysis_data is None:
        st.info("No analysis data available. Click 'Analyze All Runbooks' in the sidebar to generate a health report.")
    else:
        analysis_data = st.session_state.analysis_data
        health_summary = analysis_data["health_summary"]
        analyses = analysis_data["analyses"]

        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Overall Health", f"{health_summary['overall_health']:.1f}%")
        with col2:
            st.metric("Completeness", f"{health_summary['average_completeness']:.1f}%")
        with col3:
            st.metric("Structure", f"{health_summary['average_structure']:.1f}%")
        with col4:
            st.metric("Safety", f"{health_summary['average_safety']:.1f}%")
        with col5:
            st.metric("Clarity", f"{health_summary['average_clarity']:.1f}%")

        st.markdown("---")

        # Health breakdown chart
        st.subheader("Health Score Breakdown")
        health_df = pd.DataFrame({
            "Category": ["Completeness", "Structure", "Safety", "Clarity"],
            "Score": [
                health_summary["average_completeness"],
                health_summary["average_structure"],
                health_summary["average_safety"],
                health_summary["average_clarity"]
            ]
        })

        fig = px.bar(health_df, x="Category", y="Score",
                    title="Average Health Scores by Category",
                    color="Score",
                    color_continuous_scale="RdYlGn")
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        # Individual runbook scores
        st.subheader("Individual Runbook Scores")
        runbook_df = pd.DataFrame({
            "Runbook": [a.filename for a in analyses],
            "Overall Score": [a.overall_score for a in analyses],
            "Issues": [len(a.issues) for a in analyses],
            "Recommendations": [len(a.recommendations) for a in analyses]
        })

        # Color coding for scores
        def color_score(val):
            if val >= 80:
                return 'background-color: #d4edda; color: #155724'
            elif val >= 60:
                return 'background-color: #fff3cd; color: #856404'
            else:
                return 'background-color: #f8d7da; color: #721c24'

        styled_df = runbook_df.style.applymap(color_score, subset=["Overall Score"])
        st.dataframe(styled_df, use_container_width=True)

        # Issues distribution
        st.subheader("Issues Distribution")
        issues_fig = px.pie(runbook_df, names="Runbook", values="Issues",
                           title="Issues per Runbook")
        st.plotly_chart(issues_fig, use_container_width=True)

elif mode == "📋 Runbook Analysis":
    st.title("📋 Detailed Runbook Analysis")

    # Document upload section
    st.subheader("📤 Upload Custom Documents")
    uploaded_file = st.file_uploader(
        "Upload runbook documents (PDF, MD, TXT) for analysis:",
        type=['pdf', 'md', 'txt'],
        help="Upload your own runbook documents to analyze them"
    )

    if uploaded_file is not None:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ {uploaded_file.name} uploaded successfully!")

        # Store uploaded document in session state
        if 'uploaded_documents' not in st.session_state:
            st.session_state.uploaded_documents = []
        st.session_state.uploaded_documents.append({
            'name': uploaded_file.name,
            'path': file_path,
            'content': uploaded_file.getvalue().decode('utf-8', errors='ignore')
        })

    # Show uploaded documents
    if 'uploaded_documents' in st.session_state and st.session_state.uploaded_documents:
        st.subheader("📋 Uploaded Documents")
        for i, doc in enumerate(st.session_state.uploaded_documents):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {doc['name']}")
            with col2:
                if st.button(f"Remove {i+1}", key=f"remove_{i}"):
                    # Remove from session state
                    st.session_state.uploaded_documents.pop(i)
                    # Remove file
                    if os.path.exists(doc['path']):
                        os.remove(doc['path'])
                    st.rerun()

    # Get list of runbooks
    runbook_dir = os.path.join(os.path.dirname(__file__), "runbooks")
    if os.path.exists(runbook_dir):
        runbooks = [f for f in os.listdir(runbook_dir) if f.endswith('.md')]

        if runbooks:
            st.subheader("📖 Built-in Runbooks")
            selected_runbook = st.selectbox("Select a runbook to analyze:", runbooks)

            if selected_runbook:
                # Analyze selected runbook
                analyzer = RunbookAnalyzer()
                runbook_path = os.path.join(runbook_dir, selected_runbook)
                analysis = analyzer.analyze_runbook(runbook_path)

                # Display analysis results
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.subheader("Health Scores")
                    st.metric("Overall Score", f"{analysis.overall_score:.1f}%")
                    st.metric("Completeness", f"{analysis.completeness_score:.1f}%")
                    st.metric("Structure", f"{analysis.structure_score:.1f}%")
                    st.metric("Safety", f"{analysis.safety_score:.1f}%")
                    st.metric("Clarity", f"{analysis.clarity_score:.1f}%")

                    # Score radar chart
                    scores = {
                        "Completeness": analysis.completeness_score,
                        "Structure": analysis.structure_score,
                        "Safety": analysis.safety_score,
                        "Clarity": analysis.clarity_score
                    }

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=list(scores.values()),
                        theta=list(scores.keys()),
                        fill='toself',
                        name='Scores'
                    ))
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        title="Score Breakdown"
                    )
                    st.plotly_chart(fig)

                with col2:
                    # Issues and recommendations
                    st.subheader("Issues Found")
                    if analysis.issues:
                        for issue in analysis.issues:
                            st.error(f"• {issue}")
                    else:
                        st.success("No issues found!")

                    st.subheader("Recommendations")
                    if analysis.recommendations:
                        for rec in analysis.recommendations:
                            st.info(f"• {rec}")
                    else:
                        st.success("No recommendations needed!")

                # Metadata
                if analysis.metadata:
                    st.subheader("Runbook Metadata")
                    meta_df = pd.DataFrame(list(analysis.metadata.items()),
                                         columns=["Property", "Value"])
                    st.table(meta_df)

                # Display runbook content
                st.subheader("Runbook Content")
                try:
                    with open(runbook_path, 'r') as f:
                        content = f.read()
                    st.code(content, language="markdown")
                except Exception as e:
                    st.error(f"Error reading runbook: {e}")

        else:
            st.info("No runbooks found in the runbooks directory.")
    else:
        st.error("Runbooks directory not found.")

# Footer
st.markdown("---")
st.markdown("*AI Runbook Agent - Powered by Google Gemini & LangChain*")