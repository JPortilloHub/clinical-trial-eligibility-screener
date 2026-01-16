import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Eligibility Screener",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Custom CSS for professional clinical styling
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container - remove top padding */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Header styling - aligned to top */
    .main-header {
        background: linear-gradient(135deg, #0f4c81 0%, #1a6eb0 50%, #2d8bc9 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 16px 16px;
        margin-bottom: 0.75rem;
        margin-top: -1rem;
        color: white;
        box-shadow: 0 8px 32px rgba(15, 76, 129, 0.3);
    }

    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
        font-weight: 400;
    }

    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .metric-card.total { border-left-color: #0f4c81; }
    .metric-card.eligible { border-left-color: #67e8f9; }
    .metric-card.not-eligible { border-left-color: #a5b4fc; }
    .metric-card.review { border-left-color: #86efac; }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 28px;
        font-size: 0.95rem;
        font-weight: 600;
        border-radius: 8px;
        color: #475569;
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #0f4c81 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #0f4c81;
        background-color: rgba(255,255,255,0.5);
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 30px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .status-eligible {
        background: linear-gradient(135deg, #67e8f9 0%, #a5f3fc 100%);
        color: #155e75;
        box-shadow: 0 4px 15px rgba(103, 232, 249, 0.4);
    }

    .status-not-eligible {
        background: linear-gradient(135deg, #a5b4fc 0%, #c7d2fe 100%);
        color: #3730a3;
        box-shadow: 0 4px 15px rgba(165, 180, 252, 0.4);
    }

    .status-likely-eligible {
        background: linear-gradient(135deg, #86efac 0%, #bbf7d0 100%);
        color: #166534;
        box-shadow: 0 4px 15px rgba(134, 239, 172, 0.4);
    }

    .status-unclear {
        background: linear-gradient(135deg, #cbd5e1 0%, #e2e8f0 100%);
        color: #475569;
        box-shadow: 0 4px 15px rgba(203, 213, 225, 0.4);
    }

    /* Section headers - consistent styling */
    .section-header {
        color: #0f4c81;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 3px solid #e2e8f0;
    }

    /* Cards */
    .info-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
    }

    /* Buttons - base styling */
    .stButton > button {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Main area buttons */
    .main .stButton > button {
        background: linear-gradient(135deg, #0f4c81 0%, #1a6eb0 100%) !important;
        color: white !important;
        border: none !important;
        font-size: 14px !important;
        font-family: "Source Sans Pro", sans-serif !important;
        box-shadow: 0 4px 15px rgba(15, 76, 129, 0.3) !important;
    }

    .main .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(15, 76, 129, 0.4) !important;
    }

    /* Filter card styling */
    .filter-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    .filter-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .filter-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0f4c81;
        margin: 0;
    }

    .filter-section-inline {
        display: flex;
        align-items: center;
        gap: 0;
    }

    .filter-group {
        padding: 0 1.5rem;
        border-right: 2px solid #e2e8f0;
    }

    .filter-group:last-child {
        border-right: none;
    }

    .filter-group:first-child {
        padding-left: 0;
    }

    .filter-group-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .filter-stats {
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #475569;
        font-weight: 500;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: #f8fafc;
        border-radius: 16px;
        border: 2px dashed #cbd5e1;
    }

    .empty-state h3 {
        color: #475569;
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        color: #64748b;
    }

    /* Hide Streamlit branding and sidebar */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }

    /* Unified button styling for all action buttons (download, link, email) */
    .stDownloadButton > button,
    .stLinkButton > a {
        background: linear-gradient(135deg, #0f4c81 0%, #1a6eb0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        font-family: "Source Sans Pro", sans-serif !important;
        box-shadow: 0 4px 15px rgba(15, 76, 129, 0.3) !important;
        height: 38px !important;
        min-width: 130px !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(15, 76, 129, 0.4) !important;
        color: white !important;
        text-decoration: none !important;
    }

    /* Suggestion list styling */
    .suggestion-item {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 4px solid #0ea5e9;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        border-radius: 0 12px 12px 0;
        font-size: 0.95rem;
        color: #0c4a6e;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1);
    }

    .suggestion-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: #0ea5e9;
        color: white;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.75rem;
    }

    /* Patient header with aligned badge */
    .patient-header-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .patient-header-row h2 {
        margin: 0;
        font-size: 1.5rem;
        color: #0f4c81;
    }
</style>
""", unsafe_allow_html=True)

def load_eligibility_results():
    """Load eligibility results from JSON file."""
    results_file = "eligibility_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            return json.load(f)
    return []

def get_status_badge(status):
    """Return HTML for status badge."""
    status_class = status.lower().replace("_", "-")
    display_text = status.replace("_", " ")
    return f'<span class="status-badge status-{status_class}">{display_text}</span>'

def create_gauge_chart(value, title="Confidence"):
    """Create a gauge chart for confidence score with centered number."""
    # Ensure value is a valid number
    if value is None or not isinstance(value, (int, float)):
        value = 0
    color = "#67e8f9" if value >= 0.7 else "#86efac" if value >= 0.4 else "#a5b4fc"

    fig = go.Figure(go.Indicator(
        mode="gauge",
        value=value * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#94a3b8", 'tickfont': {'size': 11}},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "#f1f5f9",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 40], 'color': '#e0e7ff'},
                {'range': [40, 70], 'color': '#dcfce7'},
                {'range': [70, 100], 'color': '#cffafe'}
            ],
        }
    ))

    # Add centered annotation for the percentage value
    fig.add_annotation(
        x=0.5,
        y=0.25,
        text=f"<b>{value * 100:.0f}%</b>",
        showarrow=False,
        font=dict(size=36, color='#0f4c81', family='Inter'),
        xanchor='center',
        yanchor='middle'
    )

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#0f4c81", 'family': "Inter"}
    )

    return fig

def create_excel_report(data):
    """Create Excel report with multiple sheets."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        for r in data:
            criteria = r.get("criteria_evaluation", [])
            summary_data.append({
                "Patient ID": r.get("patient_id", "N/A"),
                "Eligibility Status": r.get("overall_eligibility", "N/A"),
                "Confidence Score": r.get("confidence_score", 0),
                "Criteria Met": sum(1 for c in criteria if c.get("status") == "MET"),
                "Criteria Not Met": sum(1 for c in criteria if c.get("status") == "NOT_MET"),
                "Needs Review": sum(1 for c in criteria if c.get("status") == "NEEDS_VERIFICATION"),
                "Recommendation": r.get("recommendation", "N/A")
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Detailed criteria sheet
        detailed_data = []
        for r in data:
            patient_id = r.get("patient_id", "N/A")
            for c in r.get("criteria_evaluation", []):
                detailed_data.append({
                    "Patient ID": patient_id,
                    "Criterion": c.get("criterion", "N/A"),
                    "Patient Value": c.get("patient_value", "N/A"),
                    "Status": c.get("status", "N/A").replace("NEEDS_VERIFICATION", "Review"),
                    "Score": c.get("score", "N/A")
                })

        if detailed_data:
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Criteria', index=False)

    output.seek(0)
    return output

def generate_email_body(data):
    """Generate email body with summary."""
    total = len(data)
    eligible = sum(1 for r in data if r.get("overall_eligibility") == "ELIGIBLE")
    not_eligible = sum(1 for r in data if r.get("overall_eligibility") == "NOT_ELIGIBLE")
    review = total - eligible - not_eligible

    body = f"""Clinical Trial Eligibility Screening Report

Summary:
- Total Patients Screened: {total}
- Eligible: {eligible}
- Not Eligible: {not_eligible}
- Requires Review: {review}

Patient Details:
"""
    for r in data:
        body += f"\n- {r.get('patient_id', 'N/A')}: {r.get('overall_eligibility', 'N/A')} (Confidence: {r.get('confidence_score', 0):.0%})"

    body += "\n\nPlease find the detailed report attached."

    return body

# Load data
results = load_eligibility_results()

# Main content - Header aligned to top
st.markdown("""
<div class="main-header">
    <h1>Clinical Trial Eligibility Screener</h1>
    <p>AI-Powered Patient Screening Dashboard</p>
</div>
""", unsafe_allow_html=True)

if not results:
    st.markdown("""
    <div class="empty-state">
        <h3>No Results Found</h3>
        <p>Run the eligibility screener to generate patient assessments.</p>
    </div>
    """, unsafe_allow_html=True)

    st.code("python elgibility-screener.py", language="bash")

    with st.expander("Getting Started Guide"):
        st.markdown("""
        1. **Prepare Patient Data**: Ensure CSV files are in the `patients/` folder
        2. **Run Screener**: Execute the command above in your terminal
        3. **View Results**: Refresh this dashboard to see the results
        """)

else:
    # Initialize session state for filters
    if "eligibility_filter" not in st.session_state:
        st.session_state.eligibility_filter = ["ELIGIBLE", "NOT_ELIGIBLE", "LIKELY_ELIGIBLE", "UNCLEAR"]
    if "confidence_filter" not in st.session_state:
        st.session_state.confidence_filter = 0.0

    # Tabs immediately below header
    tab1, tab2, tab3 = st.tabs(["📊  OVERVIEW", "👤  PATIENT DETAILS", "📋  FULL REPORT"])

    with tab1:
        # Filter expander
        with st.expander("🔍 Filters", expanded=False):
            filter_cols = st.columns([1, 0.05, 1])

            with filter_cols[0]:
                st.markdown('<p class="filter-group-label">Eligibility Status</p>', unsafe_allow_html=True)
                elig_col1, elig_col2 = st.columns(2)
                with elig_col1:
                    show_eligible = st.checkbox("Eligible", value="ELIGIBLE" in st.session_state.eligibility_filter, key="ov_elig")
                    show_likely = st.checkbox("Likely Eligible", value="LIKELY_ELIGIBLE" in st.session_state.eligibility_filter, key="ov_likely")
                with elig_col2:
                    show_not_eligible = st.checkbox("Not Eligible", value="NOT_ELIGIBLE" in st.session_state.eligibility_filter, key="ov_not_elig")
                    show_unclear = st.checkbox("Unclear", value="UNCLEAR" in st.session_state.eligibility_filter, key="ov_unclear")

            with filter_cols[1]:
                st.markdown('<div style="border-left: 2px solid #e2e8f0; height: 100px; margin-top: 1rem;"></div>', unsafe_allow_html=True)

            with filter_cols[2]:
                st.markdown('<p class="filter-group-label">Confidence Threshold</p>', unsafe_allow_html=True)
                confidence_min = st.slider("Minimum confidence", 0.0, 1.0, st.session_state.confidence_filter, 0.05, key="ov_conf", label_visibility="collapsed")

        # Build filter list for Overview
        ov_selected_statuses = []
        if show_eligible:
            ov_selected_statuses.append("ELIGIBLE")
        if show_not_eligible:
            ov_selected_statuses.append("NOT_ELIGIBLE")
        if show_likely:
            ov_selected_statuses.append("LIKELY_ELIGIBLE")
        if show_unclear:
            ov_selected_statuses.append("UNCLEAR")

        # Apply filters
        filtered_results = [
            r for r in results
            if r.get("overall_eligibility") in ov_selected_statuses
            and r.get("confidence_score", 0) >= confidence_min
        ]

        if not filtered_results:
            st.warning("No patients match the current filter criteria. Adjust filters to see results.")
        else:
            # Calculate metrics
            total_patients = len(filtered_results)
            eligible = sum(1 for r in filtered_results if r.get("overall_eligibility") == "ELIGIBLE")
            not_eligible = sum(1 for r in filtered_results if r.get("overall_eligibility") == "NOT_ELIGIBLE")
            likely_eligible = sum(1 for r in filtered_results if r.get("overall_eligibility") == "LIKELY_ELIGIBLE")
            unclear = sum(1 for r in filtered_results if r.get("overall_eligibility") == "UNCLEAR")

            # Add spacing between filters and KPIs
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            # KPIs only in Overview tab
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card total">
                    <p class="metric-value" style="color: #0f4c81;">{total_patients}</p>
                    <p class="metric-label">Total Screened</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card eligible">
                    <p class="metric-value" style="color: #0891b2;">{eligible}</p>
                    <p class="metric-label">Eligible</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card not-eligible">
                    <p class="metric-value" style="color: #4f46e5;">{not_eligible}</p>
                    <p class="metric-label">Not Eligible</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div class="metric-card review">
                    <p class="metric-value" style="color: #16a34a;">{likely_eligible + unclear}</p>
                    <p class="metric-label">Requires Review</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown('<p class="section-header">Eligibility Distribution</p>', unsafe_allow_html=True)

                # Create data for pie chart with light colors
                pie_data = []
                pie_colors = []
                color_map_pie = {
                    "Eligible": "#67e8f9",      # Light cyan
                    "Not Eligible": "#a5b4fc",   # Light indigo
                    "Likely Eligible": "#86efac", # Light green
                    "Unclear": "#cbd5e1"          # Light gray
                }

                if eligible > 0:
                    pie_data.append({"Status": "Eligible", "Count": eligible})
                    pie_colors.append(color_map_pie["Eligible"])
                if not_eligible > 0:
                    pie_data.append({"Status": "Not Eligible", "Count": not_eligible})
                    pie_colors.append(color_map_pie["Not Eligible"])
                if likely_eligible > 0:
                    pie_data.append({"Status": "Likely Eligible", "Count": likely_eligible})
                    pie_colors.append(color_map_pie["Likely Eligible"])
                if unclear > 0:
                    pie_data.append({"Status": "Unclear", "Count": unclear})
                    pie_colors.append(color_map_pie["Unclear"])

                if pie_data:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=[d["Status"] for d in pie_data],
                        values=[d["Count"] for d in pie_data],
                        hole=0.5,
                        marker_colors=pie_colors,
                        textinfo='label+percent',
                        textfont_size=13,
                        textfont_family="Inter",
                        pull=[0.03] * len(pie_data),
                        hovertemplate="<b>%{label}</b><br>%{value} patients<br>%{percent}<extra></extra>"
                    )])

                    fig_pie.update_layout(
                        showlegend=False,
                        margin=dict(l=20, r=20, t=20, b=20),
                        height=380,
                        paper_bgcolor='rgba(0,0,0,0)',
                        annotations=[dict(
                            text=f"<b>{total_patients}</b><br>Patients",
                            x=0.5, y=0.5,
                            font_size=18,
                            font_family="Inter",
                            showarrow=False
                        )]
                    )

                    st.plotly_chart(fig_pie, use_container_width=True)

            with chart_col2:
                st.markdown('<p class="section-header">Confidence Scores by Patient</p>', unsafe_allow_html=True)

                confidence_data = []
                for r in filtered_results:
                    status = r.get("overall_eligibility", "UNKNOWN")
                    confidence_data.append({
                        "Patient": r.get("patient_id", "N/A").replace("EHR_", ""),
                        "Confidence": r.get("confidence_score", 0),
                        "Status": status.replace("_", " ").title()
                    })

                # Light colors for bar chart
                color_map_bar = {
                    "Eligible": "#67e8f9",
                    "Not Eligible": "#a5b4fc",
                    "Likely Eligible": "#86efac",
                    "Unclear": "#cbd5e1"
                }

                if confidence_data:
                    fig_bar = px.bar(
                        confidence_data,
                        x="Patient",
                        y="Confidence",
                        color="Status",
                        color_discrete_map=color_map_bar,
                        text="Confidence"
                    )

                    fig_bar.update_traces(
                        texttemplate='%{text:.0%}',
                        textposition='outside',
                        textfont_size=11,
                        textfont_family="Inter"
                    )
                    fig_bar.update_layout(
                        yaxis_range=[0, 1.15],
                        xaxis_title="",
                        yaxis_title="Confidence",
                        legend_title="",
                        margin=dict(l=20, r=20, t=20, b=60),
                        height=380,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.25,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=12, family="Inter")
                        ),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter")
                    )
                    fig_bar.update_xaxes(tickfont=dict(size=11))
                    fig_bar.update_yaxes(tickformat=".0%", gridcolor="#e2e8f0")

                    st.plotly_chart(fig_bar, use_container_width=True)

            # Statistics row - removed Eligibility Rate
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="section-header">Key Statistics</p>', unsafe_allow_html=True)

            stat_col1, stat_col2, stat_col3 = st.columns(3)

            avg_confidence = sum(r.get("confidence_score", 0) for r in filtered_results) / len(filtered_results)
            total_criteria = sum(len(r.get("criteria_evaluation", [])) for r in filtered_results)
            avg_criteria_met = sum(
                sum(1 for c in r.get("criteria_evaluation", []) if c.get("status") == "MET")
                for r in filtered_results
            ) / total_patients if total_patients > 0 else 0

            with stat_col1:
                st.metric("Average Confidence", f"{avg_confidence:.1%}")
            with stat_col2:
                st.metric("Total Criteria Checked", f"{total_criteria:,}")
            with stat_col3:
                st.metric("Avg. Criteria Met", f"{avg_criteria_met:.1f}")

    with tab2:
        # Filter expander with patient dropdown
        with st.expander("🔍 Filters", expanded=False):
            filter_cols = st.columns([1, 0.05, 1, 0.05, 1])

            with filter_cols[0]:
                st.markdown('<p class="filter-group-label">Eligibility Status</p>', unsafe_allow_html=True)
                pd_elig_col1, pd_elig_col2 = st.columns(2)
                with pd_elig_col1:
                    pd_show_eligible = st.checkbox("Eligible", value=True, key="pd_elig")
                    pd_show_likely = st.checkbox("Likely Eligible", value=True, key="pd_likely")
                with pd_elig_col2:
                    pd_show_not_eligible = st.checkbox("Not Eligible", value=True, key="pd_not_elig")
                    pd_show_unclear = st.checkbox("Unclear", value=True, key="pd_unclear")

            with filter_cols[1]:
                st.markdown('<div style="border-left: 2px solid #e2e8f0; height: 100px; margin-top: 1rem;"></div>', unsafe_allow_html=True)

            with filter_cols[2]:
                st.markdown('<p class="filter-group-label">Confidence Threshold</p>', unsafe_allow_html=True)
                pd_confidence_min = st.slider("Minimum confidence", 0.0, 1.0, 0.0, 0.05, key="pd_conf", label_visibility="collapsed")

            with filter_cols[3]:
                st.markdown('<div style="border-left: 2px solid #e2e8f0; height: 100px; margin-top: 1rem;"></div>', unsafe_allow_html=True)

            with filter_cols[4]:
                st.markdown('<p class="filter-group-label">Select Patient</p>', unsafe_allow_html=True)
                # Build filter list for Patient Details
                pd_selected_statuses = []
                if pd_show_eligible:
                    pd_selected_statuses.append("ELIGIBLE")
                if pd_show_not_eligible:
                    pd_selected_statuses.append("NOT_ELIGIBLE")
                if pd_show_likely:
                    pd_selected_statuses.append("LIKELY_ELIGIBLE")
                if pd_show_unclear:
                    pd_selected_statuses.append("UNCLEAR")

                # Apply filters
                pd_filtered_results = [
                    r for r in results
                    if r.get("overall_eligibility") in pd_selected_statuses
                    and r.get("confidence_score", 0) >= pd_confidence_min
                ]

                patient_ids = [r.get("patient_id", f"Patient {i}") for i, r in enumerate(pd_filtered_results)]

                if patient_ids:
                    selected_patient = st.selectbox(
                        "Select patient",
                        patient_ids,
                        key="patient_select",
                        format_func=lambda x: f"📋 {x}",
                        label_visibility="collapsed"
                    )
                else:
                    selected_patient = None

        if not pd_filtered_results:
            st.warning("No patients match the current filter criteria. Adjust filters to see results.")
        else:
            selected_data = next((r for r in pd_filtered_results if r.get("patient_id") == selected_patient), pd_filtered_results[0])

            # Patient header with badge aligned to patient ID
            status = selected_data.get("overall_eligibility", "UNKNOWN")
            st.markdown(f"""
            <div class="patient-header-row">
                <h2>{selected_patient}</h2>
                {get_status_badge(status)}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Sub-tabs for Evaluation and Next Steps
            eval_tab, next_steps_tab = st.tabs(["📋 Evaluation", "💡 Next Steps"])

            with eval_tab:
                # Top row: Confidence Score and Clinical Recommendation side by side
                top_col1, top_col2 = st.columns(2)

                with top_col1:
                    st.markdown('<p class="section-header">Confidence Score</p>', unsafe_allow_html=True)
                    confidence = float(selected_data.get("confidence_score", 0) or 0)
                    st.plotly_chart(create_gauge_chart(confidence), use_container_width=True)

                with top_col2:
                    st.markdown('<p class="section-header">Clinical Recommendation</p>', unsafe_allow_html=True)
                    recommendation = selected_data.get("recommendation", "No recommendation available")
                    st.info(recommendation)

                # Bottom section: Criteria Evaluation (full width)
                st.markdown('<p class="section-header">Criteria Evaluation</p>', unsafe_allow_html=True)
                criteria = selected_data.get("criteria_evaluation", [])

                if criteria:
                    # Summary metrics
                    met = sum(1 for c in criteria if c.get("status") == "MET")
                    not_met = sum(1 for c in criteria if c.get("status") == "NOT_MET")
                    verify = sum(1 for c in criteria if c.get("status") == "NEEDS_VERIFICATION")

                    sum_col1, sum_col2, sum_col3 = st.columns(3)
                    sum_col1.metric("✅ Met", met)
                    sum_col2.metric("❌ Not Met", not_met)
                    sum_col3.metric("⚠️ Review", verify)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Criteria table with updated colors and Review label
                    criteria_df = pd.DataFrame(criteria)

                    column_map = {
                        "criterion": "Criterion",
                        "patient_value": "Patient Value",
                        "status": "Status",
                        "score": "Score"
                    }
                    criteria_df = criteria_df.rename(columns={k: v for k, v in column_map.items() if k in criteria_df.columns})

                    # Replace NEEDS_VERIFICATION with Review
                    if "Status" in criteria_df.columns:
                        criteria_df["Status"] = criteria_df["Status"].replace("NEEDS_VERIFICATION", "Review")

                    if "Score" in criteria_df.columns:
                        criteria_df["Score"] = criteria_df["Score"].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")

                    def highlight_status(row):
                        status_val = row.get("Status", "")
                        if status_val == "MET":
                            # Light green for Met
                            return ['background-color: #dcfce7; color: #166534'] * len(row)
                        elif status_val == "NOT_MET":
                            # Light red for Not Met
                            return ['background-color: #fee2e2; color: #991b1b'] * len(row)
                        elif status_val == "Review":
                            # Light yellow for Review
                            return ['background-color: #fef9c3; color: #854d0e'] * len(row)
                        return [''] * len(row)

                    styled_df = criteria_df.style.apply(highlight_status, axis=1)
                    # Dynamic height based on number of rows (35px per row + header)
                    table_height = min(400, max(100, len(criteria_df) * 35 + 40))
                    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=table_height)
                else:
                    st.info("No criteria evaluation data available for this patient.")

            with next_steps_tab:
                st.markdown('<p class="section-header">Suggestions</p>', unsafe_allow_html=True)
                next_steps = selected_data.get("next_steps", [])
                if next_steps:
                    for i, step in enumerate(next_steps, 1):
                        st.markdown(f"""
                        <div class="suggestion-item">
                            <span class="suggestion-number">{i}</span>
                            {step}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No specific suggestions defined for this patient.")

    with tab3:
        # Filter expander
        with st.expander("🔍 Filters", expanded=False):
            filter_cols = st.columns([1, 0.05, 1])

            with filter_cols[0]:
                st.markdown('<p class="filter-group-label">Eligibility Status</p>', unsafe_allow_html=True)
                fr_elig_col1, fr_elig_col2 = st.columns(2)
                with fr_elig_col1:
                    fr_show_eligible = st.checkbox("Eligible", value=True, key="fr_elig")
                    fr_show_likely = st.checkbox("Likely Eligible", value=True, key="fr_likely")
                with fr_elig_col2:
                    fr_show_not_eligible = st.checkbox("Not Eligible", value=True, key="fr_not_elig")
                    fr_show_unclear = st.checkbox("Unclear", value=True, key="fr_unclear")

            with filter_cols[1]:
                st.markdown('<div style="border-left: 2px solid #e2e8f0; height: 100px; margin-top: 1rem;"></div>', unsafe_allow_html=True)

            with filter_cols[2]:
                st.markdown('<p class="filter-group-label">Confidence Threshold</p>', unsafe_allow_html=True)
                fr_confidence_min = st.slider("Minimum confidence", 0.0, 1.0, 0.0, 0.05, key="fr_conf", label_visibility="collapsed")

        # Build filter list for Full Report
        fr_selected_statuses = []
        if fr_show_eligible:
            fr_selected_statuses.append("ELIGIBLE")
        if fr_show_not_eligible:
            fr_selected_statuses.append("NOT_ELIGIBLE")
        if fr_show_likely:
            fr_selected_statuses.append("LIKELY_ELIGIBLE")
        if fr_show_unclear:
            fr_selected_statuses.append("UNCLEAR")

        # Apply filters
        fr_filtered_results = [
            r for r in results
            if r.get("overall_eligibility") in fr_selected_statuses
            and r.get("confidence_score", 0) >= fr_confidence_min
        ]

        if not fr_filtered_results:
            st.warning("No patients match the current filter criteria. Adjust filters to see results.")
        else:
            st.markdown('<p class="section-header">Patient Summary Table</p>', unsafe_allow_html=True)

            # Action buttons between title and table - same style
            action_col1, action_col2, action_col3, action_col4 = st.columns([1, 1, 1, 2])

            with action_col1:
                # Excel export
                excel_data = create_excel_report(fr_filtered_results)
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"eligibility_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with action_col2:
                # CSV export
                summary_for_csv = []
                for r in fr_filtered_results:
                    summary_for_csv.append({
                        "Patient ID": r.get("patient_id", "N/A"),
                        "Eligibility": r.get("overall_eligibility", "N/A"),
                        "Confidence": r.get("confidence_score", 0),
                        "Recommendation": r.get("recommendation", "N/A")
                    })
                csv_df = pd.DataFrame(summary_for_csv)
                csv_data = csv_df.to_csv(index=False)

                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"eligibility_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            with action_col3:
                # Email button - using link_button for consistent styling
                email_subject = urllib.parse.quote(f"Clinical Trial Eligibility Report - {datetime.now().strftime('%Y-%m-%d')}")
                email_body = urllib.parse.quote(generate_email_body(fr_filtered_results))
                email_link = f"mailto:?subject={email_subject}&body={email_body}"

                st.link_button("✉️ Send via Email", email_link)

            st.markdown("<br>", unsafe_allow_html=True)

            # Full summary table
            summary_data = []
            for r in fr_filtered_results:
                criteria = r.get("criteria_evaluation", [])
                rec = r.get("recommendation", "N/A")
                summary_data.append({
                    "Patient ID": r.get("patient_id", "N/A"),
                    "Status": r.get("overall_eligibility", "N/A"),
                    "Confidence": f"{r.get('confidence_score', 0):.0%}",
                    "Met": sum(1 for c in criteria if c.get("status") == "MET"),
                    "Not Met": sum(1 for c in criteria if c.get("status") == "NOT_MET"),
                    "Review": sum(1 for c in criteria if c.get("status") == "NEEDS_VERIFICATION"),
                    "Recommendation": rec[:60] + "..." if len(rec) > 60 else rec
                })

            summary_df = pd.DataFrame(summary_data)

            def highlight_status_row(row):
                status_val = row.get("Status", "")
                if status_val == "ELIGIBLE":
                    return ['background-color: #dcfce7'] * len(row)  # Light green
                elif status_val == "NOT_ELIGIBLE":
                    return ['background-color: #fee2e2'] * len(row)  # Light red
                elif status_val == "LIKELY_ELIGIBLE":
                    return ['background-color: #fef9c3'] * len(row)  # Light yellow
                return ['background-color: #f1f5f9'] * len(row)

            styled_summary = summary_df.style.apply(highlight_status_row, axis=1)
            # Dynamic height based on number of rows (35px per row + header)
            summary_table_height = min(500, max(100, len(summary_df) * 35 + 40))
            st.dataframe(styled_summary, use_container_width=True, hide_index=True, height=summary_table_height)

            # Legend
            st.markdown("""
            <div style="display: flex; gap: 2rem; margin-top: 1.5rem; font-size: 0.9rem; flex-wrap: wrap;">
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: #dcfce7; padding: 4px 12px; border-radius: 6px; font-weight: 500; color: #166534;">Eligible</span>
                </span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: #fee2e2; padding: 4px 12px; border-radius: 6px; font-weight: 500; color: #991b1b;">Not Eligible</span>
                </span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: #fef9c3; padding: 4px 12px; border-radius: 6px; font-weight: 500; color: #854d0e;">Likely Eligible</span>
                </span>
                <span style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="background: #f1f5f9; padding: 4px 12px; border-radius: 6px; font-weight: 500; color: #475569;">Unclear</span>
                </span>
            </div>
            """, unsafe_allow_html=True)
