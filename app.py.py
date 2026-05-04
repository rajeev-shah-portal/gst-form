import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- DATABASE LOGIC ---
# This matches your setup: Folder 'leads.db' and file 'lead'
DB_PATH = os.path.join("leads.db", "lead")

def init_db():
    # Create the folder if it doesn't exist (safety check)
    if not os.path.exists("leads.db"):
        os.makedirs("leads.db")
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Your internal "sheet" name is 'lead_table'
    c.execute('''CREATE TABLE IF NOT EXISTS lead_table 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp DATETIME, name TEXT, phone TEXT, 
                  gstin TEXT, company TEXT, email TEXT)''')
    conn.commit()
    conn.close()

def save_lead(name, phone, gstin, company, email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO lead_table (timestamp, name, phone, gstin, company, email) VALUES (?,?,?,?,?,?)",
              (now, name, phone, gstin, company, email))
    conn.commit()
    conn.close()

# --- UI STYLING ---
st.set_page_config(page_title="GST Lead Portal", layout="centered")
init_db()

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; }
    .card { background: white; padding: 2rem; border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Submit Lead", "Admin Dashboard"])

if menu == "Submit Lead":
    st.title("Check your eligibility")
    st.write("Enter your details to get started.")
    
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        name = st.text_input("Name *")
        phone = st.text_input("Phone Number *")
        gst = st.text_input("GST Number *")
        
        # Mock verification for the "Company Name" field
        company_val = ""
        if len(gst) == 15:
            company_val = "Verified Business Name" # Replace with real API later
            st.success(f"✅ Verified: {company_val}")

        company = st.text_input("Company Name *", value=company_val)
        email = st.text_input("Email *")
        
        if st.button("Submit Details"):
            if name and phone and gst:
                save_lead(name, phone, gst, company, email)
                st.balloons()
                st.success("Registration Successful!")
            else:
                st.error("Please fill Name, Phone, and GST.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Admin Dashboard":
    st.title("📂 Download Your Leads")
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM lead_table", conn)
        conn.close()

        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            st.subheader("📅 Select Date Range for Download")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From", df['timestamp'].min())
            with col2:
                end_date = st.date_input("To", df['timestamp'].max())
            
            # Filter logic
            mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
            filtered_df = df.loc[mask]

            st.write(f"Total Leads Found: {len(filtered_df)}")
            st.dataframe(filtered_df, use_container_width=True)

            # Download Button
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data as Excel (CSV)",
                data=csv,
                file_name=f"GST_Leads_{start_date}_to_{end_date}.csv",
                mime="text/csv",
            )
        else:
            st.info("The lead file is empty. Start collecting leads!")
    else:
        st.error("The 'lead' file was not found in the 'leads.db' folder.")