import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("GOOGLE_CREDENTIALS_JSON.json", scope)  # Replace with your JSON file path
client = gspread.authorize(credentials)

# Open the Google Sheet (replace 'Your Quality Sheet Name' with the actual sheet name)
sheet = client.open("Quality Control Program").sheet1  # Replace with your Google Sheet name

# Initialize session state for data storage
if "data" not in st.session_state:
    st.session_state["data"] = []

# Target fill levels for each product (in ounces)
target_fill_levels = {
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
torque_threshold = 8.0  # ft-lbs

# App title
st.title("Sun-Pine Quality Control Management Platform")
st.markdown(
    """
    **Instructions for Supervisors**:  
    Please complete this form every 15 minutes. Record accurate data for quality control checkpoints.  
    """
)

# Input section
st.header("Input Data for Quality Checkpoints")

# Current date input
current_date = st.date_input("Select Current Date", value=datetime.now().date())

# Sample time input
sample_time = st.text_input("Enter Time of Sample Taken (e.g., 2:30 PM)")

# Supervisor selection dropdown
supervisor = st.selectbox(
    "Identify Supervisor",
    options=[
        "Zach Courtney", "Parker Reed", "Lee Thomas", "Michael Courtney",
        "Angela Przekota", "LaToria Johnson", "Wendell Carter",
        "Rodney Roberts", "Stanley Luckett"
    ]
)

# Production line selection dropdown
production_line = st.selectbox(
    "Select Production Line",
    options=[
        "Line 1", "Line 2", "Line 3", "Line 4", "Line 5",
        "Line 6", "Line 7", "Line 8", "Line 9"
    ]
)

# Product selection dropdown
product = st.selectbox(
    "Select Product Being Checked",
    options=list(target_fill_levels.keys())
)

# Retrieve the target fill level for the selected product
target_fill = target_fill_levels[product]

# Calculate the acceptable range
lower_bound = target_fill * 0.95
upper_bound = target_fill * 1.05

# Display the acceptable range
st.write(f"**Target Fill Level for {product}: {target_fill}oz**")
st.write(f"**Acceptable Range: {lower_bound:.2f}oz to {upper_bound:.2f}oz**")

# Input the actual fill level
actual_fill_level = st.number_input(
    "Enter Actual Fill Level (in ounces)",
    min_value=0.0,
    step=0.1,
    format="%.2f"
)

# Check if the actual fill level is within the acceptable range
fill_level_status = "N/A"
if actual_fill_level:
    if lower_bound <= actual_fill_level <= upper_bound:
        st.success(f"The fill level of {actual_fill_level:.2f}oz is within the acceptable range.")
        fill_level_status = "Acceptable"
    else:
        st.error(f"The fill level of {actual_fill_level:.2f}oz is outside the acceptable range.")
        fill_level_status = "Not Acceptable"

# Additional quality checks
label_alignment = st.radio("Is the label alignment correct?", options=["Yes", "No"])

# Removal Torque Testing
st.header("Removal Torque Testing")
st.markdown(
    """
    **Instructions for Testing Torque**:
    1. Use the torque measurement device to test 3 different samples.
    2. Record the torque values (in ft-lbs) for all 3 samples below.
    """
)

# Input torque measurements
torque_1 = st.number_input("Enter Torque Measurement for Sample 1 (ft-lbs)", min_value=0.0, step=0.1, format="%.2f")
torque_2 = st.number_input("Enter Torque Measurement for Sample 2 (ft-lbs)", min_value=0.0, step=0.1, format="%.2f")
torque_3 = st.number_input("Enter Torque Measurement for Sample 3 (ft-lbs)", min_value=0.0, step=0.1, format="%.2f")

# Calculate the average torque
average_torque = (torque_1 + torque_2 + torque_3) / 3 if torque_1 and torque_2 and torque_3 else 0.0

# Display the average and validation
torque_status = "N/A"
if torque_1 and torque_2 and torque_3:
    st.write(f"**Average Torque: {average_torque:.2f} ft-lbs**")
    if average_torque >= torque_threshold:
        st.success("The average torque is acceptable.")
        torque_status = "Acceptable"
    else:
        st.error("The average torque is below the acceptable threshold of 8 ft-lbs.")
        torque_status = "Not Acceptable"

# Bottle batch code
bottle_code_legible = st.radio("Is the bottle coded with a legible batch code?", options=["Yes", "No"])
bottle_batch_code = ""
if bottle_code_legible == "Yes":
    bottle_batch_code = st.text_input("Enter the Bottle Batch Code")

# Case batch code
case_code_legible = st.radio("Is the case coded with a legible batch code?", options=["Yes", "No"])
case_batch_code = ""
if case_code_legible == "Yes":
    case_batch_code = st.text_input("Enter the Case Batch Code")

# Compare batch codes
if bottle_batch_code and case_batch_code:
    if bottle_batch_code == case_batch_code:
        st.success("The bottle and case batch codes match.")
    else:
        st.error("The bottle and case batch codes do not match. Notify the supervisor.")

# Submit button
submit = st.button("Submit Quality Check")

# Handle data submission
if submit:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    checkpoint_entry = {
        "timestamp": timestamp,
        "current_date": str(current_date),
        "sample_time": sample_time,
        "supervisor": supervisor,
        "production_line": production_line,
        "product": product,
        "target_fill_level": target_fill,
        "actual_fill_level": actual_fill_level,
        "fill_level_status": fill_level_status,
        "label_alignment": label_alignment,
        "torque_sample_1": torque_1,
        "torque_sample_2": torque_2,
        "torque_sample_3": torque_3,
        "average_torque": average_torque,
        "torque_status": torque_status,
        "bottle_batch_code": bottle_batch_code,
        "case_batch_code": case_batch_code,
        "batch_code_match": "Yes" if bottle_batch_code == case_batch_code else "No"
    }
    st.session_state["data"].append(checkpoint_entry)

    # Append data to Google Sheet
    sheet.append_row([
        checkpoint_entry["timestamp"], checkpoint_entry["current_date"], checkpoint_entry["sample_time"],
        checkpoint_entry["supervisor"], checkpoint_entry["production_line"], checkpoint_entry["product"],
        checkpoint_entry["target_fill_level"], checkpoint_entry["actual_fill_level"],
        checkpoint_entry["fill_level_status"], checkpoint_entry["label_alignment"],
        checkpoint_entry["torque_sample_1"], checkpoint_entry["torque_sample_2"], checkpoint_entry["torque_sample_3"],
        checkpoint_entry["average_torque"], checkpoint_entry["torque_status"],
        checkpoint_entry["bottle_batch_code"], checkpoint_entry["case_batch_code"],
        checkpoint_entry["batch_code_match"]
    ])
    
    st.success(f"Quality checkpoint submitted successfully!")

# Display submitted data
if st.session_state["data"]:
    st.header("Submitted Quality Checkpoints")
    st.dataframe(pd.DataFrame(st.session_state["data"]))
