import os
import csv
from datetime import datetime
import pymysql

# Database connection
def connect_to_database():
    return pymysql.connect(
        host='localhost:3306',
        user='user',
        password='root',
        database='dataviz_m2_proj',
        charset='utf8mb4',
    )

# Process CSV files in a folder and integrate them into the single table
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
                            artist_name, album_title, song_title, date_listened = row

                            # Convert the date to the appropriate format
                            date_obj = datetime.strptime(date_listened, "%d %b %Y %H:%M")
                            formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

                            # Insert the record into the ListeningDetailed table
                            cursor.execute(
                                """
                                INSERT INTO ListeningDetailed (username, artist_name, album_name, song_name, date_listened)
                                VALUES (%s, %s, %s, %s, %s)
                                """,
                                (username, artist_name, album_title, song_title, formatted_date)
                            )
                            connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

# Example usage
folder_path = 'data'  # Replace with the path to your folder containing CSV files
integrate_csv_to_database(folder_path)
