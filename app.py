import streamlit as st
import pandas as pd
import base64
import pickle

# Load the ML model
model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))

# Download predictions as CSV
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Prediction logic
def build_model(input_data, load_data):
    prediction = model.predict(input_data)
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    chembl_id = pd.Series(load_data.iloc[:, 1], name='chembl_id')
    df = pd.concat([chembl_id, prediction_output], axis=1)
    df_sorted = df.sort_values(by='pIC50', ascending=False)
    st.write(df_sorted)
    st.markdown(filedownload(df_sorted), unsafe_allow_html=True)

# Streamlit App
st.markdown("# QSAR-based Drug Activity Prediction")

# Upload input compound file (.smi or .csv)
uploaded_file = st.sidebar.file_uploader("Step 1: Upload compound file (.smi or .csv)", type=['smi', 'txt', 'csv'])

# Upload descriptor file
uploaded_desc_file = st.sidebar.file_uploader("Step 2: Upload descriptor CSV (from PaDEL)", type=['csv'])

if st.sidebar.button('Predict'):
    if uploaded_file is not None and uploaded_desc_file is not None:
        # Display compound file
        if uploaded_file.name.endswith('.csv'):
            load_data = pd.read_csv(uploaded_file)
        else:
            load_data = pd.read_table(uploaded_file, sep=' ', header=None)

        st.header('**Original input data**')
        st.write(load_data)

        # Load descriptor CSV
        desc = pd.read_csv(uploaded_desc_file)
        st.header('**Uploaded molecular descriptors**')
        st.write(desc)
        st.write(desc.shape)

        # Subset selection
        st.header('**Subset of descriptors used by model**')
        Xlist = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[Xlist]
        st.write(desc_subset)
        st.write(desc_subset.shape)

        # Prediction
        build_model(desc_subset, load_data)
        
    else:
        st.error("Please upload both compound file and descriptor file.")
else:
    st.info("👈 Upload files to start prediction.")
