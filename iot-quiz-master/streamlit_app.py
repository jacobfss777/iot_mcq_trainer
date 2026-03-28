"""
IoT Quiz Master — Streamlit version styled to match the Flask UI.
Run locally: streamlit run streamlit_app.py
"""
import html as html_module
import json
import os
import random

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE, "questions.json")


def esc(s):
    return html_module.escape(str(s) if s is not None else "")


@st.cache_data
def load_questions():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    flat = []
    for topic in data:
        for q in topic["questions"]:
            qc = dict(q)
            qc["topic"] = topic["topicName"]
            if "correctAnswer" in qc:
                qc["answer"] = qc.pop("correctAnswer")
            flat.append(qc)
    return flat


def topic_counts(questions):
    m = {}
    for q in questions:
        t = q.get("topic") or "General"
        m[t] = m.get(t, 0) + 1
    return sorted(m.items(), key=lambda x: x[0])


def check_answer(q, mcq_pick, multi_pick, text_val, match_picks):
    t = q["type"]
    ans = q.get("answer")
    if t == "mcq":
        return mcq_pick == ans
    if t == "multi-select":
        correct = set(ans) if isinstance(ans, list) else set()
        opts = q.get("options", [])
        user = {opts[i] for i in (multi_pick or []) if isinstance(i, int) and 0 <= i < len(opts)}
        return correct == user
    if t == "text-input":
        u = (text_val or "").strip().lower()
        c = (str(ans) if ans is not None else "").strip().lower()
        return u == c
    if t == "matching":
        correct = ans or {}
        for item in q.get("items", []):
            if match_picks.get(item) != correct.get(item):
                return False
        return True
    return False


def mistake_record(q, mcq_pick, multi_pick, text_val, match_picks):
    t = q["type"]
    ans = q.get("answer")
    if t == "mcq":
        return (mcq_pick if mcq_pick is not None else "(none)"), ans
    if t == "multi-select":
        labels = [q["options"][i] for i in sorted(multi_pick or []) if 0 <= i < len(q["options"])]
        return ", ".join(labels) or "(none)", ", ".join(ans) if isinstance(ans, list) else ans
    if t == "text-input":
        return text_val or "(none)", ans
    if t == "matching":
        u = ", ".join(f"{k} → {v}" for k, v in sorted((match_picks or {}).items()))
        c = ", ".join(f"{k} → {v}" for k, v in sorted((ans or {}).items()))
        return u, c
    return "(none)", ans


