import csv

def validate_csv_columns(file):
    """
    Validates that the CSV file has exactly 4 columns.
    Reads the first row to check the number of columns.
    """
    file.seek(0)
    csv_reader = csv.reader(file.read().decode('utf-8').splitlines())

    try:
        first_row = next(csv_reader)  # Read the first row
        return len(first_row) == 4
    except Exception as e:
        return False

