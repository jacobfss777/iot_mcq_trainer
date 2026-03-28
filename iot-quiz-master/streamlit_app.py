"""
IoT Quiz Master — Streamlit version (deploy on Streamlit Community Cloud).
Run locally: streamlit run streamlit_app.py
"""
import json
import os
import random

import streamlit as st

BASE = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE, "questions.json")


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


def start_quiz(questions, topic=None):
    pool = [q for q in questions if topic is None or q.get("topic") == topic]
    random.shuffle(pool)
    st.session_state.quiz_questions = pool
    st.session_state.q_idx = 0
    st.session_state.score = 0
    st.session_state.mistakes = []
    st.session_state.show_answer = False
    st.session_state.page = "quiz"


def dark_css():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0f172a; }
        [data-testid="stHeader"] { background-color: #0f172a; }
        .block-container { padding-top: 2rem; max-width: 720px; }
        h1 { color: #e2e8f0 !important; }
        h2, h3, p, label, span { color: #e2e8f0 !important; }
        .stMarkdown { color: #e2e8f0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="IoT Quiz Master",
        page_icon="📡",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    dark_css()
    init_session()

    questions = load_questions()

    if st.session_state.page == "home":
        st.title("IoT Quiz Master")
        st.caption("Practice by topic or take the full mock quiz.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Practice by topic", use_container_width=True):
                st.session_state.page = "topics"
                st.rerun()
        with c2:
            if st.button("Mock quiz (all topics)", use_container_width=True):
                start_quiz(questions)
                st.rerun()

    elif st.session_state.page == "topics":
        if st.button("← Back"):
            go_home()
            st.rerun()
        st.subheader("Choose a topic")
        topics = topic_counts(questions)
        labels = [f"{name} ({count} questions)" for name, count in topics]
        choice = st.selectbox("Topic", range(len(topics)), format_func=lambda i: labels[i])
        if st.button("Start", type="primary"):
            start_quiz(questions, topic=topics[choice][0])
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
        st.progress(idx / total)
        st.caption(f"Question {idx + 1} of {total} · {q.get('topic', '')}")

        badge = {
            "mcq": "Multiple choice",
            "multi-select": "Multi-select",
            "text-input": "Text answer",
            "matching": "Matching",
        }.get(q["type"], q["type"])
        st.caption(badge)

        if not st.session_state.show_answer:
            st.markdown(q["question"])
            if q["type"] == "multi-select":
                st.caption("Select all that apply.")

            with st.form(key=f"quiz_form_{idx}_{q['id']}"):
                mcq_pick = multi_pick = text_val = None
                match_picks = {}

                if q["type"] == "mcq":
                    mcq_pick = st.radio("Choose one:", q["options"], key=f"mcq_{idx}")
                elif q["type"] == "multi-select":
                    multi_pick = []
                    for i, opt in enumerate(q["options"]):
                        if st.checkbox(opt, key=f"ms_{idx}_{i}"):
                            multi_pick.append(i)
                elif q["type"] == "text-input":
                    text_val = st.text_input("Your answer", key=f"tx_{idx}")
                elif q["type"] == "matching":
                    st.caption("Match each item to the correct option.")
                    if q.get("descriptions"):
                        st.info("\n".join(q["descriptions"]))
                    for mi, item in enumerate(q.get("items", [])):
                        opts = q.get("options", [])
                        val = st.selectbox(
                            item,
                            ["—"] + opts,
                            key=f"mt_{idx}_{mi}",
                        )
                        if val != "—":
                            match_picks[item] = val

                submitted = st.form_submit_button("Submit answer")

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
        else:
            st.markdown(q["question"])
            if st.session_state.last_correct:
                st.success("Correct!")
            else:
                st.error("Incorrect")
                ans = q.get("answer")
                if isinstance(ans, dict):
                    st.write("**Correct matches:**")
                    for k, v in sorted(ans.items()):
                        st.write(f"- {k} → {v}")
                elif isinstance(ans, list):
                    st.write(f"**Correct:** {', '.join(ans)}")
                else:
                    st.write(f"**Correct answer:** {ans}")
            if q.get("explanation"):
                st.info(q["explanation"])

            if st.button("Next"):
                st.session_state.q_idx += 1
                st.session_state.show_answer = False
                st.rerun()

    elif st.session_state.page == "score":
        total = len(st.session_state.quiz_questions)
        sc = st.session_state.score
        pct = round(100 * sc / total) if total else 0
        st.title("Quiz complete")
        st.metric("Score", f"{pct}%", f"{sc} / {total} correct")
        st.write(f"Incorrect: {total - sc}")

        if st.session_state.mistakes:
            with st.expander("Review mistakes"):
                for m in st.session_state.mistakes:
                    st.markdown(f"**{m['question'][:200]}{'…' if len(m['question']) > 200 else ''}**")
                    st.caption(f"Your answer: {m['your']}")
                    st.caption(f"Correct: {m['correct']}")
                    if m.get("explanation"):
                        st.text(m["explanation"])
                    st.divider()

        if st.button("Back to home"):
            go_home()
            st.rerun()


if __name__ == "__main__":
    main()
