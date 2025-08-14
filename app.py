"""
MoSPI AI-Powered Smart Survey Tool - Working Prototype
Single file working application with OpenAI integration

To run:
1. pip install streamlit pandas numpy plotly openai
2. Set your OpenAI API key in the script or as environment variable
3. streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
import random
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

# Optional imports - will work without them
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not installed. Install with: pip install plotly")

try:
    import openai
    OPENAI_AVAILABLE = True
    # Set your OpenAI API key here or use environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
except ImportError:
    OPENAI_AVAILABLE = False
    st.info("OpenAI not installed. Install with: pip install openai")

# Page configuration
st.set_page_config(
    page_title="MoSPI Smart Survey Tool",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.surveys = {}
    st.session_state.responses = []
    st.session_state.current_survey = None
    st.session_state.survey_progress = {}
    st.session_state.user_authenticated = False
    st.session_state.verified_user = None
    st.session_state.language = "English"
    st.session_state.manual_questions = []
    
    # Add sample survey data
    sample_survey_id = "DEMO_001"
    st.session_state.surveys[sample_survey_id] = {
        "id": sample_survey_id,
        "name": "Household Demographic Survey",
        "description": "Sample survey for demographic data collection",
        "questions": [
            {
                "id": "q1",
                "text": "What is your age?",
                "type": "number",
                "validation": {"min": 0, "max": 120},
                "required": True,
                "category": "demographic"
            },
            {
                "id": "q2",
                "text": "What is your gender?",
                "type": "select",
                "options": ["Male", "Female", "Other", "Prefer not to say"],
                "required": True,
                "category": "demographic"
            },
            {
                "id": "q3",
                "text": "What is your employment status?",
                "type": "select",
                "options": ["Employed", "Self-Employed", "Unemployed", "Student", "Retired"],
                "required": True,
                "category": "economic"
            },
            {
                "id": "q4",
                "text": "What is your monthly household income (in ₹)?",
                "type": "select",
                "options": ["<10,000", "10,000-25,000", "25,000-50,000", "50,000-1,00,000", ">1,00,000"],
                "required": True,
                "category": "economic"
            },
            {
                "id": "q5",
                "text": "What is your primary occupation?",
                "type": "text",
                "required": True,
                "category": "economic",
                "ai_classify": True
            }
        ],
        "created_at": datetime.now().isoformat(),
        "ai_generated": False,
        "adaptive": True
    }

# Sample Question Bank
QUESTION_BANK = {
    "demographic": [
        {"id": "d1", "text": "What is your age?", "type": "number", "validation": {"min": 0, "max": 120}, "required": True},
        {"id": "d2", "text": "What is your gender?", "type": "select", "options": ["Male", "Female", "Other"], "required": True},
        {"id": "d3", "text": "What is your education level?", "type": "select", "options": ["Primary", "Secondary", "Graduate", "Post-Graduate"], "required": True},
        {"id": "d4", "text": "What is your marital status?", "type": "select", "options": ["Single", "Married", "Divorced", "Widowed"], "required": False}
    ],
    "economic": [
        {"id": "e1", "text": "Employment status?", "type": "select", "options": ["Employed", "Unemployed", "Self-Employed"], "required": True},
        {"id": "e2", "text": "Monthly income?", "type": "select", "options": ["<10k", "10-25k", "25-50k", "50-100k", ">100k"], "required": True},
        {"id": "e3", "text": "Primary occupation?", "type": "text", "required": True, "ai_classify": True}
    ],
    "health": [
        {"id": "h1", "text": "Do you have health insurance?", "type": "select", "options": ["Yes", "No"], "required": True},
        {"id": "h2", "text": "How would you rate your health?", "type": "select", "options": ["Excellent", "Good", "Fair", "Poor"], "required": False}
    ]
}

# NCO Codes for occupation classification
NCO_CODES = {
    "doctor": "2211", "engineer": "2141", "teacher": "2330",
    "farmer": "6111", "driver": "8321", "manager": "1120",
    "clerk": "4110", "salesperson": "5221", "nurse": "2221",
    "software": "2512", "developer": "2512", "programmer": "2512"
}

# Helper Functions
def generate_id(prefix=""):
    """Generate unique ID"""
    return f"{prefix}{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"

def classify_occupation(text):
    """Classify occupation with NCO codes"""
    text_lower = text.lower()
    for occupation, code in NCO_CODES.items():
        if occupation in text_lower:
            return {"category": occupation.title(), "code": code, "confidence": 0.85}
    return {"category": "Other", "code": "9999", "confidence": 0.5}

def ai_generate_survey(prompt, use_openai=False):
    """Generate survey using AI or mock"""
    if use_openai and OPENAI_AVAILABLE and openai.api_key != "your-api-key-here":
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a survey designer. Generate survey questions in JSON format."},
                    {"role": "user", "content": f"Create 5 survey questions for: {prompt}. Return as JSON array with fields: id, text, type (text/number/select), options (if select), required (boolean)."}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            questions = json.loads(response.choices[0].message.content)
            return questions
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
            return mock_generate_survey(prompt)
    else:
        return mock_generate_survey(prompt)

def mock_generate_survey(prompt):
    """Mock survey generation based on keywords"""
    questions = []
    prompt_lower = prompt.lower()
    
    if "demographic" in prompt_lower or "population" in prompt_lower:
        questions.extend(QUESTION_BANK["demographic"][:2])
    if "economic" in prompt_lower or "income" in prompt_lower:
        questions.extend(QUESTION_BANK["economic"][:2])
    if "health" in prompt_lower:
        questions.extend(QUESTION_BANK["health"][:2])
    
    if not questions:
        questions = [
            QUESTION_BANK["demographic"][0],
            QUESTION_BANK["economic"][0],
            QUESTION_BANK["health"][0]
        ]
    
    return questions

def generate_adaptive_questions(responses):
    """Generate adaptive follow-up questions"""
    adaptive = []
    
    if responses.get("q4") == ">1,00,000" or responses.get("e2") == ">100k":
        adaptive.append({
            "id": "adaptive_1",
            "text": "What percentage of income do you save?",
            "type": "select",
            "options": ["<10%", "10-20%", "20-30%", ">30%"],
            "required": False
        })
    
    if responses.get("q3") == "Unemployed" or responses.get("e1") == "Unemployed":
        adaptive.append({
            "id": "adaptive_2",
            "text": "How long have you been unemployed?",
            "type": "select",
            "options": ["<3 months", "3-6 months", "6-12 months", ">1 year"],
            "required": False
        })
    
    return adaptive

def calculate_quality_score(responses, duration):
    """Calculate response quality score"""
    total_fields = len(responses)
    filled = sum(1 for v in responses.values() if v not in [None, "", "SKIPPED"])
    completeness = filled / total_fields if total_fields > 0 else 0
    
    # Time score
    if duration < 10:
        time_score = 0.5
    elif duration > 300:
        time_score = 0.7
    else:
        time_score = 1.0
    
    return (completeness * 0.7 + time_score * 0.3)

# Main Application
def main():
    # Header
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🇮🇳 MoSPI Smart Survey Tool</h1>
        <p>AI-Powered Survey Platform for National Data Collection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🏠 Home", "📝 Survey Builder", "📱 Take Survey", "📊 Analytics", "✅ Validation Demo"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Total Surveys", len(st.session_state.surveys))
    st.sidebar.metric("Total Responses", len(st.session_state.responses))
    
    # Page routing
    if page == "🏠 Home":
        show_home()
    elif page == "📝 Survey Builder":
        show_survey_builder()
    elif page == "📱 Take Survey":
        show_take_survey()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "✅ Validation Demo":
        show_validation_demo()

def show_home():
    st.title("Welcome to MoSPI Smart Survey Tool")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### 🤖 AI-Powered
        Generate surveys using natural language with GPT integration
        """)
    
    with col2:
        st.success("""
        ### 📱 Multi-Channel
        Deploy across Web, Mobile, and messaging platforms
        """)
    
    with col3:
        st.warning("""
        ### 🌐 Offline-First
        Works without internet with automatic sync
        """)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create Survey", use_container_width=True):
            st.info("Navigate to Survey Builder from the sidebar")
    
    with col2:
        if st.button("📱 Take Survey", use_container_width=True):
            st.info("Navigate to Take Survey from the sidebar")
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Navigate to Analytics from the sidebar")
    
    # Sample data display
    st.markdown("---")
    st.subheader("Recent Activity")
    
    activity_data = pd.DataFrame({
        'Time': [datetime.now() - timedelta(minutes=i*15) for i in range(5)],
        'Action': ['Survey Created', 'Response Submitted', 'Survey Updated', 'Validated', 'Exported'],
        'User': ['Admin', 'User1', 'Admin', 'System', 'Analyst'],
        'Status': ['✅ Success', '✅ Success', '✅ Success', '⚠️ Warning', '✅ Success']
    })
    
    st.dataframe(activity_data, use_container_width=True, hide_index=True)