def init_session():
    defaults = {
        "page": "home",
        "quiz_questions": [],
        "q_idx": 0,
        "score": 0,
        "mistakes": [],
        "show_answer": False,
        "last_correct": False,
        "review_open": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go_home():
    st.session_state.page = "home"
    st.session_state.quiz_questions = []
    st.session_state.q_idx = 0
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.show_answer = False
    st.session_state.review_open = False


def start_quiz(questions, topic=None):
    pool = [q for q in questions if topic is None or q.get("topic") == topic]
    random.shuffle(pool)
    st.session_state.quiz_questions = pool
    st.session_state.q_idx = 0
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.show_answer = False
    st.session_state.review_open = False
    st.session_state.page = "quiz"


def inject_flask_like_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        :root {
          --iot-bg: #0f172a;
          --iot-card: #1e293b;
          --iot-card-hover: #273548;
          --iot-accent: #6366f1;
          --iot-accent-hover: #818cf8;
          --iot-text: #e2e8f0;
          --iot-muted: #94a3b8;
          --iot-green: #22c55e;
          --iot-green-bg: rgba(34,197,94,.12);
          --iot-red: #ef4444;
          --iot-red-bg: rgba(239,68,68,.12);
          --iot-radius: 12px;
        }

        html, body, [class*="css"] {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        .stApp {
          background-color: var(--iot-bg) !important;
          color: #f1f5f9 !important;
          color-scheme: dark;
        }

        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header[data-testid="stHeader"] {
          background-color: var(--iot-bg) !important;
          border-bottom: 1px solid #1e293b;
        }

        .block-container {
          max-width: 800px !important;
          padding-top: 2rem !important;
          padding-left: 1.25rem !important;
          padding-right: 1.25rem !important;
          padding-bottom: 2rem !important;
        }

        /* Headings & text */
        h1, h2, h3 {
          color: var(--iot-text) !important;
          font-weight: 700 !important;
        }
        .stMarkdown, .stMarkdown p, label, span {
          color: var(--iot-text) !important;
        }
        .stCaption, [data-testid="stCaptionContainer"] {
          color: var(--iot-muted) !important;
        }

        /* Home hero */
        .iot-hero {
          text-align: center;
          padding: 2rem 0 1.5rem;
        }
        .iot-hero h1 {
          font-size: clamp(1.8rem, 5vw, 2.5rem);
          font-weight: 800 !important;
          letter-spacing: -0.02em;
          margin-bottom: 0.5rem;
          border: none;
        }
        .iot-hero .iot-accent { color: var(--iot-accent) !important; }
        .iot-hero p {
          color: var(--iot-muted) !important;
          font-size: 1.1rem;
          max-width: 420px;
          margin: 0 auto 2rem;
          line-height: 1.6;
        }

        /* Buttons */
        .stButton > button {
          border-radius: var(--iot-radius) !important;
          font-weight: 600 !important;
          padding: 0.75rem 1.5rem !important;
          transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        .stButton > button[kind="primary"] {
          background-color: var(--iot-accent) !important;
          color: #ffffff !important;
          border: none !important;
          box-shadow: 0 4px 14px rgba(99,102,241,.35);
        }
        .stButton > button[kind="primary"]:hover {
          background-color: var(--iot-accent-hover) !important;
          border: none !important;
        }
        .stButton > button[kind="secondary"] {
          background-color: var(--iot-card) !important;
          color: var(--iot-text) !important;
          border: 1px solid #334155 !important;
        }
        .stButton > button[kind="secondary"]:hover {
          background-color: var(--iot-card-hover) !important;
          border-color: #475569 !important;
        }

        /* Progress bar (Streamlit native) — hidden; we use custom bar */
        div[data-testid="stProgress"] > div > div > div {
          background: linear-gradient(90deg, var(--iot-accent), #818cf8) !important;
        }
        div[data-testid="stProgress"] > div > div {
          background-color: #334155 !important;
          border-radius: 99px !important;
          height: 6px !important;
        }

        /* Question card shell */
        .question-card {
          background: var(--iot-card);
          border-radius: var(--iot-radius);
          padding: 1.75rem 2rem;
          margin-bottom: 1rem;
          border: 1px solid #334155;
        }
        .q-type-badge {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.06em;
          padding: 0.25rem 0.65rem;
          border-radius: 99px;
          background: rgba(99,102,241,.15);
          color: var(--iot-accent) !important;
          margin-bottom: 1rem;
        }
        .question-text {
          font-size: 1.12rem;
          font-weight: 600;
          line-height: 1.55;
          color: var(--iot-text) !important;
          white-space: pre-wrap;
        }
        .hint-iot {
          font-size: 0.85rem;
          color: var(--iot-muted) !important;
          margin-top: 0.5rem;
          font-style: italic;
        }

        /* Custom HTML progress row */
        .progress-wrap { margin-bottom: 1.25rem; }
        .progress-info {
          display: flex;
          justify-content: space-between;
          font-size: 0.85rem;
          color: var(--iot-muted);
          margin-bottom: 0.45rem;
        }
        .progress-bar-iot {
          height: 6px;
          background: #334155;
          border-radius: 99px;
          overflow: hidden;
        }
        .progress-fill-iot {
          height: 100%;
          background: var(--iot-accent);
          border-radius: 99px;
          transition: width 0.4s ease;
        }

        /* Radio — card-like options + high-contrast text (Streamlit nests text in p/span) */
        div[data-testid="stRadio"] label {
          background-color: #273548 !important;
          border: 2px solid #475569 !important;
          border-radius: var(--iot-radius) !important;
          padding: 0.85rem 1rem !important;
          margin-bottom: 0.5rem !important;
          color: #f8fafc !important;
        }
        div[data-testid="stRadio"] label:hover {
          border-color: #64748b !important;
          background-color: #2d3d52 !important;
        }
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label div,
        div[data-testid="stRadio"] p,
        div[data-testid="stRadio"] span,
        div[data-testid="stRadio"] [data-baseweb="radio"] label,
        div[data-testid="stRadio"] [data-baseweb="radio"] label p,
        div[data-testid="stRadio"] [data-baseweb="radio"] label span,
        div[data-testid="stRadio"] [role="radiogroup"] label,
        div[data-testid="stRadio"] [role="radiogroup"] label * {
          color: #f8fafc !important;
          -webkit-text-fill-color: #f8fafc !important;
        }
        /* Radio row text in newer Streamlit (markdown-style options) */
        div[data-testid="stRadio"] .stMarkdown,
        div[data-testid="stRadio"] .stMarkdown p,
        div[data-testid="stRadio"] .stMarkdown span {
          color: #f8fafc !important;
          -webkit-text-fill-color: #f8fafc !important;
        }

        div[data-testid="stCheckbox"] {
          background-color: #273548 !important;
          border: 2px solid #475569 !important;
          border-radius: var(--iot-radius);
          padding: 0.65rem 1rem;
          margin-bottom: 0.45rem;
        }
        div[data-testid="stCheckbox"] label,
        div[data-testid="stCheckbox"] label span,
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stCheckbox"] span,
        div[data-testid="stCheckbox"] p {
          color: #f8fafc !important;
          -webkit-text-fill-color: #f8fafc !important;
        }

        /* Text input */
        .stTextInput > div > div > input {
          background-color: var(--iot-card) !important;
          color: var(--iot-text) !important;
          border: 2px solid #334155 !important;
          border-radius: var(--iot-radius) !important;
          padding: 0.85rem 1rem !important;
        }
        .stTextInput > div > div > input:focus {
          border-color: var(--iot-accent) !important;
          box-shadow: 0 0 0 1px var(--iot-accent) !important;
        }

        /* Select boxes (matching) — visible value + label */
        .stSelectbox label,
        .stSelectbox label p,
        .stSelectbox label span {
          color: #e2e8f0 !important;
        }
        .stSelectbox > div > div {
          background-color: #273548 !important;
          border: 2px solid #475569 !important;
          border-radius: 8px !important;
          color: #f8fafc !important;
        }
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] div[aria-selected],
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] li span,
        ul[role="listbox"] li,
        ul[role="listbox"] li span {
          color: #f8fafc !important;
        }
        div[data-baseweb="popover"] {
          background-color: #1e293b !important;
        }

        /* Form submit = primary */
        .stFormSubmitButton > button {
          background-color: var(--iot-accent) !important;
          color: #fff !important;
          border: none !important;
          border-radius: var(--iot-radius) !important;
          font-weight: 600 !important;
          margin-top: 0.5rem;
        }

        /* Feedback panel */
        .feedback-inner {
          border-radius: var(--iot-radius);
          padding: 1.25rem 1.5rem;
          border-left: 4px solid var(--iot-green);
          background: var(--iot-green-bg);
          margin-top: 1rem;
        }
        .feedback-inner.incorrect {
          border-left-color: var(--iot-red);
          background: var(--iot-red-bg);
        }
        .feedback-title {
          font-weight: 700;
          font-size: 1rem;
          margin-bottom: 0.35rem;
        }
        .feedback-title.correct { color: var(--iot-green) !important; }
        .feedback-title.incorrect { color: var(--iot-red) !important; }
        .feedback-text {
          font-size: 0.95rem;
          color: #cbd5e1 !important;
          line-height: 1.55;
        }
        .feedback-text strong {
          color: #f1f5f9 !important;
        }

        /* Form body default text */
        form[data-testid="stForm"] p,
        form[data-testid="stForm"] span,
        form[data-testid="stForm"] label {
          color: #e2e8f0 !important;
        }

        /* Matching descriptions box */
        .matching-descriptions {
          margin-top: 0.75rem;
          padding: 1rem 1.25rem;
          background: rgba(99,102,241,.06);
          border-radius: var(--iot-radius);
          font-size: 0.88rem;
          color: var(--iot-muted);
          line-height: 1.7;
          border: 1px solid #334155;
        }

        /* Score screen */
        .score-section { text-align: center; padding: 1.5rem 0; }
        .score-circle {
          width: 180px;
          height: 180px;
          margin: 0 auto 1.75rem;
          border-radius: 50%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          border: 6px solid var(--iot-accent);
        }
        .score-circle .pct {
          font-size: 2.75rem;
          font-weight: 800;
          line-height: 1;
          color: var(--iot-text);
        }
        .score-circle .label {
          font-size: 0.85rem;
          color: var(--iot-muted);
          margin-top: 0.25rem;
        }
        .stats-row {
          display: flex;
          justify-content: center;
          gap: 2rem;
          margin-bottom: 2rem;
          flex-wrap: wrap;
        }
        .stat { text-align: center; }
        .stat .num { font-size: 1.75rem; font-weight: 700; color: var(--iot-text); }
        .stat .stxt {
          font-size: 0.8rem;
          color: var(--iot-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .stat.green .num { color: var(--iot-green) !important; }
        .stat.red .num { color: var(--iot-red) !important; }

        /* Review items */
        .review-item {
          background: var(--iot-card);
          border-radius: var(--iot-radius);
          padding: 1.5rem;
          margin-bottom: 1rem;
          border-left: 4px solid var(--iot-red);
          text-align: left;
        }
        .review-item .q { font-weight: 600; margin-bottom: 0.5rem; color: var(--iot-text); }
        .review-item .your-ans { color: var(--iot-red); font-size: 0.9rem; margin-bottom: 0.25rem; }
        .review-item .correct-ans { color: var(--iot-green); font-size: 0.9rem; margin-bottom: 0.5rem; }
        .review-item .expl { font-size: 0.85rem; color: var(--iot-muted); line-height: 1.5; }

        .back-muted {
          color: var(--iot-muted) !important;
          font-size: 0.9rem;
        }

        @media (max-width: 540px) {
          .score-circle { width: 140px; height: 140px; }
          .score-circle .pct { font-size: 2.25rem; }
        }

        /* MCQ 2-column tiles: stable height, centered wrapped text */
        section.main div[data-testid="column"] .stButton > button {
          min-height: 100px !important;
          max-height: 140px !important;
          white-space: normal !important;
          overflow-wrap: anywhere !important;
          word-break: break-word !important;
          line-height: 1.35 !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          text-align: center !important;
          padding: 0.85rem 1rem !important;
          box-sizing: border-box !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def html_progress_row(idx, total):
    pct = round((idx / total) * 100) if total else 0
    width = (idx / total) * 100 if total else 0
    return f"""
    <div class="progress-wrap">
      <div class="progress-info">
        <span>Question {idx + 1} / {total}</span>
        <span>{pct}%</span>
      </div>
      <div class="progress-bar-iot"><div class="progress-fill-iot" style="width:{width}%"></div></div>
    </div>
    """


def html_question_block(badge_label, question_text, hint_html=""):
    return f"""
    <div class="question-card">
      <span class="q-type-badge">{esc(badge_label)}</span>
      <div class="question-text">{esc(question_text)}</div>
      {hint_html}
    </div>
    """


def badge_for_type(qtype):
    return {
        "mcq": "Multiple Choice",
        "multi-select": "Multi-Select",
        "text-input": "Text Input",
        "matching": "Matching",
    }.get(qtype, qtype)


def mcq_session_key(idx, qid):
    return f"mcq_sel_{idx}_{qid}"


def finalize_answer(q, mcq_pick, multi_pick, text_val, match_picks):
    if q["type"] == "mcq":
        ok = check_answer(q, mcq_pick, None, None, {})
    elif q["type"] == "multi-select":
        ok = check_answer(q, None, multi_pick, None, {})
    elif q["type"] == "text-input":
        ok = check_answer(q, None, None, text_val, {})
    else:
        ok = check_answer(q, None, None, None, match_picks)

    st.session_state.last_correct = ok
    st.session_state.show_answer = True
    if ok:
        st.session_state.score += 1
    else:
        ya, ca = mistake_record(q, mcq_pick, multi_pick, text_val, match_picks)
        st.session_state.mistakes.append(
            {
                "question": q["question"],
                "your": ya,
                "correct": ca,
                "explanation": q.get("explanation") or "",
            }
        )
    st.rerun()


def main():
    st.set_page_config(
        page_title="IoT Quiz Master",
        page_icon="📡",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_flask_like_css()
    init_session()

    questions = load_questions()

    if st.session_state.page == "home":
        st.markdown(
            """
            <div class="iot-hero">
              <h1><span class="iot-accent">IoT</span> Quiz Master</h1>
              <p>Test your knowledge across 11 Internet-of-Things topics. Practice by topic or take the full mock quiz.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📚 Practice by Topic", use_container_width=True, type="primary"):
                st.session_state.page = "topics"
                st.rerun()
        with c2:
            if st.button("🧪 Mock Quiz (All Topics)", use_container_width=True):
                start_quiz(questions)
                st.rerun()

    elif st.session_state.page == "topics":
        st.markdown(
            """
            <style>
            section.main div[data-testid="column"] .stButton > button {
              width: 100% !important;
              min-height: 88px !important;
              background-color: #1e293b !important;
              color: #e2e8f0 !important;
              border: 2px solid transparent !important;
              white-space: pre-line !important;
              line-height: 1.35 !important;
              text-align: center !important;
            }
            section.main div[data-testid="column"] .stButton > button:hover {
              border-color: #6366f1 !important;
              box-shadow: 0 8px 24px rgba(0,0,0,.25);
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        if st.button("← Back to Home"):
            go_home()
            st.rerun()
        st.markdown(
            '<h2 style="text-align:center;margin-bottom:1.25rem;">Choose a Topic</h2>',
            unsafe_allow_html=True,
        )
        topics = topic_counts(questions)
        cols_n = 3
        for row in range(0, len(topics), cols_n):
            cols = st.columns(cols_n)
            for j in range(cols_n):
                idx = row + j
                if idx >= len(topics):
                    break
                name, count = topics[idx]
                with cols[j]:
                    if st.button(
                        f"{name}\n{count} questions",
                        key=f"topic_pick_{idx}",
                        use_container_width=True,
                    ):
                        start_quiz(questions, topic=name)
                        st.rerun()

    elif st.session_state.page == "quiz":
        qs = st.session_state.quiz_questions
        idx = st.session_state.q_idx
        total = len(qs)

        if total == 0:
            st.warning("No questions in this set.")
            if st.button("Home"):
                go_home()
                st.rerun()
            return

        if idx >= total:
            st.session_state.page = "score"
            st.rerun()

        q = qs[idx]

        col_exit, _ = st.columns([1, 5])
        with col_exit:
            if st.button("← Exit Quiz"):
                go_home()
                st.rerun()

        st.markdown(html_progress_row(idx, total), unsafe_allow_html=True)

        hint = ""
        if q["type"] == "multi-select":
            hint = '<p class="hint-iot">(Select all that apply)</p>'
        elif q["type"] == "matching":
            hint = '<p class="hint-iot">(Match each item with the correct option)</p>'

        st.markdown(
            html_question_block(badge_for_type(q["type"]), q["question"], hint),
            unsafe_allow_html=True,
        )
        st.caption(q.get("topic", ""))

        if not st.session_state.show_answer:
            # MCQ: 2-column tile grid, no default selection (st.radio always pre-selects).
            # Regular st.button cannot be used inside st.form.
            if q["type"] == "mcq":
                sk = mcq_session_key(idx, q["id"])
                opts = q["options"]
                sel_i = st.session_state.get(sk)

                st.caption("Tap an option to select it, then press Submit Answer.")
                cols_per_row = 2
                for row_start in range(0, len(opts), cols_per_row):
                    col_pair = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        opt_i = row_start + j
                        with col_pair[j]:
                            if opt_i < len(opts):
                                label = opts[opt_i]
                                chosen = sel_i is not None and sel_i == opt_i
                                if st.button(
                                    label,
                                    key=f"mcqb_{idx}_{q['id']}_{opt_i}",
                                    use_container_width=True,
                                    type="primary" if chosen else "secondary",
                                ):
                                    st.session_state[sk] = opt_i
                                    st.rerun()
                            else:
                                st.empty()

                if st.button("Submit Answer", type="primary", key=f"mcq_submit_{idx}_{q['id']}"):
                    if st.session_state.get(sk) is None:
                        st.warning("Select an option before submitting.")
                    else:
                        finalize_answer(q, opts[st.session_state[sk]], None, None, {})

            else:
                with st.form(key=f"quiz_form_{idx}_{q['id']}"):
                    multi_pick = text_val = None
                    match_picks = {}

                    if q["type"] == "multi-select":
                        multi_pick = []
                        for i, opt in enumerate(q["options"]):
                            if st.checkbox(opt, key=f"ms_{idx}_{i}"):
                                multi_pick.append(i)
                    elif q["type"] == "text-input":
                        text_val = st.text_input(
                            "Your answer",
                            placeholder="Type your answer…",
                            label_visibility="collapsed",
                            key=f"tx_{idx}",
                        )
                    elif q["type"] == "matching":
                        if q.get("descriptions"):
                            desc_html = "<div class='matching-descriptions'>" + "<br>".join(
                                esc(d) for d in q["descriptions"]
                            ) + "</div>"
                            st.markdown(desc_html, unsafe_allow_html=True)
                        for mi, item in enumerate(q.get("items", [])):
                            opts = q.get("options", [])
                            val = st.selectbox(item, ["—"] + opts, key=f"mt_{idx}_{mi}")
                            if val != "—":
                                match_picks[item] = val

                    submitted = st.form_submit_button("Submit Answer")

                if submitted:
                    if q["type"] == "multi-select" and not multi_pick:
                        st.warning("Select at least one option.")
                        st.stop()
                    if q["type"] == "text-input" and not (text_val or "").strip():
                        st.warning("Enter an answer.")
                        st.stop()
                    if q["type"] == "matching" and len(match_picks) != len(q.get("items", [])):
                        st.warning("Match every item before submitting.")
                        st.stop()
                    finalize_answer(q, None, multi_pick, text_val, match_picks)
        else:
            ans = q.get("answer")
            correct_line = ""
            if not st.session_state.last_correct:
                if isinstance(ans, dict):
                    parts = [f"{k} → {v}" for k, v in sorted(ans.items())]
                    correct_line = "<strong>Correct answer:</strong> " + "; ".join(esc(p) for p in parts)
                elif isinstance(ans, list):
                    correct_line = "<strong>Correct answer:</strong> " + esc(", ".join(ans))
                else:
                    correct_line = "<strong>Correct answer:</strong> " + esc(ans)

            fb_cls = "" if st.session_state.last_correct else " incorrect"
            title = "✓ Correct!" if st.session_state.last_correct else "✗ Incorrect"
            title_cls = "correct" if st.session_state.last_correct else "incorrect"
            expl = esc(q.get("explanation") or "")
            body_bits = [b for b in (correct_line, expl) if b]
            inner = "<br><br>".join(body_bits) if body_bits else ""
            expl_html = f'<div class="feedback-text">{inner}</div>' if inner else ""

            st.markdown(
                f"""
                <div class="feedback-inner{fb_cls}">
                  <div class="feedback-title {title_cls}">{esc(title)}</div>
                  {expl_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Next Question →", type="primary"):
                st.session_state.q_idx += 1
                st.session_state.show_answer = False
                st.rerun()

    elif st.session_state.page == "score":
        total = len(st.session_state.quiz_questions)
        sc = st.session_state.score
        pct = round(100 * sc / total) if total else 0
        wrong = total - sc

        border_color = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
        st.markdown(
            f"""
            <div class="score-section">
              <h2 style="margin-bottom:1.5rem;">Quiz Complete!</h2>
              <div class="score-circle" style="border-color:{border_color};">
                <span class="pct">{pct}%</span>
                <span class="label">Score</span>
              </div>
              <div class="stats-row">
                <div class="stat green"><div class="num">{sc}</div><div class="stxt">Correct</div></div>
                <div class="stat red"><div class="num">{wrong}</div><div class="stxt">Incorrect</div></div>
                <div class="stat"><div class="num">{total}</div><div class="stxt">Total</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns(2)
        with b1:
            if st.session_state.mistakes:
                if st.button(
                    "📝 Review Mistakes" if not st.session_state.review_open else "🔼 Hide Review",
                    use_container_width=True,
                ):
                    st.session_state.review_open = not st.session_state.review_open
                    st.rerun()
        with b2:
            if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
                go_home()
                st.rerun()

        if st.session_state.mistakes and st.session_state.review_open:
            st.markdown('<h3 style="text-align:center;margin:1.25rem 0 1rem;">Incorrect Answers</h3>', unsafe_allow_html=True)
            for m in st.session_state.mistakes:
                qshort = m["question"][:280] + ("…" if len(m["question"]) > 280 else "")
                st.markdown(
                    f"""
                    <div class="review-item">
                      <div class="q">{esc(qshort)}</div>
                      <div class="your-ans">Your answer: {esc(m['your'])}</div>
                      <div class="correct-ans">Correct answer: {esc(str(m['correct']))}</div>
                      <div class="expl">{esc(m.get('explanation') or '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
