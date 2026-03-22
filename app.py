import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuration
st.set_page_config(page_title="Executive Revenue Dashboard", layout="wide")

COLOR_GOLD = "#D4AF37"
COLOR_NAVY = "#002B5E"
COLOR_ACCENT = "#8DA2B5"

DATA_FILE = "hotel_data.csv"

EXPECTED_COLUMNS = [
    'Date', 'Day', 'Segment', 'Arrivals', 'Departures', 
    'Rooms_Occupied', 'Occupancy_Pct', 'Adults_Children', 
    'Out_Of_Order', 'Available_Rooms', 'Forecasted_ADR', 
    'Enrollment_Goal_MTD', 'Enrollment_Actual_MTD', 
    'Enrollment_Goal_YTD', 'Enrollment_Actual_YTD', 
    'Upsell_Goal_MTD', 'Upsell_Hotel_MTD', 
    'Upsell_Goal_YTD', 'Upsell_Total_YTD', 
    'TrustYou_Score_MTD', 'TrustYou_Score_YTD', 'TrustYou_Score_LYMTD'
]

# Data Processing
def process_hotel_data(df):
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            if col in ['Date', 'Day', 'Segment']:
                df[col] = "Unknown"
            else:
                df[col] = 0         

    if df.empty:
        return df

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Day'] = df['Date'].dt.day_name()
    
    df['Total_Turns'] = df['Arrivals'] + df['Departures']
    df['RevPAR'] = df['Forecasted_ADR'] * (df['Occupancy_Pct'] / 100)
    df['Room_Revenue'] = df['Rooms_Occupied'] * df['Forecasted_ADR']
    df['Lost_Revenue'] = df['Out_Of_Order'] * df['Forecasted_ADR']

    if 'Lounge_Covers' not in df.columns:
        df['Lounge_Covers'] = df.apply(lambda row: row['Adults_Children'] * 0.75 if row['Segment'] == 'Gold' else 0, axis=1)
        
    df['Lounge_Capture_Rate'] = (df['Lounge_Covers'] / df['Adults_Children'].replace(0, 1)) * 100
    df['Lounge_Capture_Rate'] = df['Lounge_Capture_Rate'].fillna(0)
    
    return df

def load_master_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    else:
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
    return process_hotel_data(df)

# Session State Initialization
if 'live_data' not in st.session_state:
    st.session_state['live_data'] = load_master_data()

if 'viewing_temp' not in st.session_state:
    st.session_state['viewing_temp'] = False

df = st.session_state['live_data']

# Sidebar Operations
st.sidebar.title("Data Management")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    raw_new_df = pd.read_csv(uploaded_file)
    new_df = process_hotel_data(raw_new_df)
    
    st.sidebar.markdown("Choose how to handle this data:")
    
    if st.sidebar.button("Merge into Master Database"):
        master_df = load_master_data()
        combined_df = pd.concat([master_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['Date', 'Segment'], keep='last')
        
        columns_to_save = [col for col in EXPECTED_COLUMNS if col in combined_df.columns]
        combined_df[columns_to_save].to_csv(DATA_FILE, index=False)
        
        st.session_state['live_data'] = process_hotel_data(combined_df)
        st.session_state['viewing_temp'] = False
        st.sidebar.success("Data successfully merged and saved.")
        st.rerun()
        
    if st.sidebar.button("View File Only (Temporary)"):
        st.session_state['live_data'] = new_df
        st.session_state['viewing_temp'] = True
        st.rerun()

if st.session_state['viewing_temp']:
    st.sidebar.warning("Currently viewing temporary uploaded data. Changes are not saved.")
    if st.sidebar.button("Restore Master Database"):
        st.session_state['live_data'] = load_master_data()
        st.session_state['viewing_temp'] = False
        st.rerun()

st.sidebar.markdown("---")

# Smart Date Filter
display_df = df.copy()
if not df.empty:
    st.sidebar.subheader("Filter Dashboard")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
        display_df = df.loc[mask]

st.sidebar.markdown("---")
if not df.empty:
    st.sidebar.subheader("Export Database")
    csv_export = df[EXPECTED_COLUMNS].to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Master CSV",
        data=csv_export,
        file_name='hotel_data.csv',
        mime='text/csv',
    )

# Executive Dashboard Header
st.title("Executive Revenue & Operations Dashboard")

