import streamlit as st
from datetime import datetime
from trainline_utils import get_plan, find_connections, STATIONS, ALLOWED_ICE_FROM_HAM, ALLOWED_ICE_FROM_AMS

st.set_page_config(page_title="Amsterdam ↔ Hamburg Train Finder", layout="centered")

st.title("🚆 Amsterdam ↔ Hamburg Train Finder")
st.markdown(
    "Find ICE and NJ trains between Hamburg and Amsterdam using Deutsche Bahn API.\n\n"
    "Select the route, date, and time to find available trains"
)

stations = ["Hamburg Hbf", "Amsterdam Centraal"]

col1, col2 = st.columns(2)
with col1:
    from_station = st.selectbox("From", stations, index=0)
with col2:
    
    to_station = st.selectbox("To", stations, index=1 if from_station == "Hamburg Hbf" else 0)

date_input = st.date_input("Select Date", value=datetime.now().date(), min_value=datetime.now().date())
time_input = st.time_input("Select Starting Time", value=datetime.now().time().replace(second=0, microsecond=0))

search = st.button("Search Trains")

def get_allowed_trains_and_types(from_station):
    if from_station == "Hamburg Hbf":
        return ALLOWED_ICE_FROM_HAM, {"ICE"}  # Only ICE
    else:
        return ALLOWED_ICE_FROM_AMS, {"ICE", "NJ"}

if search:
    dt_selected = datetime.combine(date_input, time_input)
    if dt_selected < datetime.now():
        st.error("Selected time cannot be in the past.")
    elif from_station == to_station:
        st.error("From and To stations cannot be the same.")
    else:
        date_str = dt_selected.strftime("%y%m%d")
        allowed_trains, allowed_types = get_allowed_trains_and_types(from_station)

        results = []
        for offset in range(12):  
            hour = (dt_selected.hour + offset) % 24
            hour_str = f"{hour:02d}"
            try:
                plan = get_plan(STATIONS[from_station], date_str, hour_str)
                # Filter trains
                trains = find_connections(plan, allowed_trains, allowed_types)
                results.extend(trains)
            except Exception as e:
                st.warning(f"[Warn] Failed to fetch data for hour {hour_str}: {e}")

        results.sort(key=lambda x: x['depart'])

        if results:
            import pandas as pd

            # Prepare table data with From and To columns
            table_data = []
            for train in results:
                table_data.append({
                    "Train": train["train"],
                    "Departure Time": train["depart"],
                    "From": from_station,
                    "Towards": to_station
                })

            df = pd.DataFrame(table_data)
            st.subheader(f"🚄 Trains from {from_station} to {to_station} ")
            df.index = df.index + 1 
            st.table(df)

        else:
            st.info(f"No trains found from {from_station} to {to_station} ")