def show_survey_builder():
    st.title("📝 Survey Builder")
    
    tab1, tab2, tab3 = st.tabs(["🤖 AI Generator", "🔨 Manual Builder", "📋 My Surveys"])
    
    with tab1:
        st.subheader("Generate Survey with AI")
        
        use_openai = st.checkbox("Use OpenAI GPT (requires API key)", value=False)
        
        if use_openai and not OPENAI_AVAILABLE:
            st.error("Please install openai: pip install openai")
        
        if use_openai and openai.api_key == "your-api-key-here":
            api_key = st.text_input("Enter OpenAI API Key", type="password")
            if api_key:
                openai.api_key = api_key
        
        prompt = st.text_area(
            "Describe your survey",
            placeholder="Example: Create a household survey with demographic and economic questions",
            height=100
        )
        
        if st.button("🚀 Generate Survey", type="primary"):
            if prompt:
                with st.spinner("Generating survey..."):
                    questions = ai_generate_survey(prompt, use_openai)
                    
                    if questions:
                        st.success(f"Generated {len(questions)} questions!")
                        
                        for i, q in enumerate(questions, 1):
                            st.write(f"**{i}. {q['text']}**")
                            st.caption(f"Type: {q['type']} | Required: {q.get('required', False)}")
                        
                        # Save survey
                        col1, col2 = st.columns(2)
                        with col1:
                            name = st.text_input("Survey Name", value=f"AI Survey {datetime.now().strftime('%Y%m%d')}")
                        with col2:
                            desc = st.text_input("Description", value="AI-generated survey")
                        
                        if st.button("💾 Save Survey"):
                            survey_id = generate_id("SURVEY_")
                            st.session_state.surveys[survey_id] = {
                                "id": survey_id,
                                "name": name,
                                "description": desc,
                                "questions": questions,
                                "created_at": datetime.now().isoformat(),
                                "ai_generated": True,
                                "adaptive": True
                            }
                            st.success(f"Survey saved! ID: {survey_id}")
                            st.balloons()
            else:
                st.warning("Please enter a survey description")
    
    with tab2:
        st.subheader("Manual Survey Builder")
        
        with st.form("add_question"):
            col1, col2 = st.columns(2)
            
            with col1:
                q_text = st.text_input("Question Text")
                q_type = st.selectbox("Type", ["text", "number", "select", "multiselect"])
            
            with col2:
                q_required = st.checkbox("Required")
                if q_type in ["select", "multiselect"]:
                    q_options = st.text_area("Options (one per line)")
                else:
                    q_options = None
            
            if st.form_submit_button("➕ Add Question"):
                if q_text:
                    question = {
                        "id": generate_id("q_"),
                        "text": q_text,
                        "type": q_type,
                        "required": q_required
                    }
                    if q_options:
                        question["options"] = q_options.strip().split("\n")
                    
                    st.session_state.manual_questions.append(question)
                    st.success("Question added!")
        
        # Display current questions
        if st.session_state.manual_questions:
            st.write("### Current Questions")
            for i, q in enumerate(st.session_state.manual_questions):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {q['text']} ({q['type']})")
                with col2:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.manual_questions.pop(i)
                        st.rerun()
            
            # Save survey
            col1, col2 = st.columns(2)
            with col1:
                survey_name = st.text_input("Survey Name")
            with col2:
                survey_desc = st.text_input("Description")
            
            if st.button("💾 Save Survey", type="primary"):
                if survey_name and st.session_state.manual_questions:
                    survey_id = generate_id("SURVEY_")
                    st.session_state.surveys[survey_id] = {
                        "id": survey_id,
                        "name": survey_name,
                        "description": survey_desc,
                        "questions": st.session_state.manual_questions,
                        "created_at": datetime.now().isoformat(),
                        "ai_generated": False,
                        "adaptive": False
                    }
                    st.success(f"Survey saved! ID: {survey_id}")
                    st.session_state.manual_questions = []
                    st.balloons()
    
    with tab3:
        st.subheader("My Surveys")
        
        if st.session_state.surveys:
            for sid, survey in st.session_state.surveys.items():
                with st.expander(f"📋 {survey['name']} (ID: {sid})"):
                    st.write(f"**Description:** {survey['description']}")
                    st.write(f"**Questions:** {len(survey['questions'])}")
                    st.write(f"**Created:** {survey['created_at']}")
                    
                    if st.button(f"Delete", key=f"del_survey_{sid}"):
                        del st.session_state.surveys[sid]
                        st.rerun()
        else:
            st.info("No surveys created yet")

