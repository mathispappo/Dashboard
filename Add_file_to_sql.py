import os
import csv
from datetime import datetime
import pymysql


# Database connection
def connect_to_database():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='dataviz_m2_proj',
        charset='utf8mb4',
        autocommit=False  # Disable autocommit for better batch performance
    )


# Ensure the ListeningDetailed table exists in the database
def create_listening_table_if_not_exist():
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listening (
                    listening_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(150),
                    artist_name VARCHAR(150),
                    album_name VARCHAR(150),
                    song_name VARCHAR(150),
                    date_listened DATETIME,
                    UNIQUE KEY unique_listening (username, artist_name, album_name, song_name, date_listened)
                );
            """)
            connection.commit()
    finally:
        connection.close()


def integrate_csv_to_database(folder_path):
    """
    Process CSV files in a folder and integrate them into the database using batching for better performance.
    """
    # Ensure the folder path is valid
    folder_path = os.path.abspath(folder_path)
    if not os.path.exists(folder_path):
        print(f"Error: The folder path '{folder_path}' does not exist!")
        return

    connection = connect_to_database()

    try:
        with connection.cursor() as cursor:
            # Iterate over each file in the folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.csv'):
                    # Extract username from the filename (e.g., "username.csv")
                    username = os.path.splitext(filename)[0]

                    # Open and process the CSV file
                    file_path = os.path.join(folder_path, filename)
                    print(f"Processing file: {filename}")

                    # Prepare a batch insert list
                    batch_insert_data = []

                    with open(file_path, mode='r', encoding='utf-8') as csvfile:
                        csvreader = csv.reader(csvfile)

                        for row in csvreader:
                            if len(row) != 5:  # Ensure there are 5 columns in the row
                                print(f"Skipping invalid row: {row}")
                                continue

                            # Extract data from the row
                            username_from_file, artist_name, album_name, song_name, date_listened = row

                            # Ensure the username matches the filename
                            if username != username_from_file:
                                print(f"Skipping row with mismatched username. Expected {username}, found {username_from_file}")
                                continue

                            # Convert the date to the appropriate format
                            try:
                                date_obj = datetime.strptime(date_listened, "%d %b %Y %H:%M")
                                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                print(f"Skipping row with invalid date: {row}")
                                continue

                            # Append the row to the batch list
                            batch_insert_data.append((username, artist_name, album_name, song_name, formatted_date))

                    # Perform bulk insert for this file
                    if batch_insert_data:
                        try:
                            # Use INSERT IGNORE to skip duplicates
                            cursor.executemany("""
                                INSERT IGNORE INTO listening (username, artist_name, album_name, song_name, date_listened)
                                VALUES (%s, %s, %s, %s, %s);
                            """, batch_insert_data)
                            connection.commit()
                            print(f"Inserted {len(batch_insert_data)} rows from {filename} successfully.")
                        except Exception as e:
                            connection.rollback()
                            print(f"Error inserting data from {filename}: {e}")
                    else:
                        print(f"No valid data found in {filename}. Skipping file.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()


# Main execution
if __name__ == '__main__':
    # Path to the folder containing CSV files
    folder_path = './download'

    # Ensure table exists
    create_listening_table_if_not_exist()

    # Integrate CSV files
    integrate_csv_to_database(folder_path)
