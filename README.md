Executive Revenue & Ops Dashboard
A high-level analytics tool for luxury hotels to track revenue, segment yield, and operational efficiency.

Key Features
Dynamic Gauges: Real-time tracking of Enrollments, Upsell Revenue ($800k goal), and Guest Satisfaction.

Segment Analysis: Direct RevPAR/ADR comparison between Main House and Fairmont Gold.

Operational Flow: Automated housekeeping volume and Out-of-Order (OOO) impact.

Smart Timeline: X-axis automatically adjusts to your data’s start date. No empty spaces.

Getting Started
1. Data Format
Your file must be named hotel_data.csv and include these headers:
Date, Day, Segment, Arrivals, Departures, Rooms_Occupied, Occupancy_Pct, Adults_Children, Out_Of_Order, Forecasted_ADR, Upsell_Total_YTD, TrustYou_Score_YTD.

2. Uploading Data

View File Only: Temporary "What-If" mode. Doesn't change your master file.

Merge into Master: Permanently adds data to your history and removes duplicates.

Important: Saving Data in the Cloud ☁️
Streamlit Cloud can read from GitHub but cannot write back to it.

The Issue: Merged data is stored on a temporary drive. If the app reboots, new data is lost.

The Fix: After merging, click Download Master CSV and upload that file manually to your GitHub repo to "save" your progress.

Dashboard Tabs
Yield & Revenue: Financial KPIs and Rate vs. Occupancy.

Segment Premium: Occupancy gaps between Main and Gold.

Operational Flow: Housekeeping tasks (Stay-overs vs. Departures).

Gold Strategy: Lounge capture rates and pricing premiums.

Inventory: OOO rooms and total guest footprint.

Tech Stack
Python, Streamlit, Plotly, and Pandas.
