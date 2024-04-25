import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_place_details(place_id, api_key):
    # Fetches place details for a given Place ID
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'website',
        'key': api_key
    }
    response = requests.get(details_url, params=params)
    details_data = response.json()

    if details_data.get('status') == 'OK':
        website = details_data['result'].get('website', 'No website provided')
    else:
        website = "No website provided"
    return website

def check_website(url):
    # Check if the website is online and returns a 404 status code.
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 404:
            return 1
    except requests.RequestException:
        return 1  # Assume 404 if the website is unreachable
    return 0

def find_cold_plunge(url):
    try:
        print("checking ", url)
        # Fetch the content of the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Convert the parsed HTML to text and search for keywords
        text = soup.get_text().lower()  # Convert to lower case to make the search case-insensitive
        keywords = ['cold plunge', 'ice bath', 'cold therapy', 'cryotherapy']

        # Check if any keyword is in the text
        for keyword in keywords:
            if keyword in text:
                return True  # Return True if any keyword is found

        return False  # Return False if no keywords are found

    except requests.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return False

# Paths to data files
input_file_path = './data/pop_data.xlsx'
output_file_path_api = './data/api_response_data.xlsx'
output_file_path_biz_pop = './data/biz_pop_data.xlsx'

# Read the Excel file into a pandas DataFrame.
df = pd.read_excel(input_file_path)

# Add a new column 'Biz Count' initialized with zeros
df['Biz Count'] = 0

# Initialize an empty DataFrame to store the total results
total_results = pd.DataFrame()

# Get API key from user input
api_key = input("Please enter your API key: ")


# Loop through each row in the DataFrame
for index, row in df.iterrows():

    print("----------Checking: ",row['City'], row['State Abbr'])
    # Construct the query using the 'City' and 'State Abbr' columns
    query = f"cold plunge in {row['City']} {row['State Abbr']}"

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'key': api_key
    }

    response = requests.get(url, params=params, timeout=5)
    results = response.json()

    # Check if the API call was successful
    if results.get('status') == 'OK':
        places = results.get('results', [])

        # Extract relevant data
        data = []
        for place in places:
            name = place.get('name')
            place_id = place.get('place_id')
            website = get_place_details(place_id, api_key)
            is_404 = check_website(website) if website else 1  # Check if the website returns a 404
            
            if(is_404 == 0):        
                is_cold_plunge = find_cold_plunge(website)
            else:
                is_cold_plunge = 0

            data.append({
                'PLACEFP': row['PLACEFP'],
                'Name': name,
                'Place ID': place_id,
                'Website': website,
                '404 Error': is_404,
                'Cold Plunge': is_cold_plunge
            })

        # Create a DataFrame
        results_df = pd.DataFrame(data)

        # Filter out rows where 'Cold Plunge' column is False
        filtered_df = results_df[results_df['Cold Plunge'] != False]
       
        # After filtering, concatenate the results to the total_results DataFrame
        total_results = pd.concat([total_results, filtered_df], ignore_index=True)

        # Count the number of results in filtered_df
        biz_count = len(filtered_df)

        # Add this count to the 'Biz Count' column of the df for the current row
        df.at[index, 'Biz Count'] = biz_count

    else:
        print("Failed to fetch data: ", results.get('status'))

    # Write only the new filtered data to the 'api_response_data.xlsx' after each iteration
    if index == 0:
        # Write with header only on the first iteration
        filtered_df.to_excel(output_file_path_api, index=False)
    else:
        # Append without header for subsequent iterations
        with pd.ExcelWriter(output_file_path_api, mode='a', if_sheet_exists='overlay', engine="openpyxl") as writer:
            filtered_df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

# Write the final 'df' DataFrame with Biz Counts to 'biz_pop_data.xlsx' once after all iterations are complete
df.to_excel(output_file_path_biz_pop, index=False)