def create_gauge(title, value, goal, max_bound, prefix="", suffix="", color=COLOR_GOLD):
    safe_value = 0 if pd.isna(value) else value
    safe_goal = 1 if pd.isna(goal) or goal == 0 else goal
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=safe_value,
        title={'text': title, 'font': {'size': 18, 'color': '#333'}},
        number={'prefix': prefix, 'suffix': suffix, 'font': {'size': 32}},
        gauge={
            'axis': {'range': [None, max_bound], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': safe_goal}
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# Dynamic Calculations
if not display_df.empty:
    all_actual = display_df.groupby('Segment')['Enrollment_Actual_YTD'].max().sum()
    all_goal = display_df.groupby('Segment')['Enrollment_Goal_YTD'].max().sum()
    
    upsell_actual = display_df.groupby('Segment')['Upsell_Total_YTD'].max().sum()
    upsell_goal = display_df.groupby('Segment')['Upsell_Goal_YTD'].max().sum()
    
    rps_actual = display_df['TrustYou_Score_YTD'].mean()
    rps_goal = 100 
else:
    all_actual, all_goal = 0, 100
    upsell_actual, upsell_goal = 0, 100
    rps_actual, rps_goal = 0, 100

col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(create_gauge("ALL Enrollments (YTD)", all_actual, all_goal, max_bound=all_goal*1.2, color=COLOR_NAVY), use_container_width=True)
with col2:
    st.plotly_chart(create_gauge("Upsell Revenue (YTD)", upsell_actual, upsell_goal, max_bound=upsell_goal*1.2, prefix="$"), use_container_width=True)
with col3:
    st.plotly_chart(create_gauge("TrustYou Score (YTD)", rps_actual, rps_goal, max_bound=100, color=COLOR_ACCENT), use_container_width=True)

st.divider()

# Main Content Tabs
if display_df.empty:
    st.info("No data available in this date range. Please adjust your filters or upload a CSV.")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Yield & Revenue", "Segment Premium", "Operational Flow", "Fairmont Gold Strategy", "Inventory & Demographics"
    ])
    
    df_sorted = display_df.sort_values('Date')
    day_order = df_sorted['Day'].unique().tolist()

    with tab1:
        st.subheader("Section 1: Yield, Revenue & Financial Performance")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Room Revenue", f"${df_sorted['Room_Revenue'].sum():,.0f}")
        m2.metric("Blended ADR", f"${df_sorted['Forecasted_ADR'].mean():,.2f}")
        m3.metric("Blended RevPAR", f"${df_sorted['RevPAR'].mean():,.2f}")
        
        st.markdown("---")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Daily RevPAR Trajectory")
            fig_revpar = px.line(
                df_sorted, x="Day", y="RevPAR", color="Segment", markers=True,
                color_discrete_map={"Main": COLOR_NAVY, "Gold": COLOR_GOLD},
                category_orders={"Day": day_order}
            )
            fig_revpar.update_layout(template="plotly_white", yaxis_title="RevPAR ($)", xaxis_title="")
            st.plotly_chart(fig_revpar, use_container_width=True)
            
        with col_b:
            st.markdown("#### Revenue Generation by Segment")
            fig_rev = px.bar(
                df_sorted, x="Day", y="Room_Revenue", color="Segment",
                color_discrete_map={"Main": COLOR_NAVY, "Gold": COLOR_GOLD},
                category_orders={"Day": day_order}, barmode="stack"
            )
            fig_rev.update_layout(template="plotly_white", yaxis_title="Total Revenue ($)", xaxis_title="")
            st.plotly_chart(fig_rev, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown("#### ADR Comparison by Segment")
            fig_adr = px.line(
                df_sorted, x="Day", y="Forecasted_ADR", color="Segment", markers=True,
                color_discrete_map={"Main": COLOR_NAVY, "Gold": COLOR_GOLD},
                category_orders={"Day": day_order}
            )
            fig_adr.update_layout(template="plotly_white", yaxis_title="ADR ($)", xaxis_title="")
            st.plotly_chart(fig_adr, use_container_width=True)
            
        with col_d:
            st.markdown("#### Main House: Rate vs. Occupancy")
            df_main = df_sorted[df_sorted['Segment'] == 'Main']
            
            fig_main = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_main.add_trace(
                go.Bar(x=df_main['Day'], y=df_main['Occupancy_Pct'], name="Occupancy %", 
                       marker_color=COLOR_ACCENT, opacity=0.6), 
                secondary_y=False
            )
            
            fig_main.add_trace(
                go.Scatter(x=df_main['Day'], y=df_main['Forecasted_ADR'], name="ADR ($)", 
                           mode='lines+markers', line=dict(color=COLOR_NAVY, width=3)), 
                secondary_y=True
            )
            
            fig_main.update_layout(
                template="plotly_white", 
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig_main.update_yaxes(title_text="Occupancy (%)", secondary_y=False, range=[0, 110])
            fig_main.update_yaxes(title_text="ADR ($)", secondary_y=True)
            
            st.plotly_chart(fig_main, use_container_width=True)

    with tab2:
        st.subheader("Section 2: Segment Premium (Main vs Gold)")
        df_seg = df_sorted.groupby(['Day', 'Segment'])['Occupancy_Pct'].mean().reset_index()
        fig_occ = px.bar(
            df_seg, x="Day", y="Occupancy_Pct", color="Segment", barmode="group",
            color_discrete_map={"Main": COLOR_NAVY, "Gold": COLOR_GOLD},
            category_orders={"Day": day_order}
        )
        fig_occ.update_layout(template="plotly_white", yaxis_title="Occupancy (%)", xaxis_title="")
        st.plotly_chart(fig_occ, use_container_width=True)

    with tab3:
        st.subheader("Section 3: Housekeeping Workload Flow")
        df_sorted['Stay_Overs'] = df_sorted['Rooms_Occupied'] - df_sorted['Arrivals']
        df_sorted['Stay_Overs'] = df_sorted['Stay_Overs'].apply(lambda x: max(0, x)) 
        
        df_labor = df_sorted.groupby('Day')[['Departures', 'Stay_Overs']].mean().reset_index()
        fig_hk = px.bar(
            df_labor, x="Day", y=["Stay_Overs", "Departures"],
            title="Avg Daily Cleaning Volume",
            color_discrete_map={"Stay_Overs": COLOR_ACCENT, "Departures": COLOR_NAVY}, 
            barmode='stack', category_orders={"Day": day_order}
        )
        fig_hk.update_layout(template="plotly_white", xaxis_title="", legend_title="Task")
        st.plotly_chart(fig_hk, use_container_width=True)

    with tab4:
        st.subheader("Section 4: Fairmont Gold Strategy")
        
        col_gold1, col_gold2 = st.columns([2, 1])
        
        with col_gold1:
            if 'Gold' in df_sorted['Segment'].values and 'Main' in df_sorted['Segment'].values:
                df_spread = df_sorted.pivot_table(index='Day', columns='Segment', values='Forecasted_ADR', aggfunc='mean').reset_index()
                
                if 'Gold' in df_spread.columns and 'Main' in df_spread.columns:
                    df_spread['Premium'] = df_spread['Gold'] - df_spread['Main']
                    fig_premium = px.area(
                        df_spread, x="Day", y="Premium", title="The Gold Premium (Avg ADR Spread)", 
                        markers=True, color_discrete_sequence=[COLOR_GOLD],
                        category_orders={"Day": day_order}
                    )
                    fig_premium.update_layout(template="plotly_white", yaxis_title="Price Premium ($)", xaxis_title="")
                    st.plotly_chart(fig_premium, use_container_width=True)
                else:
                    st.warning("Need both Main and Gold segment data.")
            else:
                st.warning("Need both Main and Gold segment data.")

        with col_gold2:
            df_gold = df_sorted[df_sorted['Segment'] == 'Gold']
            avg_capture = df_gold['Lounge_Capture_Rate'].mean() if not df_gold.empty else 0

            fig_capture = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_capture,
                title={'text': "Lounge Capture Rate (%)", 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': COLOR_GOLD},
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 85}
                }
            ))
            fig_capture.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_capture, use_container_width=True)

            avg_main_revpar = df_sorted[df_sorted['Segment'] == 'Main']['RevPAR'].mean() if not df_sorted[df_sorted['Segment'] == 'Main'].empty else 0
            avg_gold_revpar = df_gold['RevPAR'].mean() if not df_gold.empty else 0
            st.metric("Avg Gold RevPAR", f"${avg_gold_revpar:.2f}")
            st.metric("Variance to Main", f"${avg_gold_revpar - avg_main_revpar:.2f}")

    with tab5:
        st.subheader("Section 5: Inventory & Demographics")
        
        col_inv1, col_inv2 = st.columns(2)
        
        with col_inv1:
            df_ooo = df_sorted.groupby('Day')[['Out_Of_Order', 'Lost_Revenue']].sum().reset_index()
            
            fig_ooo = make_subplots(specs=[[{"secondary_y": True}]])
            fig_ooo.add_trace(
                go.Bar(x=df_ooo['Day'], y=df_ooo['Out_Of_Order'], name="OOO Rooms", marker_color="#E74C3C"), 
                secondary_y=False
            )
            fig_ooo.add_trace(
                go.Scatter(x=df_ooo['Day'], y=df_ooo['Lost_Revenue'], name="Lost Revenue ($)", 
                           mode='lines+markers', line=dict(color="#C0392B", width=4)), 
                secondary_y=True
            )
            fig_ooo.update_layout(
                template="plotly_white", title_text="Out of Order Impact", 
                hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_ooo, use_container_width=True)
            
        with col_inv2:
            df_guests = df_sorted.groupby('Day')['Adults_Children'].sum().reset_index()
            
            fig_guests = px.area(
                df_guests, x="Day", y="Adults_Children", title="Total Guest Footprint", 
                color_discrete_sequence=[COLOR_ACCENT], markers=True,
                category_orders={"Day": day_order}
            )
            fig_guests.update_layout(template="plotly_white", yaxis_title="Total Guests", xaxis_title="")
            st.plotly_chart(fig_guests, use_container_width=True)
