import streamlit as st
import pandas as pd
from PIL import Image
import base64
import pickle

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

def build_model(input_data, chembl_ids):
    load_model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))
    prediction = load_model.predict(input_data)
    
    st.header('**Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    chembl_id = pd.Series(chembl_ids, name='chembl_id') 
    df = pd.concat([chembl_id, prediction_output], axis=1)
    
    df_sorted = df.sort_values(by='pIC50', ascending=False)
    st.write(df_sorted)
    st.markdown(filedownload(df_sorted), unsafe_allow_html=True)

# App title
st.markdown("# Compounds Bioactivity Prediction")

# File upload
with st.sidebar.header('1. Upload descriptor CSV file'):
    uploaded_file = st.sidebar.file_uploader("Upload descriptor file (CSV)", type=['csv'])

# On click predict
if st.sidebar.button('Predict'):
    if uploaded_file is not None:
        desc = pd.read_csv(uploaded_file)

        st.header('**Uploaded Descriptor Data**')
        st.write(desc)
        st.write(desc.shape)

        # Subset descriptors
        st.header('**Subset of descriptors from previously built model**')
        Xlist = list(pd.read_csv('descriptor_list.csv').columns)
        desc_subset = desc[Xlist]
        st.write(desc_subset)
        st.write(desc_subset.shape)

        # Get chembl_id if available
        chembl_ids = desc.iloc[:, 0] if 'chembl_id' in desc.columns[0].lower() else pd.Series(range(len(desc)))
        
        build_model(desc_subset, chembl_ids)
    else:
        st.error("Please upload a CSV file to proceed.")
else:
    st.info("Upload precomputed molecular descriptor CSV to begin.")
