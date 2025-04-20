import streamlit as st
import pandas as pd
import pickle
import base64

# Load trained ML model
model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))

# Load selected descriptors list (top 115 features)
Xlist = list(pd.read_csv('descriptor_list.csv').columns)

# Download link for predictions
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">Download Predictions</a>'
    return href

# Predict function
def predict_from_descriptors(desc_df, ids_df):
    desc_subset = desc_df[Xlist]
    predictions = model.predict(desc_subset)
    results = pd.DataFrame({
        'ChEMBL_ID': ids_df.iloc[:, 1],  # assumes ChEMBL ID is in second column
        'Predicted_pIC50': predictions
    })
    results_sorted = results.sort_values(by='Predicted_pIC50', ascending=False)
    return results_sorted

# UI starts here
st.title('QSAR-based Bioactivity Prediction App')

st.markdown("""
Upload:
1. `.smi` or `.txt` file containing **Canonical SMILES and ChEMBL ID**
2. Corresponding **descriptor CSV file** (calculated using PaDEL)
""")

uploaded_smi_file = st.file_uploader("Upload compound file (.smi or .txt)", type=['smi', 'txt'])
uploaded_desc_file = st.file_uploader("Upload descriptor file (CSV from PaDEL)", type=['csv'])

if st.button('Run Prediction'):
    if uploaded_smi_file is not None and uploaded_desc_file is not None:
        # Load and display compound data
        smiles_df = pd.read_table(uploaded_smi_file, sep=r'\s+', header=None)
        smiles_df.columns = ['SMILES', 'ChEMBL_ID']
        st.subheader('📄 Uploaded Compound Data')
        st.write(smiles_df)

        # Load and display descriptor file
        desc_df = pd.read_csv(uploaded_desc_file)
        st.subheader('🧪 Uploaded Molecular Descriptors')
        st.write(desc_df)
        st.write(f'Descriptors shape: {desc_df.shape}')

        # Validate that required descriptors are present
        missing_cols = [col for col in Xlist if col not in desc_df.columns]
        if missing_cols:
            st.error(f"Descriptor file is missing required columns: {missing_cols}")
        else:
            # Run prediction
            st.subheader('🔬 Prediction Results')
            results_df = predict_from_descriptors(desc_df, smiles_df)
            st.write(results_df)
            st.markdown(filedownload(results_df), unsafe_allow_html=True)
    else:
        st.warning("Please upload both compound and descriptor files.")
else:
    st.info("⬅️ Upload files and click 'Run Prediction'")
