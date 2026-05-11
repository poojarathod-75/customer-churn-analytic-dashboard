"""
Industry-Level Customer Churn Analytical Dashboard (Phase 2B)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency, f_oneway

from utils.document_loader import load_csv
from utils.validator import validate_file

st.set_page_config(page_title="Churn Analytical Dashboard", layout="wide")

st.title("🚀 Customer Churn Analytical Dashboard")

# =========================
# SIDEBAR
# =========================
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# =========================
# MAIN
# =========================
if uploaded_file is not None:

    if not validate_file(uploaded_file.name):
        st.error("Invalid file type")
    else:
        try:
            with st.spinner("Processing data..."):
                df = load_csv(uploaded_file)

            # =========================
            # CLEANING
            # =========================
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
            df.dropna(inplace=True)

            # =========================
            # FEATURE ENGINEERING
            # =========================
            df["tenure_group"] = pd.cut(
                df["tenure"],
                bins=[0, 12, 24, 48, 60, 100],
                labels=["0-12", "13-24", "25-48", "49-60", "61+"]
            )

            df["charge_band"] = pd.cut(
                df["MonthlyCharges"],
                bins=[0, 30, 60, 90, 120],
                labels=["Low", "Medium", "High", "Very High"]
            )

            # =========================
            # KPIs
            # =========================
            churn_rate = (df["Churn"] == "Yes").mean() * 100
            revenue_loss = df[df["Churn"] == "Yes"]["MonthlyCharges"].sum()
            annual_loss = revenue_loss * 12

            st.subheader("📊 Key Metrics")
            c1, c2, c3 = st.columns(3)
            c1.metric("Churn Rate", f"{churn_rate:.2f}%")
            c2.metric("Monthly Loss", f"${revenue_loss:.2f}")
            c3.metric("Annual Loss", f"${annual_loss:.2f}")

            # =========================
            # TABS
            # =========================
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📈 Segmentation", "🔥 Risk", "📊 Statistics", "🧠 Insights", "📊 Interactive"]
            )

            # -------------------------
            # SEGMENTATION
            # -------------------------
            with tab1:
                st.plotly_chart(px.histogram(df, x="Contract", color="Churn", barmode="group"))
                st.plotly_chart(px.histogram(df, x="tenure_group", color="Churn", barmode="group"))
                st.plotly_chart(px.histogram(df, x="PaymentMethod", color="Churn", barmode="group"))

            # -------------------------
            # RISK HEATMAP
            # -------------------------
            with tab2:
                heat = df.groupby(["Contract", "tenure_group"])["Churn"] \
                         .apply(lambda x: (x == "Yes").mean()).reset_index()

                pivot = heat.pivot(index="Contract", columns="tenure_group", values="Churn")

                st.plotly_chart(px.imshow(pivot, text_auto=True, color_continuous_scale="Reds"))

            # -------------------------
            # STATISTICS
            # -------------------------
            with tab3:
                st.subheader("Statistical Tests")

                contingency = pd.crosstab(df["Contract"], df["Churn"])
                chi2, p, _, _ = chi2_contingency(contingency)
                st.write(f"Chi-square p-value (Contract vs Churn): {p:.5f}")

                df["Churn_binary"] = df["Churn"].map({"Yes": 1, "No": 0})
                corr = df["tenure"].corr(df["Churn_binary"])
                st.write(f"Correlation (Tenure vs Churn): {corr:.2f}")

                churn_yes = df[df["Churn"] == "Yes"]["MonthlyCharges"]
                churn_no = df[df["Churn"] == "No"]["MonthlyCharges"]

                f_stat, p_anova = f_oneway(churn_yes, churn_no)
                st.write(f"ANOVA p-value (Charges vs Churn): {p_anova:.5f}")

                drivers = pd.DataFrame({
                    "Feature": ["Contract", "Tenure", "MonthlyCharges"],
                    "Metric": ["Chi-square", "Correlation", "ANOVA"],
                    "Score": [p, corr, p_anova]
                })

                st.dataframe(drivers)

            # -------------------------
            # INSIGHTS
            # -------------------------
            with tab4:
                st.subheader("Business Insights")

                insights = []

                if p < 0.05:
                    insights.append("Contract type significantly impacts churn")

                if corr < -0.3:
                    insights.append("Customers with low tenure are more likely to churn")

                if p_anova < 0.05:
                    insights.append("Monthly charges significantly affect churn")

                for i in insights:
                    st.write(f"🔍 {i}")

            # -------------------------
            # INTERACTIVE VISUALIZATION
            # -------------------------
            with tab5:
                st.subheader("📊 Interactive Churn Analysis")

                feature = st.selectbox(
                    "Select Feature for Analysis",
                    ["Contract", "tenure_group", "PaymentMethod", "InternetService"]
                )

                chart_type = st.selectbox(
                    "Select Chart Type",
                    ["Bar Chart", "Pie Chart", "Line Chart", "Box Plot"]
                )

                churn_data = df.groupby(feature)["Churn"].apply(
                    lambda x: (x == "Yes").mean()
                ).reset_index()

                churn_data.columns = [feature, "ChurnRate"]

                if chart_type == "Bar Chart":
                    fig = px.bar(
                        churn_data,
                        x=feature,
                        y="ChurnRate",
                        color="ChurnRate",
                        title=f"Churn Rate by {feature}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Pie Chart":
                    fig = px.pie(
                        churn_data,
                        names=feature,
                        values="ChurnRate",
                        title=f"Churn Distribution by {feature}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Line Chart":
                    fig = px.line(
                        churn_data,
                        x=feature,
                        y="ChurnRate",
                        markers=True,
                        title=f"Churn Trend by {feature}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif chart_type == "Box Plot":
                    fig = px.box(
                        df,
                        x=feature,
                        y="MonthlyCharges",
                        color="Churn",
                        title=f"Monthly Charges Distribution by {feature}"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # -------------------------
            # DOWNLOAD
            # -------------------------
            st.download_button("Download Data", df.to_csv(index=False), "data.csv")

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Upload CSV to start")
