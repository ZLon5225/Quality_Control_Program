import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Google Sheets Setup for Testing
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Path to the JSON credentials file
credentials_path = "GOOGLE_CREDENTIALS-JSON.json"

# Load credentials from Streamlit Secrets
# Google Sheets Setup
import json
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit Secrets
credentials_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
credentials_dict = json.loads(credentials_json)

# Authenticate and create the client
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)

# Access the Google Sheet
sheet = client.open("Quality Control Program").sheet1

# Initialize session state for data storage
if "dataTesting" not in st.session_state:
    st.session_state["dataTesting"] = []

# Initialize DataFrame for plotting if not already in session state
if "plot_data" not in st.session_state:
    st.session_state["plot_data"] = pd.DataFrame(columns=["timestamp", "production_line", "production_rate"])

# Helper function to plot scatter and trendline for each line
def plot_individual_lines(data):
    grouped = data.groupby("production_line")
    for line, group in grouped:
        plt.figure(figsize=(10, 6))

        # Convert timestamps to datetime objects
        group["time"] = pd.to_datetime(group["timestamp"])

        # Prepare x and y data
        x = group["time"]
        y = group["production_rate"].values

        # Scatter plot
        plt.scatter(x, y, label=f"{line} (Data Points)")

        # Trendline using Linear Regression
        if len(x) > 1:  # Fit only if there's enough data
            # Convert datetime to numeric values for regression
            x_numeric = np.array([t.timestamp() for t in x]).reshape(-1, 1)
            model = LinearRegression()
            model.fit(x_numeric, y)
            y_pred = model.predict(x_numeric)
            plt.plot(x, y_pred, label=f"{line} (Trendline)", linestyle="--")

        # Format the x-axis range
        plt.xlim([datetime.combine(datetime.now(), time(8, 0)),
                  datetime.combine(datetime.now(), time(19, 0))])
        plt.xticks(rotation=45)
        plt.title(f"Production Rates for {line}")
        plt.xlabel("Time of Day")
        plt.ylabel("Production Rate (Bottles per Minute)")
        plt.legend()
        plt.grid(True)

        # Display the plot in Streamlit
        st.pyplot(plt)

# Target fill levels for each product (in ounces)
target_fill_levels_testing = {
    "64oz Family Dollar Lemon Ammonia": 64,
    "64oz True Living Lemon Ammonia RP2555": 64,
    "64oz True Living Cleaning Vinegar RP2555": 64,
    "33oz True Living Lavender MPC": 33,
    "24oz True Living Pine MPC RP2106": 24,
    "56oz Terriffic! Pine": 56,
    "56oz Terriffic! Lavender": 56,
    "40oz Sun-Pine Window Spray Bonus RP2520": 40,
    "40oz Sun-Pine Cleaner with Bleach/Peroxide Bonus": 40,
    "56oz Sun-Pine Lavender Floor Cleaner RP2290": 56,
    "32oz CVS Drain Opener": 32,
    "32oz Mr. Plumber Drain Opener": 32,
    "32oz Red Cleaning Vinegar RP2325": 32,
    "32oz Red Value Window Cleaner": 32,
    "32oz Solutions Pink AllPurpose": 32,
    "56oz Red Cleaning Vinegar Original": 56,
    "32oz Tile Plus 4 in 1": 32,
    "64oz Maxx Bubbles": 64,
    "128oz Maxx Bubbles": 128
}

# Torque testing threshold
torque_threshold_testing = 7.0  # ft-lbs

# App title
st.title("Sun-Pine Quality Control Management Platform - Testing")
st.markdown(
    """
    **Instructions for Supervisors (Testing Environment)**:  
    Please complete this form every 15 minutes. Record accurate data for quality control checkpoints.  
    """
)

# Input section
st.header("Input Data for Quality Checkpoints (Testing)")

# Current date input
current_date_testing = st.date_input("Select Current Date", value=datetime.now().date())

# Sample time input
sample_time_testing = st.text_input("Enter Time of Sample Taken (Testing) (e.g., 2:30 PM)")

# Supervisor selection dropdown
supervisor_testing = st.selectbox(
    "Identify Supervisor (Testing)",
    options=[
        "Zach Courtney", "Parker Reed", "Lee Thomas", "Michael Courtney",
        "Angela Przekota", "LaToria Johnson", "Wendell Carter",
        "Rodney Roberts", "Stanley Luckett"
    ]
)

# Production line selection dropdown
production_line_testing = st.selectbox(
    "Select Production Line (Testing)",
    options=[
        "Line 1", "Line 2", "Line 3", "Line 4", "Line 5",
        "Line 6", "Line 7", "Line 8", "Line 9"
    ]
)

# Product selection dropdown
product_testing = st.selectbox(
    "Select Product Being Checked (Testing)",
    options=list(target_fill_levels_testing.keys())
)

# Torque Testing
st.header("Torque Testing (Testing)")
st.markdown(
    """
    **Instructions for Torque Testing**:  
    Test 3 different samples using the torque measurement device and record the results below.
    """
)

