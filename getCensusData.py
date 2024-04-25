import pandas as pd
import requests

# Paths to data files
output_file_path = './data/us_census_data.xlsx'

# Get API key from user input
# api_key = input("Please enter your US Census API key: ")

# URL of the API
url = 'https://api.census.gov/data/2022/acs/acs5?get=NAME,B01001_001E,B01001_026E,B01002_001E,B17001_001E,B27001_001E,B25064_001E,B25077_001E,B25035_001E,B19013_001E&for=place:*&in=state:*'

# Make the API call
response = requests.get(url)
data = response.json()  # Assuming the response is in JSON format that matches the example you provided

# Create DataFrame using the first element for column headers, and the rest for data
df = pd.DataFrame(data[1:], columns=data[0])

# Define a dictionary with old and new column names
new_column_names = {
    "NAME": "Location",
    "B01001_001E": "Population",
    "B01001_026E": "Total_population_Female",
    "B01002_001E": "Median_age",
    "B17001_001E": "Poverty_status",
    "B27001_001E": "Health_insurance_coverage",
    "B25064_001E": "Median_gross_rent",
    "B25077_001E": "Median_value_owned_housing_ units",
    "B25035_001E": "Median_year_housing_units_age",
    "B19013_001E": "Median_household_income"
}

# Rename the columns
df.rename(columns=new_column_names, inplace=True)

df['Population'] = pd.to_numeric(df['Population'])
df['Total_population_Female'] = pd.to_numeric(df['Total_population_Female'])
df['Median_age'] = pd.to_numeric(df['Median_age'])
df['Poverty_ status'] = pd.to_numeric(df['Poverty_ status'])
df['Health_insurance_coverage'] = pd.to_numeric(df['Health_insurance_coverage'])
df['Median_gross_rent'] = pd.to_numeric(df['Median_gross_rent'])
df['Median_value_owned_housing_ units'] = pd.to_numeric(df['Median_value_owned_housing_ units'])
df['Median_year_housing_units_age'] = pd.to_numeric(df['Median_year_housing_units_age'])
df['Median_household_income'] = pd.to_numeric(df['Median_household_income'])

# Filter the DataFrame to include only rows where 'Population' is greater than 20000
filtered_df = df[df['Population'] > 20000]

# Calculate percentage of the Population
filtered_df['Total_population_Female'] = (filtered_df['Total_population_Female'] / filtered_df['Population']) * 100
filtered_df['Poverty_status'] = (filtered_df['Poverty_status'] / filtered_df['Population']) * 100
filtered_df['Health_insurance_coverage'] = (filtered_df['Health_insurance_coverage'] / filtered_df['Population']) * 100

# Export the DataFrame to an Excel file
filtered_df.to_excel(output_file_path, index=False, engine='openpyxl')

print("DataFrame has been exported to Excel file successfully.")