def show_take_survey():
    st.title("📱 Take Survey")
    
    # Simple authentication
    if not st.session_state.verified_user:
        st.subheader("User Verification")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            user_id = st.text_input("Enter User ID (any text for demo)")
        with col2:
            st.info("Enter any text to continue")
        
        if st.button("Verify & Continue", type="primary"):
            if user_id:
                st.session_state.verified_user = {
                    "id": generate_id("USER_"),
                    "name": f"User {user_id}",
                    "verified": True
                }
                st.success("Verified!")
                st.rerun()
    else:
        user = st.session_state.verified_user
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"Logged in as: {user['name']}")
        with col2:
            if st.button("Logout"):
                st.session_state.verified_user = None
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.surveys:
            survey_names = [s['name'] for s in st.session_state.surveys.values()]
            survey_ids = list(st.session_state.surveys.keys())
            
            selected_idx = st.selectbox(
                "Select a survey",
                range(len(survey_names)),
                format_func=lambda x: survey_names[x]
            )
            
            selected_survey_id = survey_ids[selected_idx]
            selected_survey = st.session_state.surveys[selected_survey_id]
            
            st.info(f"Questions: {len(selected_survey['questions'])}")
            
            if 'current_session' not in st.session_state:
                if st.button("Start Survey", type="primary"):
                    st.session_state.current_session = {
                        'survey_id': selected_survey_id,
                        'survey': selected_survey,
                        'current_q': 0,
                        'responses': {},
                        'start_time': datetime.now(),
                        'adaptive_questions': []
                    }
                    st.rerun()
            else:
                session = st.session_state.current_session
                all_questions = session['survey']['questions'] + session['adaptive_questions']
                current_idx = session['current_q']
                
                if current_idx < len(all_questions):
                    # Progress
                    progress = (current_idx + 1) / len(all_questions)
                    st.progress(progress)
                    st.write(f"Question {current_idx + 1} of {len(all_questions)}")
                    
                    question = all_questions[current_idx]
                    st.subheader(question['text'])
                    
                    # Input
                    response = None
                    if question['type'] == 'text':
                        response = st.text_input("Your answer", key=f"q_{question['id']}")
                        if question.get('ai_classify') and response:
                            classification = classify_occupation(response)
                            st.info(f"Classification: {classification['category']} (Code: {classification['code']})")
                    
                    elif question['type'] == 'number':
                        validation = question.get('validation', {})
                        response = st.number_input(
                            "Your answer",
                            min_value=validation.get('min', 0),
                            max_value=validation.get('max', 1000),
                            key=f"q_{question['id']}"
                        )
                    
                    elif question['type'] == 'select':
                        response = st.selectbox(
                            "Select an option",
                            question.get('options', []),
                            key=f"q_{question['id']}"
                        )
                    
                    # Navigation
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if current_idx > 0:
                            if st.button("Previous"):
                                session['current_q'] -= 1
                                st.rerun()
                    
                    with col3:
                        is_last = current_idx == len(all_questions) - 1
                        if st.button("Submit" if is_last else "Next", type="primary"):
                            if response is not None or not question.get('required'):
                                session['responses'][question['id']] = response
                                
                                # Adaptive questions
                                if session['survey'].get('adaptive') and current_idx == len(session['survey']['questions']) - 1:
                                    adaptive = generate_adaptive_questions(session['responses'])
                                    if adaptive:
                                        session['adaptive_questions'].extend(adaptive)
                                        st.info(f"Added {len(adaptive)} follow-up questions")
                                
                                if not is_last:
                                    session['current_q'] += 1
                                    st.rerun()
                                else:
                                    # Complete
                                    duration = (datetime.now() - session['start_time']).total_seconds()
                                    quality = calculate_quality_score(session['responses'], duration)
                                    
                                    response_record = {
                                        "id": generate_id("RESP_"),
                                        "survey_id": session['survey_id'],
                                        "user_id": user['id'],
                                        "responses": session['responses'],
                                        "duration": duration,
                                        "quality_score": quality,
                                        "completed_at": datetime.now().isoformat()
                                    }
                                    
                                    st.session_state.responses.append(response_record)
                                    del st.session_state.current_session
                                    
                                    st.success("Survey completed!")
                                    st.balloons()
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Duration", f"{duration:.0f}s")
                                    with col2:
                                        st.metric("Quality Score", f"{quality:.2%}")
                            else:
                                st.warning("This question is required")
        else:
            st.warning("No surveys available")