# Input torque measurements
torque_1_testing = st.number_input("Enter Torque Measurement for Sample 1 (ft-lbs):", min_value=0.0, step=0.1, format="%.2f")
torque_2_testing = st.number_input("Enter Torque Measurement for Sample 2 (ft-lbs):", min_value=0.0, step=0.1, format="%.2f")
torque_3_testing = st.number_input("Enter Torque Measurement for Sample 3 (ft-lbs):", min_value=0.0, step=0.1, format="%.2f")

# Calculate the average torque
average_torque_testing = (torque_1_testing + torque_2_testing + torque_3_testing) / 3 if torque_1_testing and torque_2_testing and torque_3_testing else 0.0

# Display average torque and validate
torque_status_testing = "N/A"
if torque_1_testing and torque_2_testing and torque_3_testing:
    st.write(f"**Average Torque: {average_torque_testing:.2f} ft-lbs (Testing)**")
    if average_torque_testing >= torque_threshold_testing:
        st.success("The average torque is acceptable.")
        torque_status_testing = "Acceptable"
    else:
        st.error(f"The average torque is below the acceptable threshold of {torque_threshold_testing} ft-lbs.")
        torque_status_testing = "Not Acceptable"

# Bottle and Case Code Verification
st.header("Bottle and Case Code Verification (Testing)")
bottle_code_legible = st.radio("Is the bottle coded with a legible batch code?", options=["Yes", "No"])
bottle_batch_code = ""
if bottle_code_legible == "Yes":
    bottle_batch_code = st.text_input("Enter the Bottle Batch Code:")

case_code_legible = st.radio("Is the case coded with a legible batch code?", options=["Yes", "No"])
case_batch_code = ""
if case_code_legible == "Yes":
    case_batch_code = st.text_input("Enter the Case Batch Code:")

# Check if bottle and case batch codes match
batch_code_match = "N/A"
if bottle_batch_code and case_batch_code:
    if bottle_batch_code == case_batch_code:
        st.success("The bottle and case batch codes match.")
        batch_code_match = "Yes"
    else:
        st.error("The bottle and case batch codes do not match. Notify the supervisor.")
        batch_code_match = "No"
# Fill Level Section
st.header("Fill Level Check (Testing)")

# Display the target fill level for the selected product
if product_testing in target_fill_levels_testing:
    target_fill = target_fill_levels_testing[product_testing]
    lower_bound = target_fill * 0.95
    upper_bound = target_fill * 1.05

    st.write(f"**Target Fill Level for {product_testing}: {target_fill} oz**")
    st.write(f"**Acceptable Range: {lower_bound:.2f} oz to {upper_bound:.2f} oz**")

    # Input for actual fill level
    actual_fill_level_testing = st.number_input(
        "Enter Actual Fill Level (in ounces):",
        min_value=0.0,
        step=0.1,
        format="%.2f"
    )

    # Check if the actual fill level is within the acceptable range
    fill_level_status = "N/A"
    if actual_fill_level_testing:
        if lower_bound <= actual_fill_level_testing <= upper_bound:
            st.success(f"The fill level of {actual_fill_level_testing:.2f} oz is within the acceptable range.")
            fill_level_status = "Acceptable"
        else:
            st.error(f"The fill level of {actual_fill_level_testing:.2f} oz is outside the acceptable range.")
            fill_level_status = "Not Acceptable"
else:
    st.warning("Please select a valid product to display the target fill level.")

submit_testing = st.button("Submit Quality Check")

# Submit Data to Google Sheets
if submit_testing:
    # Generate timestamp
    timestamp_testing = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Collect data for submission
    row_data = [
        timestamp_testing,                         # Timestamp
        str(current_date_testing),                 # Current Date
        sample_time_testing or "",                 # Sample Time
        supervisor_testing or "",                  # Supervisor Name
        production_line_testing or "",             # Production Line
        product_testing or "",                     # Product
        target_fill if product_testing in target_fill_levels_testing else 0,  # Target Fill Level
        actual_fill_level_testing or 0,            # Actual Fill Level
        fill_level_status,                         # Fill Level Status
        torque_1_testing or 0,                     # Torque Sample 1
        torque_2_testing or 0,                     # Torque Sample 2
        torque_3_testing or 0,                     # Torque Sample 3
        round(average_torque_testing, 2) if average_torque_testing else 0,  # Average Torque
        torque_status_testing or "",               # Torque Status
        bottle_batch_code or "",                   # Bottle Batch Code
        case_batch_code or "",                     # Case Batch Code
        batch_code_match or "",                    # Batch Code Match (Yes/No)
        production_rate_testing or 0,              # Production Rate
        total_employees_testing or 0,              # Total Employees
        supervisor_comments_testing or ""          # Supervisor Comments
    ]

    # Debugging Output
    st.write("Data being sent to Google Sheets:")
    st.write(row_data)

    # Append Data to Google Sheets
    try:
        sheet.append_row(row_data)
        st.success("Quality checkpoint submitted successfully!")
    except Exception as e:
        st.error(f"Error appending data to Google Sheets: {e}")

