import pandas as pd

def text_to_excel(input_filename, output_filename):
    # Read the text file using pandas, specifying the delimiter
    df = pd.read_csv(input_filename, delimiter='|')
    
    # Export the DataFrame to an Excel file
    df.to_excel(output_filename, index=False)

# Example usage
text_to_excel('./data/place_by_county2020.txt', './data/place_by_county2020.xlsx')