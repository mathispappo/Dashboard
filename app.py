import os
from flask import Flask, request, render_template, flash, redirect, url_for
from Add_file_to_sql import integrate_csv_to_database, create_listening_table_if_not_exist, connect_to_database
from add_username import add_username_column_to_csv
import pymysql

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Define folders
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')

# Ensure the folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Ensure the Listening table exists
create_listening_table_if_not_exist()

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        flash('No files part in the request.')
        return redirect(request.url)

    files = request.files.getlist('files')
    if not files:
        flash('No files selected.')
        return redirect(request.url)

    for file in files:
        if file and file.filename.endswith('.csv'):
            # Save the uploaded file to the UPLOAD_FOLDER
            upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(upload_path)

            # Process the file and save the processed version in DOWNLOAD_FOLDER
            try:
                download_path = os.path.join(DOWNLOAD_FOLDER, file.filename)
                
                # Add username column to the file
                add_username_column_to_csv(upload_path, DOWNLOAD_FOLDER)

                flash(f"File {file.filename} successfully uploaded and processed.")
            except Exception as e:
                flash(f"Error processing file {file.filename}: {e}")

    return redirect(url_for('index'))


@app.route('/integration', methods=['POST'])
def integration():
    # Connect to the database
    connection = connect_to_database()

    try:
        create_listening_table_if_not_exist()  # Ensure the table exists

        # Loop through all files in the DOWNLOAD_FOLDER
        for file_name in os.listdir(DOWNLOAD_FOLDER):
            if file_name.endswith('.csv'):
                # Extract the username from the file name (before .csv)
                username = os.path.splitext(file_name)[0]

                # Check if the username already exists in the database
                if username_exists_in_database(username, connection):
                    flash(f"Username '{username}' already exists. File '{file_name}' skipped.")
                    continue

                # Integrate the file's data into the database
                file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                integrate_csv_to_database(file_path)
                flash(f"File '{file_name}' successfully integrated.")

        # Delete processed files in the DOWNLOAD_FOLDER
        delete_files_in_directory(DOWNLOAD_FOLDER)
        flash("Integration complete and files deleted!")

    except Exception as e:
        flash(f"Error during integration: {e}")

    finally:
        connection.close()

    return redirect(url_for('index'))



# Function to check if username exists in the database
def username_exists_in_database(username, connection):
    """Check if the username already exists in the database."""
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM listening WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        return result[0] > 0

# Function to ensure directory exists (you might already have this in your script)
def ensure_directory_exists(directory):
    """Ensure that the directory exists, if not, create it."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory created: {directory}")


# Function to delete all files in a directory
def delete_files_in_directory(directory):
    """Delete all files in the specified directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):  # Only delete files (not subdirectories)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")

if __name__ == '__main__':
    app.run(debug=True)
