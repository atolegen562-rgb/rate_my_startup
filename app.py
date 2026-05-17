import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import sqlite3
import json
import os

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()

# -----------------------------
# OPENAI CLIENT
# -----------------------------
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------
# DATABASE SETUP
# -----------------------------
conn = sqlite3.connect(
    "startup_ai.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea TEXT,
    overall_score REAL,
    investor_score INTEGER,
    yc_score INTEGER
)
""")

conn.commit()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Startup AI",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.title("Startup AI")

    st.caption(
        "AI-powered startup evaluation platform"
    )

    st.divider()

    # DATABASE STATS
    cursor.execute(
        "SELECT COUNT(*) FROM analyses"
    )

    total_analyses = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(overall_score) FROM analyses"
    )

    avg_score = cursor.fetchone()[0]

    st.metric(
        "Analyses",
        total_analyses
    )

    st.metric(
        "Average Score",
        f"{avg_score:.1f}/10"
        if avg_score else "0"
    )

    st.divider()

    st.write("### Recent Analyses")

    cursor.execute("""
    SELECT idea
    FROM analyses
    ORDER BY id DESC
    LIMIT 5
    """)

    recent_ideas = cursor.fetchall()

    if recent_ideas:

        for item in recent_ideas:

            st.write(f"• {item[0][:40]}")

    else:

        st.caption("No analyses yet")

    st.divider()

    st.caption(
        "Built with Streamlit + OpenAI + SQLite"
    )

# -----------------------------
# MAIN PAGE
# -----------------------------
st.title("🚀 Startup AI")

st.write(
    "Analyze startup ideas with AI-powered "
    "market, investor, and YC evaluation."
)

# -----------------------------
# USER INPUT
# -----------------------------
idea = st.text_area(
    "Describe your startup idea",
    placeholder=(
        "Example: AI platform that helps "
        "international students find scholarships"
    ),
    height=220
)

# -----------------------------
# ANALYZE BUTTON
# -----------------------------
if st.button("Analyze Startup"):

    if idea.strip() == "":

        st.warning(
            "Please enter a startup idea."
        )

    else:

        with st.spinner(
            "Analyzing startup..."
        ):

            try:

                # -----------------------------
                # OPENAI REQUEST
                # -----------------------------
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """
You are a top-tier startup investor,
YC partner, and venture capitalist.

Analyze startup ideas professionally.

Return ONLY valid JSON.

No markdown.
"""
                        },
                        {
                            "role": "user",
                            "content": f"""
Analyze this startup:

{idea}

Return JSON exactly like this:

{{
    "market_score": 0,
    "virality_score": 0,
    "monetization_score": 0,
    "competition_score": 0,
    "investor_interest": 0,
    "yc_probability": 0,
    "summary": "",
    "strengths": [],
    "risks": [],
    "competitors": [],
    "pitch": ""
}}
"""
                        }
                    ]
                )

                # -----------------------------
                # PARSE AI JSON
                # -----------------------------
                data = json.loads(
                    response.choices[0]
                    .message.content
                )

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )

                st.stop()

        # -----------------------------
        # SCORES
        # -----------------------------
        market_score = data["market_score"]

        virality_score = data["virality_score"]

        monetization_score = (
            data["monetization_score"]
        )

        competition_score = (
            data["competition_score"]
        )

        investor_score = (
            data["investor_interest"]
        )

        yc_score = (
            data["yc_probability"]
        )

        summary = data["summary"]

        strengths = data["strengths"]

        risks = data["risks"]

        competitors = data["competitors"]

        pitch = data["pitch"]

        # -----------------------------
        # OVERALL SCORE
        # -----------------------------
        overall_score = (
            market_score +
            virality_score +
            monetization_score +
            competition_score
        ) / 4

        # -----------------------------
        # SAVE TO DATABASE
        # -----------------------------
        cursor.execute(
            """
            INSERT INTO analyses (
                idea,
                overall_score,
                investor_score,
                yc_score
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                idea,
                overall_score,
                investor_score,
                yc_score
            )
        )

        conn.commit()

        # -----------------------------
        # DIVIDER
        # -----------------------------
        st.divider()

        # -----------------------------
        # METRICS
        # -----------------------------
        st.subheader(
            "Startup Analysis"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        with col1:

            st.metric(
                "Market",
                f"{market_score}/10"
            )

        with col2:

            st.metric(
                "Virality",
                f"{virality_score}/10"
            )

        with col3:

            st.metric(
                "Monetization",
                f"{monetization_score}/10"
            )

        with col4:

            st.metric(
                "Competition",
                f"{competition_score}/10"
            )

        # -----------------------------
        # OVERALL SCORE
        # -----------------------------
        st.write(
            "## Overall Startup Score"
        )

        st.progress(
            overall_score / 10
        )

        st.metric(
            "Overall Score",
            f"{overall_score:.1f}/10"
        )

        # -----------------------------
        # AI SUMMARY
        # -----------------------------
        st.write(
            "## AI Summary"
        )

        st.write(summary)

        # -----------------------------
        # CHART
        # -----------------------------
        st.write(
            "## Analytics Dashboard"
        )

        chart_data = pd.DataFrame({
            "Category": [
                "Market",
                "Virality",
                "Monetization",
                "Competition"
            ],
            "Score": [
                market_score,
                virality_score,
                monetization_score,
                competition_score
            ]
        })

        st.bar_chart(
            chart_data,
            x="Category",
            y="Score"
        )

        # -----------------------------
        # INVESTOR INTEREST
        # -----------------------------
        st.write(
            "## Investor Interest"
        )

        st.progress(
            investor_score / 100
        )

        st.metric(
            "Investor Interest",
            f"{investor_score}%"
        )

        # -----------------------------
        # YC PROBABILITY
        # -----------------------------
        st.write(
            "## Y Combinator Probability"
        )

        st.progress(
            yc_score / 100
        )

        st.metric(
            "YC Probability",
            f"{yc_score}%"
        )

        # -----------------------------
        # STRENGTHS
        # -----------------------------
        st.write(
            "## Key Strengths"
        )

        for strength in strengths:

            st.write(
                f"• {strength}"
            )

        # -----------------------------
        # RISKS
        # -----------------------------
        st.write(
            "## Key Risks"
        )

        for risk in risks:

            st.write(
                f"• {risk}"
            )

        # -----------------------------
        # COMPETITORS
        # -----------------------------
        st.write(
            "## Competitor Landscape"
        )

        for company in competitors:

            st.write(
                f"• {company}"
            )

        # -----------------------------
        # PITCH
        # -----------------------------
        st.write(
            "## Elevator Pitch"
        )

        st.write(pitch)

        # -----------------------------
        # DOWNLOAD REPORT
        # -----------------------------
        st.write(
            "## Download Startup Report"
        )

        report = f"""
STARTUP REPORT

IDEA:
{idea}

OVERALL SCORE:
{overall_score:.1f}/10

MARKET:
{market_score}/10

VIRALITY:
{virality_score}/10

MONETIZATION:
{monetization_score}/10

COMPETITION:
{competition_score}/10

INVESTOR INTEREST:
{investor_score}%

YC PROBABILITY:
{yc_score}%

SUMMARY:
{summary}

STRENGTHS:
{strengths}

RISKS:
{risks}

COMPETITORS:
{competitors}

PITCH:
{pitch}
"""

        st.download_button(
            label="Download Report",
            data=report,
            file_name="startup_report.txt",
            mime="text/plain"
        )