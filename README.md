# Executive Revenue & Ops Dashboard 🏨

**Live Demo:** [https://hotel-analytics-kcast7amfrsdhdrnn5sfry.streamlit.app/](https://hotel-analytics-kcast7amfrsdhdrnn5sfry.streamlit.app/)

A professional, data-driven analytics suite for luxury hotels to track segment yield, operational flow, and revenue goals.

---

### Core Features
* **Dynamic Performance Gauges:** Real-time tracking of ALL Enrollments, Upsell Revenue ($800k goal), and TrustYou scores.
* **Segment Analytics:** Compare RevPAR and ADR between **Main House** and **Fairmont Gold**.
* **Operational Flow:** Automated housekeeping volume forecasting and Out-of-Order (OOO) impact tracking.
* **Smart Timeline:** The dashboard automatically adjusts its X-axis to match the dates in your dataset.

---

### Getting Started

#### 1. Data Requirements
The dashboard expects a CSV named `hotel_data.csv`. Ensure your file includes these exact headers:
`Date`, `Day`, `Segment`, `Arrivals`, `Departures`, `Rooms_Occupied`, `Occupancy_Pct`, `Adults_Children`, `Out_Of_Order`, `Forecasted_ADR`, `Upsell_Total_YTD`, `TrustYou_Score_YTD`.

#### 2. Using the Sidebar
* **View File Only:** Temporary "What-If" mode. View any CSV without changing the master database.
* **Merge into Master:** Permanently appends data to your history and removes duplicates for the same date.

---

### Important: Data Persistence in the Cloud ☁️
Streamlit Cloud can **read** from GitHub but cannot **write** back to it.

> **The Ghost File Rule:** When you click "Merge," data is saved to a temporary virtual disk. If the app reboots or you push new code, that data is wiped.

**How to save permanently:**
1. Upload and **Merge** your data.
2. Click **Download Master CSV** in the sidebar.
3. Manually upload that file to your GitHub repository to "lock in" the updates.

---

### Dashboard Sections
* **Yield & Revenue:** Financial KPIs and Rate vs. Occupancy compression.
* **Segment Premium:** Occupancy gaps between Main and Gold.
* **Operational Flow:** Housekeeping tasks (Stay-overs vs. Departures).
* **Gold Strategy:** Lounge capture rates and pricing premiums.
* **Inventory:** OOO room volume and total guest footprint.

---

### Technical Stack
* **Language:** Python 3.x
* **Framework:** Streamlit
* **Visuals:** Plotly
* **Data:** Pandas
