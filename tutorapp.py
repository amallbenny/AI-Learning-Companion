import streamlit as st
import os
import json
import pandas as pd

from modules.extractor import extract_text_from_pdf
from modules.summarizer import generate_learning_content
from modules.audio import generate_audio
from modules.quiz import generate_quiz
from modules.revision import (
    generate_simplified_explanation,
    generate_ultra_simple_explanation
)

# =============================================================
# PAGE CONFIG
# =============================================================
st.set_page_config(
    page_title="AI Learning Companion",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# THEME / STYLING  (notebook + bookmark look)
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Work+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Work Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Lora', serif;
}
.block-container { padding-top: 1.6rem; max-width: 1150px; }

/* Cover banner */
.cover {
    background: linear-gradient(135deg, #1F2A44 0%, #34406b 100%);
    color: #FBF7F0;
    border-radius: 18px;
    padding: 2.1rem 2.3rem;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
}
.cover::after {
    content: "";
    position: absolute;
    right: -50px; top: -50px;
    width: 170px; height: 170px;
    border-radius: 50%;
    background: rgba(224,164,88,0.18);
}
.cover h1 {
    font-family: 'Lora', serif;
    margin: 0;
    font-size: 2.1rem;
    font-weight: 700;
}
.cover p {
    margin: 0.5rem 0 0;
    opacity: 0.85;
    max-width: 640px;
    font-size: 0.97rem;
}

/* Stepper / bookmark tabs */
.stepper { display:flex; gap:0.5rem; margin: 0 0 1.6rem 0; flex-wrap: wrap; }
.step {
    flex:1; min-width: 140px;
    background:#F4EFE6; color:#9A9486;
    padding: 0.55rem 0.9rem;
    border-radius: 0 10px 10px 0;
    border-left: 6px solid #D8CFC0;
    font-weight:600; font-size:0.85rem;
}
.step .step-num {
    display:inline-block; width:20px; height:20px; border-radius:50%;
    text-align:center; line-height:20px; font-size:0.7rem; margin-right:6px;
    background:#D8CFC0; color:#fff;
}
.step-active { background:#FBF1DE; color:#1F2A44; border-left-color:#E0A458; }
.step-active .step-num { background:#E0A458; }
.step-done { background:#EAF4EE; color:#1F2A44; border-left-color:#3E8E5C; }
.step-done .step-num { background:#3E8E5C; }

/* Info cards */
.card {
    background:#FBF7F0; border:1px solid #E7DFD3; border-radius:14px;
    padding:1rem 1.2rem; text-align:center;
}
.card-label {
    font-size:0.75rem; letter-spacing:0.06em; text-transform:uppercase;
    color:#9A9486; margin-bottom:0.25rem; font-weight:600;
}
.card-value {
    font-family:'Lora', serif; font-size:1.45rem; font-weight:700; color:#1F2A44;
}

/* Section titles */
.section-title {
    font-family:'Lora', serif; font-weight:700; font-size:1.3rem; color:#1F2A44;
    border-bottom: 3px solid #E0A458; display:inline-block;
    padding-bottom:0.2rem; margin: 0.4rem 0 0.9rem 0;
}

/* Banners */
.info-banner {
    background:#EAF4EE; color:#23633F; border-left:4px solid #3E8E5C;
    padding:0.7rem 1rem; border-radius:8px; font-weight:600; margin-bottom:1rem;
}

/* Badges */
.badge {
    display:inline-block; padding:0.18rem 0.65rem; border-radius:6px;
    font-size:0.72rem; font-weight:600; color:#fff; margin-right:0.4rem;
}
.q-num {
    background:#1F2A44; color:#fff; font-weight:700; padding:0.15rem 0.6rem;
    border-radius:6px; margin-right:0.5rem; font-family:'Lora',serif; font-size:0.85rem;
}

/* Sidebar logo */
.sidebar-logo {
    text-align:center; font-family:'Lora', serif; font-weight:700;
    color:#1F2A44; font-size:1.05rem; line-height:1.4; padding: 0.6rem 0 1rem 0;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(31,42,68,0.15);
}

.footer-credit {
    text-align:center; color:#B5AD9D; font-size:0.78rem;
    margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #E7DFD3;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# NAVIGATION / SESSION STATE
# =============================================================
NAV_PAGES = ["📄 Upload PDF", "📖 Learning Content", "📝 Quiz", "📊 Results & Revision"]
STEP_LABELS = ["Upload", "Learn", "Quiz", "Results"]

DEFAULTS = {
    "learning_content": None,
    "extracted_text": "",
    "pdf_name": None,
    "quiz": None,
    "user_answers": {},
    "quiz_submitted": False,
    "revision_data": {},
    "weak_topics": [],
    "score": 0,
    "total": 0,
    "results_detail": [],
    "topic_perf": [],
    "nav": NAV_PAGES[0],
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Apply any pending programmatic navigation BEFORE the sidebar
# radio widget is instantiated (Streamlit forbids changing a
# widget-bound session_state value after the widget is created).
if "nav_pending" in st.session_state:
    target_page = st.session_state.pop("nav_pending")
    st.session_state["nav_radio"] = target_page
    st.session_state["nav"] = target_page


# =============================================================
# HELPERS
# =============================================================
def metric_card(label, value):
    st.markdown(f"""
    <div class="card">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="cover">
        <h1>📚 AI Learning Companion</h1>
        <p>Turn any PDF into a complete personalised study module — a summary, narrated
        topic explanations, an adaptive quiz, and smart revision for the topics that need it most.</p>
    </div>
    """, unsafe_allow_html=True)


def render_stepper():
    completed = [
        bool(st.session_state.extracted_text),
        st.session_state.learning_content is not None,
        st.session_state.quiz is not None,
        st.session_state.quiz_submitted,
    ]
    active_idx = NAV_PAGES.index(st.session_state.nav)

    html = '<div class="stepper">'
    for i, label in enumerate(STEP_LABELS):
        if i == active_idx:
            cls = "step step-active"
        elif completed[i]:
            cls = "step step-done"
        else:
            cls = "step step-pending"
        html += f'<div class="{cls}"><span class="step-num">{i + 1}</span>{label}</div>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def goto(page):
    st.session_state.nav_pending = page
    st.rerun()


# =============================================================
# SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📚<br>AI Learning<br>Companion</div>', unsafe_allow_html=True)

    st.markdown("**🧭 Navigate**")
    selected_page = st.radio(
        "Go to", NAV_PAGES,
        index=NAV_PAGES.index(st.session_state.nav),
        key="nav_radio",
        label_visibility="collapsed"
    )
    st.session_state.nav = selected_page

    st.divider()
    st.markdown("**📌 Session Progress**")

    if st.session_state.extracted_text:
        st.markdown(f"✅ PDF processed — **{st.session_state.pdf_name}**")
    else:
        st.markdown("⬜ No PDF uploaded yet")

    if st.session_state.learning_content:
        n_topics = len(st.session_state.learning_content.get("topics", []))
        st.markdown(f"✅ Learning content ready — **{n_topics} topics**")
    else:
        st.markdown("⬜ Learning content not generated")

    if st.session_state.quiz:
        st.markdown(f"✅ Quiz ready — **{len(st.session_state.quiz)} questions**")
    else:
        st.markdown("⬜ Quiz not generated")

    if st.session_state.quiz_submitted:
        st.markdown(f"✅ Quiz submitted — **{st.session_state.score}/{st.session_state.total}**")
    else:
        st.markdown("⬜ Quiz not submitted")

    st.divider()

    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    with st.expander("ℹ️ About this app"):
        st.write(
            "Upload a PDF and the AI Learning Companion will extract its content, "
            "generate a structured study module with narrated audio, build an "
            "adaptive quiz, and provide simplified or ELI5 revisions for any "
            "topics you find difficult."
        )


# =============================================================
# PAGE 1 — UPLOAD & EXTRACT
# =============================================================
def page_upload():
    st.markdown('<div class="section-title">📄 Step 1 — Upload Your Study Material</div>', unsafe_allow_html=True)
    st.write("Upload a PDF — notes, a textbook chapter, or slides — and let AI build a complete learning module for you.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Only (re)extract when a new file is uploaded
        if st.session_state.pdf_name != uploaded_file.name:
            st.session_state.pdf_name = uploaded_file.name

            with st.spinner("🔍 Extracting text — this can take a little longer for scanned PDFs..."):
                st.session_state.extracted_text = extract_text_from_pdf(file_path)

            # reset everything downstream for the new document
            st.session_state.learning_content = None
            st.session_state.quiz = None
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.revision_data = {}
            st.session_state.weak_topics = []
            st.session_state.results_detail = []
            st.session_state.topic_perf = []
            st.session_state.score = 0
            st.session_state.total = 0

    if st.session_state.pdf_name and not st.session_state.extracted_text:
        st.error("⚠️ No readable text could be extracted from this PDF. Try a different file.")
        return

    if st.session_state.extracted_text:
        char_count = len(st.session_state.extracted_text)
        word_count = len(st.session_state.extracted_text.split())

        st.markdown(
            f'<div class="info-banner">✅ <b>{st.session_state.pdf_name}</b> processed successfully!</div>',
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("📄 File", st.session_state.pdf_name)
        with c2:
            metric_card("🔢 Characters Extracted", f"{char_count:,}")
        with c3:
            metric_card("📝 Word Count", f"{word_count:,}")

        st.write("")

        label = "✨ Generate Learning Content" if not st.session_state.learning_content else "🔁 Regenerate Learning Content"

        if st.button(label, type="primary", use_container_width=True):
            with st.spinner("🧠 AI is reading and structuring your material..."):
                try:
                    st.session_state.learning_content = generate_learning_content(
                        st.session_state.extracted_text
                    )
                    st.session_state.quiz = None
                    st.session_state.user_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.revision_data = {}
                except Exception as e:
                    st.error(f"Something went wrong while generating learning content: {e}")
                else:
                    goto(NAV_PAGES[1])

        if st.session_state.learning_content:
            st.success("Learning content has already been generated. Head to **📖 Learning Content** to view it.")
    else:
        st.info("👆 Upload a PDF to get started.")


# =============================================================
# PAGE 2 — LEARNING CONTENT
# =============================================================
def page_content():
    if not st.session_state.learning_content:
        st.warning("⚠️ No learning content yet. Go to **📄 Upload PDF** and generate it first.")
        return

    content = st.session_state.learning_content

    st.markdown('<div class="section-title">📖 Step 2 — Your Learning Module</div>', unsafe_allow_html=True)

    # --- Summary ---
    st.markdown("#### 📋 Summary")
    with st.container(border=True):
        st.write(content["summary"])

        if st.button("🔊 Listen to Summary", key="summary_audio_btn"):
            with st.spinner("Generating audio..."):
                generate_audio(content["summary"], "audio_files/summary.mp3")

        if os.path.exists("audio_files/summary.mp3"):
            with open("audio_files/summary.mp3", "rb") as f:
                st.audio(f.read(), format="audio/mp3")

    st.write("")

    # --- Topics ---
    topics = content.get("topics", [])
    st.markdown(f"#### 📚 Topics ({len(topics)})")

    for i, topic in enumerate(topics):
        with st.expander(f"{i + 1:02d}  ·  {topic['title']}", expanded=(i == 0)):
            st.markdown("**🧩 Explanation**")
            st.write(topic["explanation"])

            st.markdown("**🔑 Key Points**")
            for p in topic["key_points"]:
                st.markdown(f"- {p}")

            if "examples" in topic:
                st.markdown("**💡 Examples**")
                for e in topic["examples"]:
                    st.markdown(f"- {e}")

            topic_audio = f"audio_files/topic_{i}.mp3"

            if st.button("🔊 Listen to this topic", key=f"audio_{i}"):
                text = topic["title"] + " " + topic["explanation"]
                for p in topic["key_points"]:
                    text += " " + p
                if "examples" in topic:
                    for e in topic["examples"]:
                        text += " " + e

                with st.spinner("Generating audio..."):
                    generate_audio(text, topic_audio)

            if os.path.exists(topic_audio):
                with open(topic_audio, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

    st.write("")
    st.divider()

    if st.button("📝 Continue to Quiz", type="primary", use_container_width=True):
        goto(NAV_PAGES[2])


# =============================================================
# PAGE 3 — QUIZ
# =============================================================
DIFFICULTY_COLORS = {"easy": "#3E8E5C", "medium": "#E0A458", "hard": "#C1502E"}


def grade_quiz():
    quiz = st.session_state.quiz

    topic_total, topic_score = {}, {}
    results_detail = []
    score = 0

    for q in quiz:
        topic = q.get("topic", "Unknown")
        topic_total[topic] = topic_total.get(topic, 0) + 1
        topic_score.setdefault(topic, 0)

    for idx, q in enumerate(quiz):
        user_ans = st.session_state.user_answers.get(idx)
        correct_ans = q["answer"]
        topic = q.get("topic", "Unknown")

        is_correct = user_ans == correct_ans
        if is_correct:
            score += 1
            topic_score[topic] += 1

        results_detail.append({
            "idx": idx,
            "question": q["question"],
            "user_ans": user_ans,
            "correct_ans": correct_ans,
            "is_correct": is_correct,
        })

    topic_perf = []
    weak_topics = []

    for topic, total_q in topic_total.items():
        correct = topic_score.get(topic, 0)
        accuracy = (correct / total_q) * 100
        topic_perf.append({"Topic": topic, "Correct": correct, "Total": total_q, "Accuracy": accuracy})
        if accuracy < 60:
            weak_topics.append(topic)

    st.session_state.score = score
    st.session_state.total = len(quiz)
    st.session_state.results_detail = results_detail
    st.session_state.topic_perf = topic_perf
    st.session_state.weak_topics = weak_topics
    st.session_state.quiz_submitted = True


def page_quiz():
    if not st.session_state.learning_content:
        st.warning("⚠️ Generate learning content first on the **📄 Upload PDF** page.")
        return

    content = st.session_state.learning_content

    st.markdown('<div class="section-title">📝 Step 3 — Test Your Understanding</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Generate an AI-crafted quiz based on the topics you just learned, with a mix of easy, medium and hard questions.")
    with col2:
        label = "🎲 Generate Quiz" if not st.session_state.quiz else "🔁 Regenerate Quiz"
        if st.button(label, use_container_width=True):
            with st.spinner("Crafting quiz questions..."):
                st.session_state.quiz = generate_quiz(content, os.getenv("GEMINI_API_KEY"))
                st.session_state.user_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.revision_data = {}
                st.session_state.weak_topics = []
                st.session_state.results_detail = []
                st.session_state.topic_perf = []
            st.rerun()

    if st.session_state.quiz is None:
        st.info("No quiz yet — click **Generate Quiz** to begin.")
        return

    if len(st.session_state.quiz) == 0:
        st.error("⚠️ Quiz generation failed or returned no questions. Please try again.")
        return

    quiz = st.session_state.quiz
    total = len(quiz)
    answered = len(st.session_state.user_answers)

    st.progress(min(answered / total, 1.0), text=f"Answered {answered} / {total}")

    for idx, q in enumerate(quiz):
        diff = str(q.get("difficulty", "medium")).lower()
        diff_color = DIFFICULTY_COLORS.get(diff, "#9A9486")
        topic = q.get("topic", "")

        with st.container(border=True):
            st.markdown(
                f'<span class="q-num">Q{idx + 1}</span>'
                f'<span class="badge" style="background:{diff_color}">{diff.title()}</span>'
                f'<span class="badge" style="background:#34406b">{topic}</span>',
                unsafe_allow_html=True
            )

            st.markdown(f"**{q['question']}**")

            selected = st.radio(
                "Select your answer",
                q["options"],
                key=f"q_{idx}",
                index=None,
                label_visibility="collapsed",
                disabled=st.session_state.quiz_submitted,
            )

            if selected is not None:
                st.session_state.user_answers[idx] = selected

    st.write("")

    if not st.session_state.quiz_submitted:
        if st.button("✅ Submit Quiz", type="primary", use_container_width=True):
            grade_quiz()
            goto(NAV_PAGES[3])
    else:
        st.success("Quiz submitted! Head to **📊 Results & Revision** to see how you did.")
        if st.button("➡️ View Results", type="primary", use_container_width=True):
            goto(NAV_PAGES[3])


# =============================================================
# PAGE 4 — RESULTS & REVISION
# =============================================================
def render_revision_block(topic_title, content):
    original_explanation = None
    for topic_obj in content["topics"]:
        if topic_obj["title"] == topic_title:
            original_explanation = topic_obj["explanation"]
            break

    os.makedirs("audio_files", exist_ok=True)
    safe_title = "".join(c if c.isalnum() else "_" for c in topic_title)

    norm_audio = f"audio_files/rev_norm_{safe_title}.mp3"
    simp_audio = f"audio_files/rev_simp_{safe_title}.mp3"
    eli_audio = f"audio_files/rev_eli_{safe_title}.mp3"

    with st.container(border=True):
        st.markdown(f"#### 📘 {topic_title}")

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button("🟢 Normal Revision", key=f"nr_{topic_title}", use_container_width=True):
                st.session_state.revision_data[f"normal_{topic_title}"] = original_explanation
                if original_explanation and not os.path.exists(norm_audio):
                    with st.spinner("Generating audio..."):
                        generate_audio(original_explanation, norm_audio)

        with c2:
            if st.button("🟡 Simplified", key=f"sp_{topic_title}", use_container_width=True):
                with st.spinner("Simplifying..."):
                    result = generate_simplified_explanation(topic_title, original_explanation)
                    try:
                        data = json.loads(result)
                        st.session_state.revision_data[f"simp_{topic_title}"] = data
                        if os.path.exists(simp_audio):
                            os.remove(simp_audio)
                    except Exception:
                        st.session_state.revision_data[f"simp_{topic_title}"] = None

        with c3:
            if st.button("🔴 I still don't get it", key=f"eli_{topic_title}", use_container_width=True):
                with st.spinner("Generating an ELI5 explanation..."):
                    result = generate_ultra_simple_explanation(topic_title, original_explanation)
                    try:
                        data = json.loads(result)
                        st.session_state.revision_data[f"eli_{topic_title}"] = data
                        if os.path.exists(eli_audio):
                            os.remove(eli_audio)
                    except Exception:
                        st.session_state.revision_data[f"eli_{topic_title}"] = None

        # --- Normal revision output ---
        if f"normal_{topic_title}" in st.session_state.revision_data:
            st.markdown("**📖 Original Explanation**")
            st.write(st.session_state.revision_data[f"normal_{topic_title}"])

        if os.path.exists(norm_audio):
            with open(norm_audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        # --- Simplified output ---
        if f"simp_{topic_title}" in st.session_state.revision_data:
            data = st.session_state.revision_data[f"simp_{topic_title}"]
            if data:
                st.markdown("**🟡 Simplified Explanation**")
                st.write(data["simple_explanation"])
                for p in data["key_points"]:
                    st.markdown(f"- {p}")

                if not os.path.exists(simp_audio):
                    with st.spinner("Generating audio..."):
                        generate_audio(data["simple_explanation"], simp_audio)
            else:
                st.error("Couldn't read the simplified explanation. Please try again.")

        if os.path.exists(simp_audio):
            with open(simp_audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        # --- ELI5 output ---
        if f"eli_{topic_title}" in st.session_state.revision_data:
            data = st.session_state.revision_data[f"eli_{topic_title}"]
            if data:
                st.markdown("**🔴 ELI5 Explanation**")
                st.write(data["eli5_explanation"])
                st.info(f"💡 Analogy: {data['analogy']}")

                if not os.path.exists(eli_audio):
                    with st.spinner("Generating audio..."):
                        generate_audio(data["eli5_explanation"], eli_audio)
            else:
                st.error("Couldn't read the ELI5 explanation. Please try again.")

        if os.path.exists(eli_audio):
            with open(eli_audio, "rb") as f:
                st.audio(f.read(), format="audio/mp3")

        # --- Mini recheck ---
        st.markdown("**🧪 Quick Check**")
        for idx, q in enumerate(st.session_state.quiz):
            if q.get("topic") == topic_title:
                st.write(q["question"])

                ans = st.radio(
                    "Answer again",
                    q["options"],
                    key=f"rev_q_{topic_title}_{idx}",
                    index=None,
                    label_visibility="collapsed",
                )

                if st.button("Check Answer", key=f"check_{topic_title}_{idx}"):
                    if ans == q["answer"]:
                        st.success("Correct 🎉")
                    else:
                        st.error(f"Wrong ❌ — Correct answer: {q['answer']}")


def page_results():
    if not st.session_state.quiz_submitted:
        st.warning("⚠️ Complete and submit the quiz first on the **📝 Quiz** page to see your results.")
        return

    content = st.session_state.learning_content
    score = st.session_state.score
    total = st.session_state.total
    percentage = (score / total) * 100 if total else 0

    st.markdown('<div class="section-title">📊 Step 4 — Results & Smart Revision</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("🎯 Score", f"{score} / {total}")
    with c2:
        metric_card("📈 Percentage", f"{percentage:.1f}%")
    with c3:
        if percentage >= 75:
            status = "Excellent 🎉"
        elif percentage >= 50:
            status = "Moderate"
        else:
            status = "Needs Work"
        metric_card("🏅 Status", status)

    st.write("")
    st.progress(percentage / 100)

    if percentage >= 75:
        st.success("Excellent understanding 🎉")
    elif percentage >= 50:
        st.warning("Moderate understanding — some revision recommended")
    else:
        st.error("Weak understanding — revision recommended")

    # --- Detailed review ---
    with st.expander("📋 Detailed Question Review"):
        for r in st.session_state.results_detail:
            if r["is_correct"]:
                st.success(f"Q{r['idx'] + 1}: {r['question']}")
            else:
                st.error(f"Q{r['idx'] + 1}: {r['question']}")
                st.caption(f"Your answer: {r['user_ans'] or '— not answered —'}  |  Correct answer: {r['correct_ans']}")

    st.divider()

    # --- Topic-wise performance ---
    st.markdown("#### 📊 Topic-wise Performance")

    df = pd.DataFrame(st.session_state.topic_perf).set_index("Topic")
    st.bar_chart(df["Accuracy"])

    for row in st.session_state.topic_perf:
        st.write(f"📘 **{row['Topic']}**: {row['Correct']}/{row['Total']}  ({row['Accuracy']:.1f}%)")

    weak_topics = st.session_state.weak_topics

    st.divider()

    if weak_topics:
        st.markdown("#### 🧠 Smart Revision — Focus Areas")
        st.warning("Topics that need revision: " + ", ".join(weak_topics))

        for t in weak_topics:
            render_revision_block(t, content)
    else:
        st.success("🎯 No weak topics detected — great job!")


# =============================================================
# MAIN
# =============================================================
render_header()
render_stepper()

PAGES = {
    NAV_PAGES[0]: page_upload,
    NAV_PAGES[1]: page_content,
    NAV_PAGES[2]: page_quiz,
    NAV_PAGES[3]: page_results,
}

PAGES[st.session_state.nav]()

st.markdown(
    '<div class="footer-credit">AI Learning Companion · Built with Streamlit, PyMuPDF, PaddleOCR &amp; Gemini</div>',
    unsafe_allow_html=True
)