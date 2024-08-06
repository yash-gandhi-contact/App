import pandas as pd
import os
import streamlit as st

# Function to read and combine all Excel files into a single DataFrame
def read_excel_files(folder_path):
    dataframes = []
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path)
            dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

# Function to clean data by ensuring consistent column data types
def clean_data(df):
    # Ensure NaN values are preserved and no conversion is done for non-numeric columns
    for column in df.columns:
        if df[column].dtype == 'object':
            # Replace empty strings with NaN
            df[column] = df[column].replace('', pd.NA)
    return df

# Function to dynamically filter data based on user inputs
def filter_data(df, column, value):
    if value:
        # Use str.contains with na=False to handle NaNs correctly
        return df[df[column].astype(str).str.contains(value, case=False, na=False)]
    return df

# Main function to create the Streamlit app
def main():
    # Add the logo to the sidebar
    logo_url = "https://www.eupd-research.com/wp-content/uploads/2019/09/Logo_EuPD_Research_RGB.png"
    st.sidebar.image(logo_url, width=200)  # Adjust the width as needed

    # Smaller title using markdown
    st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)

    folder_path = 'Z:/EUPD/EUPD_Energy/03_Colleagues/Yash/file'  
    combined_df = read_excel_files(folder_path)
    cleaned_df = clean_data(combined_df)

    # Create a dropdown for ID prefixes if 'ID' column exists
    if 'ID' in cleaned_df.columns:
        # Extract the first two characters of each ID
        cleaned_df['ID_prefix'] = cleaned_df['ID'].astype(str).str[:2]
        
        # Get unique prefixes for dropdown
        id_prefixes = cleaned_df['ID_prefix'].dropna().unique()
        
        # Add a dropdown to the sidebar
        selected_prefix = st.sidebar.selectbox("Select ID Prefix", options=['All'] + list(id_prefixes))

        # Filter the DataFrame based on the selected prefix
        if selected_prefix != 'All':
            cleaned_df = cleaned_df[cleaned_df['ID_prefix'] == selected_prefix]

    st.sidebar.title("Filter Options")

    # Dropdown to select which column to filter
    column_to_filter = st.sidebar.selectbox("Select Column to Filter", options=['None'] + list(cleaned_df.columns))

    # Show filter input only if a valid column is selected
    if column_to_filter != 'None':
        filter_value = st.sidebar.text_input(f"Filter {column_to_filter}", key=f"filter_{column_to_filter}")
        filtered_data = filter_data(cleaned_df, column_to_filter, filter_value)
    else:
        filtered_data = cleaned_df

    # Display the filtered data in full-screen and styled
    st.subheader("Filtered Data")

    # Use st.dataframe with some additional styling
    st.dataframe(filtered_data, use_container_width=True)

    # Additional styling with CSS
    st.markdown("""
        <style>
        .dataframe tbody tr:hover {
            background-color: #f5f5f5;
        }
        .dataframe thead th {
            background-color: #007bff;
            color: white;
        }
        .dataframe td, .dataframe th {
            text-align: center;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
