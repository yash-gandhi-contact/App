import pandas as pd
import streamlit as st

# Function to read the uploaded Excel file
def read_uploaded_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

# Function to clean data by ensuring consistent column data types
def clean_data(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            df[column] = df[column].replace('', pd.NA)
    return df

# Function to dynamically filter data based on user inputs
def filter_data(df, column, value):
    if value:
        return df[df[column].astype(str).str.contains(value, case=False, na=False)]
    return df

# Main function to create the Streamlit app
def main():
    # Add the logo to the sidebar
    logo_url = "https://www.eupd-research.com/wp-content/uploads/2019/09/Logo_EuPD_Research_RGB.png"
    st.sidebar.image(logo_url, width=200)  # Adjust the width as needed

    # Smaller title using markdown
    st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)

    # Upload file widget
    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        combined_df = read_uploaded_file(uploaded_file)
        cleaned_df = clean_data(combined_df)

        # Create a dropdown for ID prefixes if 'ID' column exists
        if 'ID' in cleaned_df.columns:
            cleaned_df['ID_prefix'] = cleaned_df['ID'].astype(str).str[:2]
            id_prefixes = cleaned_df['ID_prefix'].dropna().unique()
            selected_prefix = st.sidebar.selectbox("Select ID Prefix", options=['All'] + list(id_prefixes))
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

    else:
        st.info("Please upload an Excel file to get started.")

if __name__ == "__main__":
    main()
