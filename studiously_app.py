
import os
import io
import json
import re
import html
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Studiously AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# 2. CUSTOM THEME
# =====================================================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --background: #faf8ff;
        --surface: #ffffff;
        --purple: #7c3aed;
        --purple-dark: #6d28d9;
        --pink: #ec4899;
        --text: #302344;
        --muted: #6b5c7d;
        --border: #e8def5;
    }

    /* Main page */

    .stApp {
        background-color: var(--background) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif;
    }

    .stApp p,
    .stApp label,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {
        color: var(--text);
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text) !important;
        font-weight: 800 !important;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] small {
        color: var(--muted) !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--text) !important;
    }

    /* Brand */

    .brand {
        font-family: 'Manrope', sans-serif;
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #7c3aed !important;
        margin-bottom: 4px;
    }

    .brand-pink {
        color: #ec4899 !important;
    }

    .small-muted {
        color: #6b5c7d !important;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Hero: use native Streamlit components for its content */

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e8def5 !important;
        border-radius: 20px !important;
    }

    .hero-badge {
        display: inline-block;
        background: #ffffff;
        border: 1px solid #e8def5;
        border-radius: 30px;
        padding: 8px 14px;
        color: #7c3aed !important;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.4px;
    }

    /* Feature cards */

    .feature-card {
        background: #ffffff;
        border: 1px solid #e8def5;
        border-radius: 17px;
        padding: 20px;
        min-height: 150px;
        box-shadow: 0 5px 18px rgba(74, 40, 110, 0.04);
    }

    .feature-icon {
        font-size: 27px;
        margin-bottom: 10px;
    }

    .feature-title {
        color: #302344 !important;
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .feature-description {
        color: #6b5c7d !important;
        font-size: 13px;
        line-height: 1.7;
    }

    /* Text inputs */

    .stTextInput input,
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #302344 !important;
        -webkit-text-fill-color: #302344 !important;
        border: 1px solid #d9c9ee !important;
        border-radius: 11px !important;
        caret-color: #7c3aed !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #897d99 !important;
        -webkit-text-fill-color: #897d99 !important;
        opacity: 1 !important;
    }

    /* Select boxes */

    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: #d9c9ee !important;
        border-radius: 11px !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: #302344 !important;
    }

    /* Dropdown menu */

    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background-color: #ffffff !important;
    }

    [role="option"] {
        background-color: #ffffff !important;
        color: #302344 !important;
    }

    [role="option"]:hover {
        background-color: #f3edff !important;
    }

    /* Standard buttons */

    .stApp .stButton > button,
    .stApp [data-testid="stDownloadButton"] > button {
        background-color: #ffffff !important;
        color: #6d28d9 !important;
        border: 1px solid #d9c9ee !important;
        border-radius: 11px !important;
        font-weight: 700 !important;
        min-height: 42px;
        transition: all 0.2s ease;
    }

    .stApp .stButton > button:hover,
    .stApp [data-testid="stDownloadButton"] > button:hover {
        background-color: #f3edff !important;
        color: #5b21b6 !important;
        border-color: #a78bfa !important;
    }

    /* Primary buttons */

    .stApp .stFormSubmitButton > button,
    .stApp .stButton > button[kind="primary"] {
        background: linear-gradient(
            100deg,
            #7c3aed,
            #a855f7
        ) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #7c3aed !important;
        border-radius: 11px !important;
        font-weight: 800 !important;
        min-height: 44px;
        box-shadow: 0 5px 14px rgba(124, 58, 237, 0.14);
    }

    .stApp .stFormSubmitButton > button:hover,
    .stApp .stButton > button[kind="primary"]:hover {
        background: #6d28d9 !important;
        color: #ffffff !important;
    }

    /* Tabs */

    [data-testid="stTabs"] button {
        color: #6b5c7d !important;
        font-weight: 700 !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #7c3aed !important;
    }

    /* Metrics */

    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e8def5;
        border-radius: 15px;
        padding: 14px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #6b5c7d !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: #7c3aed !important;
    }

    /* Expanders */

    [data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e8def5;
        border-radius: 12px;
    }

    [data-testid="stExpander"] summary {
        color: #302344 !important;
    }

    /* Chat */

    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #e8def5;
        border-radius: 13px;
    }

    /* Footer */

    .app-footer {
        text-align: center;
        color: #6b5c7d !important;
        padding: 28px 0 12px;
        font-size: 13px;
    }

    .app-footer strong {
        color: #7c3aed !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 3. GEMINI API CONFIGURATION
# =====================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.1-flash-lite"

client = genai.Client(api_key=API_KEY) if API_KEY else None


# =====================================================
# 4. SESSION STATE
# =====================================================

if "material" not in st.session_state:
    st.session_state.material = None

if "history" not in st.session_state:
    st.session_state.history = []

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []


# =====================================================
# 5. GENERATE STUDY MATERIAL
# =====================================================

def generate_material(topic, difficulty, question_count):

    if client is None:
        raise ValueError(
            "Gemini API key is missing. Set GEMINI_API_KEY "
            "in your Windows environment variables."
        )

    prompt = f"""
You are a friendly AI study tutor.

Topic: {topic}
Learning level: {difficulty}
Number of questions: {question_count}

Create a concise study pack for a student.

Return valid JSON only in this format:

{{
  "explanation": "Clear explanation of the topic",
  "key_points": [
    "Important point 1",
    "Important point 2"
  ],
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "answer_explanation": "Short explanation"
    }}
  ]
}}

Requirements:
- Explain concepts in simple, accurate English.
- Include 5 to 7 useful key points.
- Generate exactly {question_count} questions.
- Every question must have exactly four distinct options.
- correct_answer must exactly match one of the options.
- Include a short explanation for every answer.
- Avoid duplicate questions.
- Do not return Markdown code fences.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=3000,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise ValueError("The AI returned an empty response.")

    data = json.loads(response.text)

    if not isinstance(data, dict):
        raise ValueError("The AI returned an invalid study pack.")

    if not isinstance(data.get("explanation"), str):
        raise ValueError("The explanation is missing.")

    if not isinstance(data.get("key_points"), list):
        raise ValueError("The key points are missing.")

    if not isinstance(data.get("questions"), list):
        raise ValueError("The questions are missing.")

    valid_questions = []

    for question in data["questions"]:

        if not isinstance(question, dict):
            continue

        options = question.get("options")
        answer = question.get("correct_answer")

        if (
            isinstance(question.get("question"), str)
            and isinstance(options, list)
            and len(options) == 4
            and all(isinstance(option, str) for option in options)
            and answer in options
        ):
            valid_questions.append(question)

    if not valid_questions:
        raise ValueError(
            "The AI did not generate valid questions. Please retry."
        )

    data["questions"] = valid_questions
    data["topic"] = topic
    data["difficulty"] = difficulty
    data["created_at"] = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    return data


# =====================================================
# 6. CREATE PDF
# =====================================================

def create_pdf(data):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=23,
        leading=29,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#7c3aed"),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#7c3aed"),
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#302344"),
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "CustomSmall",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#6b5c7d"),
        spaceAfter=5,
    )

    story = [
        Paragraph("STUDIOUSLY AI", title_style),
        Paragraph(
            "Your personal AI study companion",
            small_style,
        ),
        Spacer(1, 10),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#e8def5"),
        ),
        Spacer(1, 12),
        Paragraph(
            html.escape(str(data["topic"])),
            styles["Heading1"],
        ),
        Paragraph(
            "Learning level: "
            + html.escape(str(data["difficulty"])),
            small_style,
        ),
        Paragraph("Concept Explanation", heading_style),
    ]

    for paragraph in str(data["explanation"]).splitlines():

        paragraph = paragraph.strip()

        if paragraph:
            story.append(
                Paragraph(
                    html.escape(paragraph),
                    body_style,
                )
            )

    story.append(
        Paragraph("Key Takeaways", heading_style)
    )

    for point in data["key_points"]:

        story.append(
            Paragraph(
                "&#8226; " + html.escape(str(point)),
                body_style,
            )
        )

    story.append(
        Paragraph("Practice Questions", heading_style)
    )

    for index, question in enumerate(
        data["questions"],
        start=1,
    ):

        elements = [
            Paragraph(
                f"<b>{index}. "
                f"{html.escape(str(question['question']))}</b>",
                body_style,
            )
        ]

        for option in question["options"]:

            elements.append(
                Paragraph(
                    "&#8226; " + html.escape(str(option)),
                    small_style,
                )
            )

        elements.append(
            Paragraph(
                "<b>Correct answer:</b> "
                + html.escape(str(question["correct_answer"])),
                body_style,
            )
        )

        elements.append(
            Paragraph(
                "<b>Explanation:</b> "
                + html.escape(
                    str(question.get("answer_explanation", ""))
                ),
                small_style,
            )
        )

        elements.append(Spacer(1, 8))
        story.append(KeepTogether(elements))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Generated with Studiously AI",
            small_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# =====================================================
# 7. AI TUTOR
# =====================================================

def ask_tutor(topic, notes, question):

    if client is None:
        raise ValueError("Gemini API key is missing.")

    prompt = f"""
You are the personal tutor in Studiously AI.

Study topic: {topic}

Reference notes:
{notes[:2500]}

Student question:
{question}

Answer in simple English.
Explain step by step if necessary.
Give a short example when useful.
Be concise and accurate.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=800,
        ),
    )

    if not response.text:
        raise ValueError("The tutor returned an empty response.")

    return response.text


