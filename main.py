import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("d2r_rwanda_2020.csv")

# Identify human-focused results
human_keywords = [
    "people", "children", "students", "farmers", "patients",
    "trained", "beneficiaries", "households", "teachers",
    "individuals", "recipients", "community", "participants"
]
df['is_human_impact'] = df['result_name'].str.lower().apply(
    lambda x: any(keyword in x for keyword in human_keywords)
)

# Sidebar filters
st.sidebar.title("Filters")
selected_years = st.sidebar.multiselect("Select Years", options=sorted(df['fiscal_year'].dropna().unique()), default=sorted(df['fiscal_year'].dropna().unique()))
selected_sectors = st.sidebar.multiselect("Select Sectors", options=sorted(df['sector_name'].dropna().unique()), default=sorted(df['sector_name'].dropna().unique()))

filtered_df = df[df['fiscal_year'].isin(selected_years) & df['sector_name'].isin(selected_sectors)]
human_df = filtered_df[filtered_df['is_human_impact'] == True]

# Ensure disbursements are aggregated correctly by avoiding NaNs
df['disbursements'] = pd.to_numeric(df['disbursements'], errors='coerce')
human_df['disbursements'] = pd.to_numeric(human_df['disbursements'], errors='coerce')

# Title
st.title("USAID Development Aid Impact in Rwanda (2014-2022)")

# Sectors with Most Disbursements
st.header("Top Sectors by Disbursements")
disbursement_summary = filtered_df.dropna(subset=['disbursements']).groupby('sector_name').agg(total_disbursed=('disbursements', 'sum')).reset_index()
disbursement_summary = disbursement_summary.sort_values(by='total_disbursed', ascending=False)
fig_top_sectors = px.bar(disbursement_summary.head(10), x='sector_name', y='total_disbursed', title="Top 10 Sectors by Disbursements")
st.plotly_chart(fig_top_sectors)

# Human Impact per Sector by Result Name
st.header("Impact in Terms of Human Outcomes")
human_impact_summary = human_df.groupby(['sector_name', 'result_name']).agg(total_impact=('value', 'sum')).reset_index()
human_impact_summary = human_impact_summary.sort_values(by='total_impact', ascending=False)
fig_impact = px.bar(human_impact_summary.head(20), x='total_impact', y='result_name', color='sector_name', orientation='h', title="Top 20 Human-Focused Results")
st.plotly_chart(fig_impact)

# Bubble chart: Human outcomes (bubble size) vs Funding (color intensity)
st.header("Bubble Visualization: Human Outcomes vs Disbursements")
bubble_data = human_df.dropna(subset=['disbursements']).groupby('sector_name').agg(
    total_impact=('value', 'sum'),
    total_disbursed=('disbursements', 'sum')
).reset_index()

fig_bubble = px.scatter(
    bubble_data,
    x='sector_name',
    y='total_impact',
    size='total_impact',
    color='total_disbursed',
    hover_name='sector_name',
    title='Human Outcomes (Bubble Size) and Disbursement (Color)',
    size_max=60
)
fig_bubble.update_layout(xaxis_title='Sector', yaxis_title='Total Human Outcomes')
st.plotly_chart(fig_bubble)

# Sector-wise Table
st.header("Detailed Sector Impact Table")
st.dataframe(human_df[['fiscal_year', 'sector_name', 'result_name', 'value', 'disbursements']])
