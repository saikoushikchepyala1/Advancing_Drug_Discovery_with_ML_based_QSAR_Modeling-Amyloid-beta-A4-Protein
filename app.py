import streamlit as st
import pandas as pd
import pickle
import subprocess
import base64
import os

# Load model and descriptor list
model = pickle.load(open('bioactivity_prediction_model.pkl', 'rb'))
descriptor_list = list(pd.read_csv('descriptor_list.csv').columns)

# File download utility
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">Download Predictions</a>'

# Descriptor calculation using PaDEL
def calculate_descriptors():
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

# Streamlit UI
st.title("QSAR-Based Bioactivity Prediction (pIC50)")

# Upload file
uploaded_file = st.file_uploader("Upload .smi or .txt file (SMILES + ChEMBL ID)", type=['smi', 'txt'])

if uploaded_file is not None:
    # Read uploaded SMILES file
    smiles_df = pd.read_table(uploaded_file, sep=r"\s+", header=None)
    smiles_df.columns = ["SMILES", "ChEMBL_ID"]
    st.subheader("📄 Uploaded Compound Data")
    st.write(smiles_df)

    # Save for PaDEL
    smiles_df.to_csv("input_molecule.smi", sep="\t", header=False, index=False)

    with st.spinner("🧬 Calculating molecular descriptors using PaDEL..."):
        calculate_descriptors()
        st.success("Descriptor calculation complete!")

    # Load descriptors
    desc_df = pd.read_csv("descriptors_output.csv")
    st.subheader("🧪 Calculated Molecular Descriptors")
    st.write(desc_df)

    # Check required descriptors
    missing_cols = [col for col in descriptor_list if col not in desc_df.columns]
    if missing_cols:
        st.error(f"Missing descriptors: {missing_cols}")
        st.stop()

    # Predict pIC50
    desc_subset = desc_df[descriptor_list]
    predictions = model.predict(desc_subset)

    # Combine and display results
    results_df = pd.DataFrame({
        "ChEMBL_ID": smiles_df["ChEMBL_ID"],
        "Predicted_pIC50": predictions
    }).sort_values(by="Predicted_pIC50", ascending=False)

    st.subheader("🔬 Prediction Results")
    st.write(results_df)

    st.markdown(filedownload(results_df), unsafe_allow_html=True)

    # Clean up temp files
    os.remove("input_molecule.smi")
    os.remove("descriptors_output.csv")
else:
    st.info("⬅️ Upload a compound file to begin.")