# =====================================================
# 8. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            study<span class="brand-pink">lously</span> AI
        </div>
        <div class="small-muted">
            Your little study companion ✨
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### ⚙️ Preferences")

    difficulty = st.selectbox(
        "Learning level",
        ["Beginner", "Intermediate", "Advanced"],
        key="learning_level",
    )

    question_count = st.selectbox(
        "Number of questions",
        [5, 10, 15],
        index=0,
        key="question_count",
    )

    st.divider()

    st.markdown("### 📚 Recent topics")

    if st.session_state.history:

        for index, item in enumerate(
            reversed(st.session_state.history[-8:])
        ):

            label = item["topic"][:28]

            if st.button(
                f"📖 {label}",
                key=f"recent_{index}",
                use_container_width=True,
            ):

                st.session_state.material = item
                st.session_state.quiz_result = None
                st.session_state.tutor_messages = []
                st.rerun()

        if st.button(
            "🗑️ Clear history",
            use_container_width=True,
        ):

            st.session_state.history = []
            st.rerun()

    else:

        st.caption(
            "Your generated topics will appear here."
        )

    st.divider()

    st.markdown("### 💜 About")

    st.markdown(
        """
        <div class="small-muted">
            Learn concepts, practise questions, test your
            knowledge and ask your AI tutor.
            <br><br>
            Built with Python, Streamlit and Gemini.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# 9. HERO SECTION
# =====================================================

# Native Streamlit components are used for the hero text.
# This avoids displaying HTML tags as code.

with st.container(border=True):

    st.markdown(
        """
        <div class="hero-badge">
            ✨ YOUR PERSONAL AI STUDY SPACE
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.title("Study smarter, not harder.")

    st.markdown(
        """
        <div class="small-muted">
            Turn confusing concepts into clear notes, practice
            questions and interactive learning experiences —
            all in one place.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")


# =====================================================
# 10. GENERATE STUDY PACK
# =====================================================

st.header("What are we learning today?")

st.markdown(
    """
    <div class="small-muted">
        Enter a subject, concept or exam topic to get started.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("study_generation_form"):

    topic_input = st.text_input(
        "Study topic",
        placeholder=(
            "Try Python OOP, DBMS normalization, "
            "or neural networks..."
        ),
        max_chars=200,
    )

    generate_button = st.form_submit_button(
        "✨ Generate my study pack",
        type="primary",
        use_container_width=True,
    )


if generate_button:

    topic_input = topic_input.strip()

    if not topic_input:

        st.warning("Please enter a study topic first.")

    elif client is None:

        st.error(
            "Gemini API key not found. Set GEMINI_API_KEY "
            "in Windows environment variables, then restart "
            "Command Prompt."
        )

    else:

        try:

            with st.spinner(
                "✨ Creating your study pack. This may take a moment..."
            ):

                new_material = generate_material(
                    topic_input,
                    difficulty,
                    question_count,
                )

            st.session_state.material = new_material
            st.session_state.quiz_result = None
            st.session_state.tutor_messages = []

            st.session_state.history = [
                item
                for item in st.session_state.history
                if not (
                    item["topic"].lower() == topic_input.lower()
                    and item["difficulty"] == difficulty
                )
            ]

            st.session_state.history.append(new_material)

            st.rerun()

        except Exception as error:

            st.error(
                "We couldn't generate the study pack. "
                "Check your API key and model availability, "
                "then try again."
            )

            with st.expander("Technical details"):

                st.code(str(error))


# =====================================================
# 11. STUDY WORKSPACE
# =====================================================

material = st.session_state.material

if material:

    st.divider()

    st.header(f"📖 {material['topic']}")

    st.caption(
        f"{material['difficulty']} level  •  "
        f"{len(material['questions'])} questions  •  "
        f"Created {material['created_at']}"
    )

    notes_tab, practice_tab, quiz_tab, tutor_tab = st.tabs(
        [
            "📚 Study Notes",
            "💡 Practice",
            "🎯 Quiz Mode",
            "🤖 AI Tutor",
        ]
    )

    # -------------------------------------------------
    # STUDY NOTES
    # -------------------------------------------------

    with notes_tab:

        st.subheader("🧠 Concept explanation")

        st.markdown(material["explanation"])

        st.subheader("📌 Key takeaways")

        for point in material["key_points"]:

            st.markdown(f"- {point}")

        safe_filename = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            material["topic"],
        ).strip("_") or "study_notes"

        try:

            pdf_bytes = create_pdf(material)

            st.download_button(
                "📄 Download study pack as PDF",
                data=pdf_bytes,
                file_name=f"Studiously_AI_{safe_filename}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as error:

            st.error("Could not create the PDF.")

            with st.expander("PDF technical details"):

                st.code(str(error))

    # -------------------------------------------------
    # PRACTICE
    # -------------------------------------------------

    with practice_tab:

        st.subheader("💡 Learn at your own pace")

        st.caption(
            "Try answering each question before revealing the answer."
        )

        for index, question in enumerate(
            material["questions"],
            start=1,
        ):

            with st.expander(
                f"Question {index}: {question['question']}"
            ):

                for option_index, option in enumerate(
                    question["options"]
                ):

                    st.markdown(
                        f"**{chr(65 + option_index)}.** {option}"
                    )

                with st.expander("✨ Reveal answer"):

                    st.success(
                        "Correct answer: "
                        + question["correct_answer"]
                    )

                    st.write(
                        question.get("answer_explanation", "")
                    )

    # -------------------------------------------------
    # QUIZ
    # -------------------------------------------------

    with quiz_tab:

        st.subheader("🎯 Test your understanding")

        quiz_id = str(
            hash(
                material["topic"]
                + material["created_at"]
            )
        )

        with st.form(f"quiz_form_{quiz_id}"):

            quiz_answers = {}

            for index, question in enumerate(
                material["questions"]
            ):

                st.markdown(
                    f"**{index + 1}. {question['question']}**"
                )

                quiz_answers[index] = st.radio(
                    "Choose your answer",
                    question["options"],
                    index=None,
                    key=f"quiz_answer_{quiz_id}_{index}",
                    label_visibility="collapsed",
                )

            submit_quiz = st.form_submit_button(
                "Check my score",
                type="primary",
                use_container_width=True,
            )

        if submit_quiz:

            score = sum(
                quiz_answers[index] == question["correct_answer"]
                for index, question in enumerate(
                    material["questions"]
                )
            )

            total = len(material["questions"])

            st.session_state.quiz_result = {
                "quiz_id": quiz_id,
                "answers": quiz_answers,
                "score": score,
                "percentage": round(score / total * 100),
            }

        result = st.session_state.quiz_result

        if result and result["quiz_id"] == quiz_id:

            col1, col2 = st.columns(2)

            col1.metric(
                "Your score",
                f"{result['score']}/{len(material['questions'])}",
            )

            col2.metric(
                "Percentage",
                f"{result['percentage']}%",
            )

            if result["percentage"] >= 80:

                st.success("Excellent work! 🎉")

            elif result["percentage"] >= 50:

                st.info(
                    "Good effort! Review the explanations to improve. 💜"
                )

            else:

                st.warning(
                    "Keep practising. You can improve with revision! 🌱"
                )

            st.subheader("📝 Answer review")

            for index, question in enumerate(
                material["questions"]
            ):

                selected = result["answers"][index]
                correct = question["correct_answer"]

                if selected == correct:

                    st.success(
                        f"{index + 1}. Correct — {correct}"
                    )

                else:

                    st.error(
                        f"{index + 1}. Your answer: "
                        f"{selected if selected else 'Not answered'}"
                    )

                    st.write(f"Correct answer: {correct}")

                st.caption(
                    question.get("answer_explanation", "")
                )

            if st.button(
                "🔄 Try quiz again",
                use_container_width=True,
            ):

                st.session_state.quiz_result = None

                for index in range(len(material["questions"])):

                    key = f"quiz_answer_{quiz_id}_{index}"

                    if key in st.session_state:
                        del st.session_state[key]

                st.rerun()

    # -------------------------------------------------
    # AI TUTOR
    # -------------------------------------------------

    with tutor_tab:

        st.subheader("🤖 Your personal AI tutor")

        st.markdown(
            """
            <div class="small-muted">
                Ask follow-up questions about your current topic.
                Your tutor will explain concepts in simple language.
            </div>
            """,
            unsafe_allow_html=True,
        )

        for message in st.session_state.tutor_messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

        user_question = st.chat_input(
            f"Ask about {material['topic']}..."
        )

        if user_question:

            st.session_state.tutor_messages.append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            with st.chat_message("user"):

                st.markdown(user_question)

            with st.chat_message("assistant"):

                try:

                    with st.spinner("Your tutor is thinking..."):

                        answer = ask_tutor(
                            material["topic"],
                            material["explanation"],
                            user_question,
                        )

                    st.markdown(answer)

                    st.session_state.tutor_messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as error:

                    st.error(
                        "The tutor could not answer right now. "
                        "Please check the API and try again."
                    )

                    with st.expander("Technical details"):

                        st.code(str(error))

        if st.session_state.tutor_messages:

            if st.button("🗑️ Clear tutor conversation"):

                st.session_state.tutor_messages = []
                st.rerun()


# =====================================================
# 12. WELCOME FEATURES
# =====================================================

else:

    st.subheader("✨ Your study space")

    st.markdown(
        """
        <div class="small-muted">
            Generate your first study pack to unlock your learning tools.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📚</div>
                <div class="feature-title">Understand</div>
                <div class="feature-description">
                    Turn difficult topics into clear explanations
                    and useful takeaways.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Practise</div>
                <div class="feature-description">
                    Strengthen your understanding with practice
                    questions and interactive quizzes.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Ask your AI tutor</div>
                <div class="feature-description">
                    Explore concepts and clear up confusion
                    with follow-up questions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =====================================================
# 13. FOOTER
# =====================================================

st.markdown(
    """
    <div class="app-footer">
        Made with 💜 by <strong>Studiously AI</strong>
        <br>
        Learn something new every day.
    </div>
    """,
    unsafe_allow_html=True,
)
