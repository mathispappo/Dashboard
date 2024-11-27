import csv
import os


def ensure_directory_exists(directory):
    """
    Ensure the given directory exists. If not, create it.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")


def add_username_column_to_csv(file_path, output_directory):
    """
    Process a CSV file to add a 'username' column and ensure all required columns are present.
    Save the processed file to the output directory.
    """
    try:
        # Extract the username from the filename (excluding the extension)
        username = os.path.splitext(os.path.basename(file_path))[0]

        # Define the expected headers
        expected_headers = ['username', 'artist', 'album', 'song', 'date']

        # Ensure the output directory exists before attempting to save the file
        ensure_directory_exists(output_directory)

        # Prepare the output file path (same filename, but in the output directory)
        output_file_path = os.path.join(output_directory, os.path.basename(file_path))

        # Open the original file and the output file
        with open(file_path, mode='r', encoding='utf-8') as infile, open(output_file_path, mode='w', encoding='utf-8', newline='') as outfile:
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)

            # Write the headers to the output file
            csv_writer.writerow(expected_headers)

            # Iterate over the rows and modify them
            for row in csv_reader:
                # If row has missing columns, add empty values for missing ones
                while len(row) < len(expected_headers) - 1:  # Exclude 'username'
                    row.append('')  # Fill missing values with empty strings

                # Prepend the username to the row
                row = [username] + row[:len(expected_headers) - 1]

                # Write the updated row to the output file
                csv_writer.writerow(row)

        print(f"File processed: {file_path}, saved to: {output_file_path}")

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")


def process_all_files_in_directory(input_directory, output_directory):
    """
    Process all CSV files in the input directory and save the results to the output directory.
    """
    # Ensure the output directory exists
    ensure_directory_exists(output_directory)

    # Iterate over all files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):  # Process only CSV files
            file_path = os.path.join(input_directory, filename)
            print(f"Processing file: {file_path}")

            # Process the file and save the result to the output directory
            add_username_column_to_csv(file_path, output_directory)


if __name__ == '__main__':
    # Define the input and output directories (relative to the script's location)
    input_directory = os.path.join(os.path.dirname(__file__), 'data')  # Folder containing input files
    output_directory = os.path.join(os.path.dirname(__file__), 'download')  # Folder to store processed files

    # Process all files in the input directory
    process_all_files_in_directory(input_directory, output_directory)

    print(f"All files processed. Processed files are saved in the '{output_directory}' directory.")
