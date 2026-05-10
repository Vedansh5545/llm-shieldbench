from __future__ import annotations

import base64
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from src.categories import CATEGORIES, CATEGORY_DESCRIPTIONS
from src.evaluator import run_single_evaluation
from src.report_generator import generate_markdown_report


APP_TITLE = "LLM ShieldBench"
PALETTE = {
    "background": "#0B0F14",
    "surface": "#16202A",
    "text": "#F5F1E8",
    "primary": "#36F2B2",
    "secondary": "#22D3EE",
    "human": "#F4B860",
}


def image_to_base64(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        return ""
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")


def apply_brand_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at 20% 10%, rgba(54, 242, 178, 0.12), transparent 28%),
                        radial-gradient(circle at 80% 15%, rgba(34, 211, 238, 0.13), transparent 24%),
                        {PALETTE["background"]};
            color: {PALETTE["text"]};
        }}

        [data-testid="stHeader"] {{
            background: rgba(11, 15, 20, 0.0);
        }}

        [data-testid="stSidebar"] {{
            background: {PALETTE["surface"]};
            border-right: 1px solid rgba(54, 242, 178, 0.20);
        }}

        .main-card {{
            padding: 2rem;
            border-radius: 28px;
            background: linear-gradient(145deg, rgba(22, 32, 42, 0.96), rgba(11, 15, 20, 0.96));
            border: 1px solid rgba(54, 242, 178, 0.23);
            box-shadow: 0 0 42px rgba(54, 242, 178, 0.09);
        }}

        .brand-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            color: {PALETTE["primary"]};
            background: rgba(54, 242, 178, 0.08);
            border: 1px solid rgba(54, 242, 178, 0.28);
            font-size: 0.85rem;
            letter-spacing: 0.02em;
            margin-bottom: 1rem;
        }}

        .hero-title {{
            font-size: 3.2rem;
            line-height: 1.04;
            font-weight: 800;
            color: {PALETTE["text"]};
            margin: 0;
        }}

        .hero-subtitle {{
            font-size: 1.2rem;
            line-height: 1.65;
            color: rgba(245, 241, 232, 0.78);
            max-width: 820px;
            margin-top: 1rem;
        }}

        .metric-card {{
            padding: 1.25rem;
            border-radius: 22px;
            background: rgba(22, 32, 42, 0.86);
            border: 1px solid rgba(34, 211, 238, 0.20);
            min-height: 132px;
        }}

        .metric-label {{
            color: rgba(245, 241, 232, 0.68);
            font-size: 0.88rem;
            margin-bottom: 0.3rem;
        }}

        .metric-value {{
            color: {PALETTE["primary"]};
            font-size: 2rem;
            font-weight: 800;
        }}

        .risk-low {{ color: {PALETTE["primary"]}; font-weight: 800; }}
        .risk-medium {{ color: {PALETTE["human"]}; font-weight: 800; }}
        .risk-high {{ color: #ff7b7b; font-weight: 800; }}

        .section-title {{
            color: {PALETTE["text"]};
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            font-size: 1.4rem;
            font-weight: 750;
        }}

        .footer-note {{
            color: rgba(245, 241, 232, 0.55);
            font-size: 0.9rem;
            margin-top: 2rem;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, {PALETTE["primary"]}, {PALETTE["secondary"]});
            color: {PALETTE["background"]};
            font-weight: 800;
            border: none;
            border-radius: 999px;
            padding: 0.75rem 1.25rem;
            box-shadow: 0 0 24px rgba(54, 242, 178, 0.18);
        }}

        .stDownloadButton>button {{
            background: transparent;
            color: {PALETTE["primary"]};
            font-weight: 700;
            border: 1px solid rgba(54, 242, 178, 0.50);
            border-radius: 999px;
            padding: 0.75rem 1.25rem;
        }}

        textarea, input, .stSelectbox div[data-baseweb="select"] {{
            border-radius: 16px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    logo_b64 = image_to_base64("assets/vedansh-labs-logo-jukebox-bg-removed.png")

    if logo_b64:
        logo_html = f"""
        <div class="logo-stage">
            <div class="logo-orbit orbit-one"></div>
            <div class="logo-orbit orbit-two"></div>

            <div class="logo-tile">
                <div class="logo-glow"></div>
                <img src="data:image/png;base64,{logo_b64}" class="hero-logo" />
            </div>
        </div>
        """
    else:
        logo_html = ""

    hero_html = f"""
    <html>
    <head>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: Inter, Segoe UI, Arial, sans-serif;
            }}

            .hero-card {{
                width: 100%;
                min-height: 290px;
                padding: 38px 42px;
                border-radius: 32px;
                background:
                    radial-gradient(circle at 12% 18%, rgba(54,242,178,0.15), transparent 34%),
                    radial-gradient(circle at 88% 18%, rgba(34,211,238,0.12), transparent 34%),
                    linear-gradient(145deg, rgba(22,32,42,0.97), rgba(11,15,20,0.97));
                border: 1px solid rgba(54,242,178,0.24);
                box-shadow:
                    0 0 46px rgba(54,242,178,0.08),
                    inset 0 0 42px rgba(34,211,238,0.025);
                overflow: hidden;
                position: relative;
            }}

            .hero-card::before {{
                content: "";
                position: absolute;
                inset: 0;
                background:
                    linear-gradient(120deg, transparent 0%, rgba(54,242,178,0.055) 45%, transparent 62%);
                transform: translateX(-100%);
                animation: sweep 7s ease-in-out infinite;
                pointer-events: none;
            }}

            .hero-layout {{
                position: relative;
                z-index: 2;
                display: flex;
                align-items: center;
                gap: 30px;
            }}

            .logo-stage {{
                position: relative;
                width: 136px;
                height: 136px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }}

            .logo-tile {{
                position: relative;
                width: 118px;
                height: 118px;
                border-radius: 30px;
                background:
                    radial-gradient(circle at 32% 22%, rgba(54,242,178,0.18), transparent 42%),
                    radial-gradient(circle at 78% 80%, rgba(34,211,238,0.18), transparent 46%),
                    linear-gradient(145deg, rgba(22,32,42,0.98), rgba(11,15,20,0.98));
                border: 1px solid rgba(54,242,178,0.38);
                box-shadow:
                    0 0 28px rgba(54,242,178,0.18),
                    0 0 58px rgba(34,211,238,0.08),
                    inset 0 0 26px rgba(34,211,238,0.06);
                display: flex;
                align-items: center;
                justify-content: center;
                animation: floatLogo 4.8s ease-in-out infinite;
                overflow: hidden;
            }}

            .logo-tile::after {{
                content: "";
                position: absolute;
                width: 160%;
                height: 160%;
                background: conic-gradient(
                    from 180deg,
                    transparent,
                    rgba(54,242,178,0.18),
                    rgba(34,211,238,0.22),
                    transparent
                );
                animation: rotateGlow 8s linear infinite;
                opacity: 0.55;
            }}

            .logo-glow {{
                position: absolute;
                inset: 12px;
                border-radius: 24px;
                background: radial-gradient(circle, rgba(54,242,178,0.18), transparent 68%);
                filter: blur(8px);
                animation: pulseGlow 3.2s ease-in-out infinite;
                z-index: 1;
            }}

            .hero-logo {{
                position: relative;
                z-index: 3;
                width: 92px;
                height: 92px;
                object-fit: contain;
                filter:
                    drop-shadow(0 0 10px rgba(54,242,178,0.40))
                    drop-shadow(0 0 18px rgba(34,211,238,0.18));
            }}

            .logo-orbit {{
                position: absolute;
                border-radius: 999px;
                border: 1px solid rgba(54,242,178,0.24);
                opacity: 0.65;
                pointer-events: none;
            }}

            .orbit-one {{
                width: 132px;
                height: 132px;
                animation: orbitPulse 4.2s ease-in-out infinite;
            }}

            .orbit-two {{
                width: 112px;
                height: 112px;
                border-color: rgba(34,211,238,0.20);
                animation: orbitPulse 4.2s ease-in-out infinite reverse;
            }}

            .content {{
                flex: 1;
                min-width: 0;
            }}

            .brand-pill {{
                display: inline-flex;
                align-items: center;
                padding: 7px 14px;
                border-radius: 999px;
                color: #36F2B2;
                background: rgba(54,242,178,0.08);
                border: 1px solid rgba(54,242,178,0.32);
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0.02em;
                margin-bottom: 13px;
                box-shadow: 0 0 18px rgba(54,242,178,0.08);
            }}

            h1 {{
                font-size: 56px;
                line-height: 1.02;
                font-weight: 900;
                color: #F5F1E8;
                margin: 0;
                letter-spacing: -0.045em;
                text-shadow: 0 0 26px rgba(245,241,232,0.08);
            }}

            .subtitle {{
                font-size: 18px;
                line-height: 1.65;
                color: rgba(245,241,232,0.78);
                max-width: 900px;
                margin-top: 16px;
                margin-bottom: 0;
            }}

            .tagline {{
                color: #F4B860;
                font-size: 16px;
                font-weight: 800;
                margin-top: 16px;
                margin-bottom: 0;
            }}

            @keyframes floatLogo {{
                0%, 100% {{
                    transform: translateY(0px) scale(1);
                }}
                50% {{
                    transform: translateY(-6px) scale(1.025);
                }}
            }}

            @keyframes pulseGlow {{
                0%, 100% {{
                    opacity: 0.50;
                    transform: scale(0.96);
                }}
                50% {{
                    opacity: 1;
                    transform: scale(1.08);
                }}
            }}

            @keyframes rotateGlow {{
                from {{
                    transform: rotate(0deg);
                }}
                to {{
                    transform: rotate(360deg);
                }}
            }}

            @keyframes orbitPulse {{
                0%, 100% {{
                    transform: scale(0.96);
                    opacity: 0.28;
                }}
                50% {{
                    transform: scale(1.06);
                    opacity: 0.72;
                }}
            }}

            @keyframes sweep {{
                0% {{
                    transform: translateX(-120%);
                }}
                45%, 100% {{
                    transform: translateX(120%);
                }}
            }}

            @media (max-width: 760px) {{
                .hero-card {{
                    padding: 30px 24px;
                }}

                .hero-layout {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 22px;
                }}

                h1 {{
                    font-size: 42px;
                }}

                .subtitle {{
                    font-size: 16px;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="hero-card">
            <div class="hero-layout">
                {logo_html}

                <div class="content">
                    <div class="brand-pill">
                        Vedansh Labs · Trustworthy Intelligence
                    </div>

                    <h1>LLM ShieldBench</h1>

                    <p class="subtitle">
                        Evaluate AI assistants before real users depend on them.
                        Test chatbot safety, reliability, hallucination behavior,
                        privacy risk, and instruction-following quality.
                    </p>

                    <p class="tagline">
                        Building human-centered AI from research to reality.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(hero_html, height=315, scrolling=False)
    
def render_score_gauge(score: int) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100", "font": {"color": PALETTE["text"], "size": 36}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": PALETTE["text"]},
                "bar": {"color": PALETTE["primary"]},
                "bgcolor": PALETTE["surface"],
                "borderwidth": 1,
                "bordercolor": PALETTE["secondary"],
                "steps": [
                    {"range": [0, 65], "color": "rgba(244, 184, 96, 0.25)"},
                    {"range": [65, 85], "color": "rgba(34, 211, 238, 0.20)"},
                    {"range": [85, 100], "color": "rgba(54, 242, 178, 0.22)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": PALETTE["text"]},
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title="LLM ShieldBench",
        page_icon="🛡️",
        layout="wide",
    )

    apply_brand_styles()

    with st.sidebar:
        st.markdown("## LLM ShieldBench")
        st.caption("Vedansh Labs · Trustworthy Intelligence")
        st.markdown("---")
        st.markdown("### Test Categories")
        for category in CATEGORIES:
            st.markdown(f"**{category}**")
            st.caption(CATEGORY_DESCRIPTIONS[category])
        st.markdown("---")
        st.caption("v0.1.1 Research Preview")

    render_hero()

    st.markdown('<div class="section-title">Run a new evaluation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([0.9, 1.1], gap="large")

    with col1:
        category = st.selectbox("Evaluation category", CATEGORIES)
        prompt = st.text_area(
            "Original prompt",
            height=130,
            placeholder="Paste the user prompt given to the chatbot...",
        )
        response = st.text_area(
            "Chatbot response",
            height=180,
            placeholder="Paste the chatbot response you want to evaluate...",
        )
        expected_behavior = st.text_area(
            "Expected safe behavior",
            height=110,
            placeholder="Optional: describe what a safe and reliable response should do...",
        )

        run_button = st.button("Run ShieldBench Evaluation", use_container_width=True)

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Selected Category</div>
                <div style="font-size:1.35rem; font-weight:800; color:{PALETTE["secondary"]};">{category}</div>
                <p style="color:rgba(245,241,232,0.68); margin-top:0.8rem;">
                    {CATEGORY_DESCRIPTIONS[category]}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.info(
        "MVP note: This version uses a transparent rule-based evaluator. It scores the chatbot response, not the risky wording inside the user prompt."
    )

    if run_button:
        if not prompt.strip() or not response.strip():
            st.warning("Please add both the original prompt and the chatbot response before running the evaluation.")
            return

        result = run_single_evaluation(category, prompt, response, expected_behavior)

        st.markdown('<div class="section-title">Evaluation result</div>', unsafe_allow_html=True)

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        risk_class = {
            "Low": "risk-low",
            "Medium": "risk-medium",
            "High": "risk-high",
        }.get(result["risk_level"], "risk-medium")

        with metric_col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Trust Score</div>
                    <div class="metric-value">{result["score"]} / 100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with metric_col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Risk Level</div>
                    <div class="{risk_class}" style="font-size:2rem;">{result["risk_level"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with metric_col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Category</div>
                    <div style="font-size:1.35rem; font-weight:800; color:{PALETTE["secondary"]};">{result["category"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        render_score_gauge(result["score"])

        result_col1, result_col2 = st.columns(2, gap="large")

        with result_col1:
            st.markdown("### Strengths")
            for item in result["strengths"]:
                st.success(item)

        with result_col2:
            st.markdown("### Issues")
            for item in result["issues"]:
                st.warning(item)

        st.markdown("### Recommendation")
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="color:{PALETTE["text"]}; font-size:1.05rem; line-height:1.65;">
                    {result["recommendation"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        report = generate_markdown_report(result)
        st.download_button(
            "Download Markdown Report",
            data=report,
            file_name="llm-shieldbench-report.md",
            mime="text/markdown",
            use_container_width=True,
        )

        with st.expander("Preview report"):
            st.markdown(report)

    st.markdown(
        '<p class="footer-note">Built by Vedansh Labs · Building human-centered AI from research to reality.</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()