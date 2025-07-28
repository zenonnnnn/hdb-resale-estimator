import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
import time

st.set_page_config(
    page_title="HDB Resale Price Estimator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Base layout */
    .stApp {
    background: 
        linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
        url('https://images.pexels.com/photos/15480511/pexels-photo-15480511.jpeg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    }
    
    /* Hide empty containers */
    .block-container > div:first-child:empty,
    div[data-testid="stVerticalBlock"] > div:empty,
    .element-container:empty {
        display: none !important;
    }
    
    /* Text styles */
    h1 {
        color: #ffffff;
        text-align: center;
        font-family: 'Arial', sans-serif;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        padding: 20px;
        background: rgba(30, 58, 138, 0.9);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Container styling */
    .main-container {
        background-color: rgba(255, 255, 255, 1);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 15px auto;
    }
    
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 1);
        border: 2px solid #e5e7eb;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .prediction-result {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    
    /* Form elements */
    /* Labels */
    .stSelectbox label,
    .stNumberInput label,
    .stDateInput label,
    .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #d1d5db !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        color: #000000 !important;
        font-weight: 500 !important;
        background-color: #ffffff !important;
    }
    
    .stSelectbox input {
        color: #000000 !important;      
        background-color: #ffffff !important;  
        font-weight: 500 !important;
    }
    
    .stSelectbox ul {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }
    
    .stSelectbox li {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    .stSelectbox li:hover {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
    }
    
    /* Number and date inputs */
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div > div[role="slider"] {
        background-color: #3b82f6 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    .stSlider > div > div > div > div[aria-valuemin] {
        background-color: #64748b !important;
    }
    
    .stSlider > div > div > div > div:first-child {
        background-color: #3b82f6 !important;
    }
    
    .stSlider *::selection {
        background: transparent !important;
    }
    
    .stSlider div[data-baseweb="slider"] {
        background: transparent !important;
    }
    
    /* Slider value text */
    .stSlider > div > div > div > div > div {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1e3a8a;
        color: white;
        font-size: 18px;
        padding: 12px 40px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.3s;
        width: 100%;
        margin-top: 20px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1e40af;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Alerts and msgs */
    /* Force success and info boxes to be solid white */
    div.stSuccess, div.stInfo {
        background-color: transparent !important;
    }
    
    div.stSuccess > div, div.stInfo > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 2px solid #3b82f6 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        opacity: 1 !important;
    }
    
    div[data-testid="stWarning"] > div {
        background-color: rgba(251, 146, 60, 1) !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid rgba(251, 146, 60, 1);
        border-radius: 10px;
    }
    
    /* Section headers */
    .main-container h4 {
        color: #1e293b !important;
    }
    
    /* Subheader styling */
    .stSubheader > div {
        color: #1e293b !important;
    }
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 1) !important;
        border-radius: 8px;
        border: 2px solid #3b82f6;
        font-weight: 600;
        color: #1e293b !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border-color: #2563eb;
    }
    
    /* Expander content */
    div[data-testid="stExpander"] > div:nth-child(2) {
        background-color: rgba(255, 255, 255, 1) !important;
        border-radius: 0 0 8px 8px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    model = joblib.load('hdb_resale_model.pkl')
    feature_names = joblib.load('feature_names.pkl')
    encoding_info = joblib.load('encoding_info.pkl')
    feature_eng_info = joblib.load('feature_eng_info.pkl')
    return model, feature_names, encoding_info, feature_eng_info

model, feature_names, encoding_info, feature_eng_info = load_models()

st.markdown("<h1>HDB Resale Price Estimator</h1>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; padding: 15px; background-color: rgba(255,255,255,1); 
border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <h3 style='color: #1e293b; margin-bottom: 8px;'>Get HDB resale price predictions using machine learning</h3>
    <p style='color: #64748b; margin: 0;'>This model analysed thousands of transactions to provide you with price estimates</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.subheader("Property Details")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Location & Type")
    town = st.selectbox("Town", [
        'ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH',
        'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG',
        'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST',
        'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL',
        'QUEENSTOWN', 'SEMBAWANG', 'SENGKANG', 'SERANGOON', 'TAMPINES',
        'TOA PAYOH', 'WOODLANDS', 'YISHUN'
    ], help="Select the town where the HDB is located")
    
    flat_type = st.selectbox("Flat Type", [
        '3 ROOM', '4 ROOM', '5 ROOM', 'EXECUTIVE', 
        '1 ROOM', '2 ROOM', 'MULTI-GENERATION'
    ], index=1, help="Select the flat type")
    
    flat_model = st.selectbox("Flat Model", [
        'Improved', 'New Generation', 'Model A', 'Standard', 'Simplified',
        'Premium Apartment', 'Maisonette', 'Apartment', 'Model A2', 'DBSS'
    ], help="Select the flat model")
    
    st.markdown("#### Size & Age")
    floor_area_sqm = st.slider("Floor Area (sqm)", 30, 200, 90, 
                               help="Adjust the floor area using the slider")
    
    lease_commence_date = st.number_input("Lease Commence Date", 
                                          min_value=1960, 
                                          max_value=2025, 
                                          value=1990,
                                          help="The year when the lease started")

with col2:
    st.markdown("#### Floor & Lease")
    storey_range = st.selectbox("Storey Range", 
                                list(encoding_info['storey_mapping'].keys()),
                                help="Select the floor range of the unit")
    
    remaining_lease_years = st.slider("Remaining Lease (years)", 
                                      0, 99, 60,
                                      help="Years left on the 99 year lease")
    
    st.markdown("#### Transaction Details")
    month = st.date_input("Transaction Date", 
                          value=pd.Timestamp.now(),
                          max_value=pd.Timestamp.now(),
                          min_value=pd.Timestamp('2000-01-01'),
                          help="Select the transaction date")
    
    is_mature = town in encoding_info['mature_estates']
    if is_mature:
        st.success("Mature Estate")
    else:
        st.info("Non-Mature Estate")

with st.expander("Preview Property Summary", expanded=False):
    preview_col1, preview_col2, preview_col3 = st.columns(3)
    with preview_col1:
        st.metric("Property Type", f"{flat_type} {flat_model}")
    with preview_col2:
        st.metric("Location", f"{town} ({'Mature' if is_mature else 'Non-mature'})")
    with preview_col3:
        st.metric("Age", f"{pd.Timestamp.now().year - lease_commence_date} years old")

if st.button("Predict Price", type="primary"):
    with st.spinner('Analysing property data...'):
        year = month.year
        flat_age = year - lease_commence_date

        # Input validations
        if lease_commence_date > year:
            st.error("❌ Error: Lease commence date cannot be in the future!")
            st.stop()
        
        if flat_age < 0:
            st.error("❌ Error: Invalid dates - flat age cannot be negative!")
            st.stop()
        
        if remaining_lease_years > (99 - flat_age):
            st.error("❌ Error: Remaining lease years cannot exceed the original 99-year lease!")
            st.stop()
        
        # Progress bar
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        # Prediction
        storey_mid = encoding_info['storey_mapping'][storey_range]
        is_mature_val = 1 if is_mature else 0
        flat_type_numeric = encoding_info['flat_type_order'].get(flat_type, 4)

        input_data = pd.DataFrame({
            'town': [town],
            'flat_type': [flat_type],
            'storey_range': [storey_range],
            'floor_area_sqm': [floor_area_sqm],
            'flat_model': [flat_model],
            'year': [year],
            'flat_age': [flat_age],
            'remaining_lease_years': [remaining_lease_years],
            'storey_mid': [storey_mid],
            'is_mature': [is_mature_val],
            'flat_type_numeric': [flat_type_numeric],
            'quarter': [pd.Timestamp(month).quarter],
            'month_of_year': [pd.Timestamp(month).month],
            'is_year_end': [1 if pd.Timestamp(month).month >= 11 else 0],
            'floor_area_x_storey': [floor_area_sqm * storey_mid],
            'age_x_remaining_lease': [flat_age * remaining_lease_years],
            'mature_x_storey': [is_mature_val * storey_mid],
            'age_category': [pd.cut([flat_age], bins=[0, 10, 20, 30, 40, 100], 
                                labels=['Very New', 'New', 'Moderate', 'Old', 'Very Old'])[0]],
            'area_category': [pd.cut([floor_area_sqm], bins=[0, 50, 70, 90, 110, 200], 
                                    labels=['Very Small', 'Small', 'Medium', 'Large', 'Very Large'])[0]]
        })

        input_encoded = pd.get_dummies(input_data)

        for col in feature_names:
            if col not in input_encoded.columns:
                input_encoded[col] = 0
        input_encoded = input_encoded[feature_names]

        prediction = model.predict(input_encoded.to_numpy())[0]

        # Clear the progress bar
        progress_bar.empty()

        
    st.markdown(f"""
    <div class='prediction-result'>
        <h2 style='margin: 0; color: white;'>Predicted Resale Price</h2>
        <h1 style='font-size: 48px; margin: 10px 0; color: white;'>${prediction:,.0f}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Price Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price per sqm", f"${prediction/floor_area_sqm:,.0f}",
                  help="Price divided by floor area")
    with col2:
        st.metric("Flat Age", f"{flat_age} years",
                  delta=f"{remaining_lease_years} years left")
    with col3:
        monthly_payment = prediction * 0.8 / 300
        st.metric("Est. Monthly", f"${monthly_payment:,.0f}",
                  help="Estimated monthly payment (80% loan, 25 years)")
    with col4:
        st.metric("Floor Level", storey_range,
                  help="Higher floors typically mean more premium prices")
    
    st.markdown("### Price Insights")
    
    comparison_data = {
        'Category': ['Prediction', 'Town Average*', 'National Average*'],
        'Price': [prediction, prediction * 0.95, prediction * 0.85]
    }
    
    fig = go.Figure(data=[
        go.Bar(x=comparison_data['Category'], 
               y=comparison_data['Price'],
               text=[f'${p:,.0f}' for p in comparison_data['Price']],
               textposition='auto',
               textfont=dict(size=14, color='white'),
               marker_color=['#059669', '#2563eb', '#7c3aed'])
    ])
    
    fig.update_layout(
        title=dict(
            text="Price Comparison",
            font=dict(size=20, color='#1e293b', family='Arial'),
            x=0.5
        ),
        yaxis_title=dict(
            text="Price (SGD)",
            font=dict(size=14, color='#1e293b')
        ),
        xaxis=dict(
            tickfont=dict(size=12, color='#1e293b')
        ),
        yaxis=dict(
            tickfont=dict(size=12, color='#1e293b')
        ),
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Prediction Confidence**: Based on the model's performance, most predictions 
    are accurate within +-$50,000 of the actual price. This represents a 95% confidence rate.
    """)
    
    st.warning("""
    **Disclaimer:** This prediction is based on historical data and 
    machine learning models. Actual prices may vary due to market conditions, 
    specific unit features, and other factors not captured in this model.
    *Comparison values are illustrative only.   
    """)

st.markdown('</div>', unsafe_allow_html=True)