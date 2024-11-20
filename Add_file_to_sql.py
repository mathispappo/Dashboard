import os
import csv
from datetime import datetime
import pymysql

# Database connection
def connect_to_database():
    return pymysql.connect(
        host='localhost',
        user='your_username',
        password='your_password',
        database='your_database',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


# Process CSV files in a folder and integrate them into the database
def integrate_csv_to_database(folder_path):
    # Connect to the database
    connection = connect_to_database()

    try:
        with connection.cursor() as cursor:
            # Iterate over each file in the folder
            for filename in os.listdir(folder_path):
                if filename.endswith('.csv'):
                    # Extract username from the filename (e.g., "username.csv")
                    username = os.path.splitext(filename)[0]

                    # Ensure the user exists in the User table
                    cursor.execute("SELECT user_id FROM User WHERE username = %s", (username,))
                    user = cursor.fetchone()

                    if not user:
                        # Insert new user
                        cursor.execute("INSERT INTO User (username) VALUES (%s)", (username,))
                        connection.commit()
                        user_id = cursor.lastrowid
                    else:
                        user_id = user['user_id']

                    # Open and process the CSV file
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, mode='r', encoding='utf-8') as csvfile:
                        csvreader = csv.reader(csvfile)

                        for row in csvreader:
                            artist_name, album_title, song_title, date_listened = row

                            # Ensure the artist exists
                            cursor.execute("SELECT artist_id FROM Artist WHERE name = %s", (artist_name,))
                            artist = cursor.fetchone()

                            if not artist:
                                cursor.execute("INSERT INTO Artist (name) VALUES (%s)", (artist_name,))
                                connection.commit()
                                artist_id = cursor.lastrowid
                            else:
                                artist_id = artist['artist_id']

                            # Ensure the album exists
                            cursor.execute("SELECT album_id FROM Album WHERE title = %s AND artist_id = %s",
                                           (album_title, artist_id))
                            album = cursor.fetchone()

                            if not album:
                                cursor.execute("INSERT INTO Album (title, artist_id) VALUES (%s, %s)",
                                               (album_title, artist_id))
                                connection.commit()
                                album_id = cursor.lastrowid
                            else:
                                album_id = album['album_id']

                            # Ensure the song exists
                            cursor.execute(
                                "SELECT song_id FROM Song WHERE title = %s AND album_id = %s AND artist_id = %s",
                                (song_title, album_id, artist_id)
                            )
                            song = cursor.fetchone()

                            if not song:
                                cursor.execute(
                                    "INSERT INTO Song (title, album_id, artist_id) VALUES (%s, %s, %s)",
                                    (song_title, album_id, artist_id)
                                )
                                connection.commit()
                                song_id = cursor.lastrowid
                            else:
                                song_id = song['song_id']

                            # Convert date to MySQL format
                            date_obj = datetime.strptime(date_listened, "%d %b %Y %H:%M")
                            formatted_date = date_obj.strftime("%Y-%m-%d")

                            # Insert the listening record
                            cursor.execute(
                                "INSERT INTO Listening (user_id, song_id, date_listened) VALUES (%s, %s, %s)",
                                (user_id, song_id, formatted_date)
                            )
                            connection.commit()
    finally:
        connection.close()


# Example usage
folder_path = 'path_to_your_folder'  # Replace with the path to your folder containing CSV files
integrate_csv_to_database(folder_path)
