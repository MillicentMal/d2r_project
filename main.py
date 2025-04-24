import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Load data
@st.cache
def load_data():
    return pd.read_csv("d2r_rwanda_2020.csv")

df = load_data()

# 2. Identify human-focused results
human_keywords = [
    "people", "children", "students", "farmers", "patients",
    "trained", "beneficiaries", "households", "teachers",
    "individuals", "recipients", "community", "participants"
]
df['is_human_impact'] = df['result_name'].str.lower().apply(
    lambda x: any(keyword in x for keyword in human_keywords)
)

# 3. Sidebar filters
st.sidebar.title("Filters")

years = sorted(df['fiscal_year'].dropna().unique())
sectors = sorted(df['sector_name'].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Select Years", options=years, default=years
)
selected_sectors = st.sidebar.multiselect(
    "Select Sectors", options=sectors, default=sectors
)

# only show result_names that actually appear in the filtered data
filtered_base = df[
    df['fiscal_year'].isin(selected_years) & 
    df['sector_name'].isin(selected_sectors)
]

result_names = sorted(filtered_base['result_name'].unique())
selected_results = st.sidebar.multiselect(
    "Select Result Names",
    options=result_names,
    default=result_names
)

# final filtered df
filtered_df = filtered_base[filtered_base['result_name'].isin(selected_results)]
human_df = filtered_df[filtered_df['is_human_impact']]

# 4. Main page
st.title("USAID Aid Impact on Rwanda Vision 2020")
st.markdown(
    "Use the sidebar to pick years, sectors and specific result indicators.  \n"
    "Below you’ll see overall disbursement rankings, human-impact breakdowns, bubbles—and per-sector drilldowns."
)

# A) Top sectors by total disbursement
st.header("Top Sectors by Total Disbursements")
disp = (
    filtered_df
    .dropna(subset=['disbursements'])
    .groupby('sector_name')['disbursements']
    .sum()
    .reset_index()
    .sort_values('disbursements', ascending=False)
)
fig1 = px.bar(
    disp.head(10),
    x='sector_name',
    y='disbursements',
    labels={'sector_name':'Sector','disbursements':'Total Disbursed'},
    title="Top 10 Sectors by Disbursement"
)
fig1.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig1, use_container_width=True)

# B) Top human-impact indicators overall
st.header("Top Human-Focused Results (All Sectors)")
impact = (
    human_df
    .groupby('result_name')['value']
    .sum()
    .reset_index()
    .sort_values('value', ascending=False)
)
fig2 = px.bar(
    impact.head(20),
    x='value',
    y='result_name',
    orientation='h',
    labels={'value':'Total People Impacted','result_name':'Indicator'},
    title="Top 20 Human-Focused Results"
)
st.plotly_chart(fig2, use_container_width=True)

# C) Bubble chart: per-sector human impact vs funding
st.header("Bubble: Human Outcomes vs Funding by Sector")
bubble = (
    human_df
    .groupby('sector_name')
    .agg(
        total_impact=('value','sum'),
        total_disbursed=('disbursements','sum')
    )
    .reset_index()
    .dropna()
)
fig3 = px.scatter(
    bubble,
    x='sector_name',
    y='total_impact',
    size='total_impact',
    color='total_disbursed',
    hover_name='sector_name',
    labels={'total_impact':'People Impacted','sector_name':'Sector','total_disbursed':'Disbursed'},
    title="Bubble: Human Impact (size) vs Disbursement (color)",
    size_max=60
)
fig3.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig3, use_container_width=True)

# D) Drill-down: for each selected sector, show its result_name breakdown
st.header("Drill-down: Result Names per Sector")
for sector in selected_sectors:
    sec_df = filtered_df[filtered_df['sector_name'] == sector]
    if sec_df.empty:
        continue
    sec_summary = (
        sec_df.groupby('result_name')['value']
        .sum()
        .reset_index()
        .sort_values('value', ascending=False)
    )
    st.subheader(f"{sector}")
    fig4 = px.bar(
        sec_summary,
        x='value',
        y='result_name',
        orientation='h',
        labels={'value':'Total Value','result_name':'Indicator'},
        title=f"{sector}: Breakdown by Result Name"
    )
    st.plotly_chart(fig4, use_container_width=True)

# E) Detailed table
st.header("Detailed Data Table")
st.dataframe(
    filtered_df[['fiscal_year','sector_name','result_name','value','disbursements']],
    height=300
)