def show_analytics():
    st.title("📊 Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Surveys", len(st.session_state.surveys))
    with col2:
        st.metric("Total Responses", len(st.session_state.responses))
    with col3:
        avg_quality = np.mean([r['quality_score'] for r in st.session_state.responses]) if st.session_state.responses else 0
        st.metric("Avg Quality", f"{avg_quality:.2%}")
    with col4:
        avg_duration = np.mean([r['duration'] for r in st.session_state.responses]) if st.session_state.responses else 0
        st.metric("Avg Duration", f"{avg_duration:.0f}s")
    
    if st.session_state.responses and PLOTLY_AVAILABLE:
        st.markdown("---")
        
        df = pd.DataFrame(st.session_state.responses)
        
        # Quality distribution
        fig = px.histogram(df, x='quality_score', title='Quality Score Distribution', nbins=10)
        st.plotly_chart(fig, use_container_width=True)
        
        # Response table
        st.subheader("Recent Responses")
        display_cols = ['id', 'survey_id', 'user_id', 'duration', 'quality_score']
        st.dataframe(df[display_cols].head(10), use_container_width=True, hide_index=True)
    elif st.session_state.responses:
        st.subheader("Response Summary")
        df = pd.DataFrame(st.session_state.responses)
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No responses yet")

def show_validation_demo():
    st.title("✅ Validation Demo")
    
    st.markdown("Test the validation system with sample data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Enter Test Data")
        age = st.number_input("Age", 0, 150, 25)
        email = st.text_input("Email", "user@example.com")
        phone = st.text_input("Phone", "9876543210")
        occupation = st.text_input("Occupation", "Software Engineer")
    
    with col2:
        st.subheader("Validation Rules")
        st.code("""
        • Age: 0-120 years
        • Email: Valid format
        • Phone: 10 digits
        • Occupation: AI classification
        """)
    
    if st.button("Validate", type="primary"):
        errors = []
        
        # Validate
        if age < 0 or age > 120:
            errors.append("Age must be 0-120")
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append("Invalid email")
        
        if not re.match(r'^\d{10}$', phone):
            errors.append("Phone must be 10 digits")
        
        # Classification
        classification = classify_occupation(occupation)
        
        # Results
        st.markdown("---")
        
        if errors:
            st.error(f"Found {len(errors)} errors:")
            for error in errors:
                st.write(f"• {error}")
        else:
            st.success("All validations passed!")
        
        st.info(f"Occupation Classification: {classification['category']} (Code: {classification['code']})")

if __name__ == "__main__":
    main()