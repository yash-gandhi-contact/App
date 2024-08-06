import os
import pandas as pd
import streamlit as st

# Function to validate the file path
def is_valid_file_path(file_path, allowed_path_prefix):
    return file_path.startswith(allowed_path_prefix)

# Function to read and combine all Excel files into a single DataFrame
def read_excel_files_from_path(folder_path):
    dataframes = []
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path)
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

# Function to read uploaded file
def read_uploaded_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

# Main function to create the Streamlit app
def main():
    st.title("Dynamic Excel Data Query Dashboard")

    # Specify the allowed path prefix
    allowed_path_prefix = "Z:/EUPD/EUPD_Energy/03_Colleagues/Yash/file"
    
    # Option for users to upload file
    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        # Check if the uploaded file path matches the allowed path
        if is_valid_file_path(uploaded_file.name, allowed_path_prefix):
            combined_df = read_uploaded_file(uploaded_file)
            cleaned_df = clean_data(combined_df)

            st.write("Filtered Data", cleaned_df)
        else:
            st.error("The file must be from the specified path.")
    else:
        st.info("Please upload an Excel file.")

if __name__ == "__main__":
    main()
