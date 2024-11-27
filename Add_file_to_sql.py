import os
import csv
from datetime import datetime
import pymysql


# Database connection
def connect_to_database():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='', # Change to your password
        database='dataviz_m2_proj',
        charset='utf8mb4',
    )


# Ensure the ListeningDetailed table exists in the database
def create_listening_table_if_not_exist():
    connection = connect_to_database()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS listening (
                    listening_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(250),
                    artist_name VARCHAR(1000),
                    album_name VARCHAR(250),
                    song_name VARCHAR(250),
                    date_listened DATETIME
                );
            """)
            connection.commit()
    finally:
        connection.close()


# Process CSV files in a folder and integrate them into the ListeningDetailed table
def integrate_csv_to_database(folder_path):
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
                    with open(file_path, mode='r', encoding='utf-8') as csvfile:
                        csvreader = csv.reader(csvfile)

                        for row in csvreader:
                            if len(row) != 5:  # Ensure there are 5 columns in the row
                                print(f"Skipping invalid row: {row}")
                                continue

                            # Extract data from the row
                            username_from_file, artist_name, album_title, song_title, date_listened = row

                            # Ensure the username matches the filename
                            if username != username_from_file:
                                print(
                                    f"Skipping row with mismatched username. Expected {username}, found {username_from_file}")
                                continue

                            # Convert the date to the appropriate format
                            try:
                                date_obj = datetime.strptime(date_listened, "%d %b %Y %H:%M")
                                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # If the date format is invalid, skip this row
                                print(f"Skipping row with invalid date: {row}")
                                continue

                            # Check if the listening record already exists in ListeningDetailed table
                            cursor.execute("""
                                SELECT * FROM listening 
                                WHERE username = %s AND artist_name = %s AND album_name = %s AND song_name = %s AND date_listened = %s
                            """, (username, artist_name, album_title, song_title, formatted_date))

                            if not cursor.fetchone():  # If no record exists, insert it
                                cursor.execute("""
                                    INSERT INTO listening (username, artist_name, album_name, song_name, date_listened)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (username, artist_name, album_title, song_title, formatted_date))
                                connection.commit()
                            else:
                                print(
                                    f"Skipping duplicate listening entry for {username}, {song_title}, {formatted_date}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()


# Example usage
folder_path = '/Users/mathispappo/Documents/Applications-of-Big-Data/DataViz/Dashboard/data'  # Replace with the path to your folder containing CSV files
create_listening_table_if_not_exist()  # Ensure the table exists before integrating data
integrate_csv_to_database(folder_path)
