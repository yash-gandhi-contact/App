import pandas as pd
import streamlit as st
import re

# Function to read and combine all uploaded Excel files into a single DataFrame
def read_excel_files(uploaded_files):
    dataframes = []
    for uploaded_file in uploaded_files:
        df = pd.read_excel(uploaded_file)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

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

# Function to extract first two alphabetic characters from ID
def extract_alphabetic_prefix(id_value):
    # Extract only alphabetic characters
    letters = re.findall(r'[A-Za-z]', str(id_value))
    # Return the first two alphabetic characters
    return ''.join(letters[:2]).upper()

# Function to update entries based on primary key ID, with option to replace with empty values
def update_entries(old_df, latest_df, replace_with_empty=False):
    # Ensure 'ID' column is in both DataFrames
    if 'ID' not in old_df.columns or 'ID' not in latest_df.columns:
        st.error("Both files must contain an 'ID' column to perform updates.")
        return old_df

    # Set 'ID' as the index for easier comparison
    old_df.set_index('ID', inplace=True)
    latest_df.set_index('ID', inplace=True)

    # Update old_df with latest_df's data where IDs match
    for column in latest_df.columns:
        if replace_with_empty:
            # Update even if the new value is None (NaN)
            old_df[column] = latest_df[column].combine_first(old_df[column])
        else:
            # Update only non-NA values
            old_df[column].update(latest_df[column])

    # Combine dataframes to include new entries from latest_df
    updated_df = latest_df.combine_first(old_df)

    # Reset index to bring 'ID' back as a column
    updated_df.reset_index(inplace=True)

    return updated_df

# Function to render the data query dashboard
def render_data_query_dashboard():
    # Upload multiple files
    uploaded_files = st.sidebar.file_uploader("Upload your Excel files", type=['xlsx', 'xls'], accept_multiple_files=True)

    if uploaded_files:
        combined_df = read_excel_files(uploaded_files)
        cleaned_df = clean_data(combined_df)

        # Create a dropdown for ID prefixes if 'ID' column exists
        if 'ID' in cleaned_df.columns:
            cleaned_df['ID_prefix'] = cleaned_df['ID'].apply(extract_alphabetic_prefix)
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
        st.info("Please upload one or more Excel files to get started.")

# Function to render the update entries page
def render_update_entries_page():
    st.sidebar.header("Update Entries")

    # Upload files for the old and latest Excel
    old_excel = st.sidebar.file_uploader("Upload Old Excel", type=['xlsx', 'xls'], key='old_excel')
    latest_excel = st.sidebar.file_uploader("Upload Latest Excel", type=['xlsx', 'xls'], key='latest_excel')

    # Radio button for replace with empty values option
    replace_option = st.sidebar.radio(
        "Replace with empty values",
        ("Do not replace with empty values", "Replace with empty values"),
        index=0
    )

    # Determine if replacement should occur
    replace_with_empty = replace_option == "Replace with empty values"

    # Display information if both files are uploaded
    if old_excel and latest_excel:
        old_df = pd.read_excel(old_excel)
        latest_df = pd.read_excel(latest_excel)

        # Update entries in old_df based on latest_df
        updated_df = update_entries(old_df, latest_df, replace_with_empty=replace_with_empty)

        st.subheader("Updated Data")
        st.dataframe(updated_df, use_container_width=True)

        # Option to download the updated DataFrame as an Excel file
        download_excel(updated_df, "updated_data.xlsx")

    elif not old_excel:
        st.info("Please upload the Old Excel file.")
    elif not latest_excel:
        st.info("Please upload the Latest Excel file.")

# Function to download a DataFrame as an Excel file
def download_excel(df, file_name):
    import io

    # Use a BytesIO buffer instead of writing to disk
    buffer = io.BytesIO()

    # Write the DataFrame to an Excel file using the buffer
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Updated Data')

    # Get the Excel data from the buffer
    buffer.seek(0)
    
    st.download_button(
        label="Download Updated Excel",
        data=buffer,
        file_name=file_name,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# Main function to create the Streamlit app
def main():
    # Add the logo to the sidebar
    logo_url = "https://www.eupd-research.com/wp-content/uploads/2019/09/Logo_EuPD_Research_RGB.png"
    st.sidebar.image(logo_url, width=200)  # Adjust the width as needed

    # Sidebar navigation for multiple pages
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio("Go to", ["Dynamic Excel Data Query", "Update Entries"])

    # Render the selected page
    if page_selection == "Dynamic Excel Data Query":
        # Smaller title using markdown
        st.markdown("<h2 style='text-align: center;'>Dynamic Excel Data Query Dashboard</h2>", unsafe_allow_html=True)
        render_data_query_dashboard()
    elif page_selection == "Update Entries":
        st.markdown("<h2 style='text-align: center;'>Update Entries</h2>", unsafe_allow_html=True)
        render_update_entries_page()

if __name__ == "__main__":
    main()
