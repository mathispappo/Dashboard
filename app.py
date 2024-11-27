import os
from flask import Flask, request, render_template, flash, redirect, url_for
from Add_file_to_sql import integrate_csv_to_database, create_listening_table_if_not_exist
from add_username import add_username_column_to_csv

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


# Route for integration
@app.route('/integration', methods=['POST'])
def integration():
    # Ensure that the input directory is an absolute path
    input_directory = os.path.join(os.path.dirname(__file__), 'data')  # Use relative path if running the script from the project root
    output_directory = os.path.join(os.path.dirname(__file__), 'download')  # Output directory for processed files

    # Ensure the output directory exists before running the function
    ensure_directory_exists(output_directory)

    # Now process the CSV files in the given directory
    create_listening_table_if_not_exist()  # Ensure the table exists before integrating data
    integrate_csv_to_database(output_directory)

    # After integration, delete all the files in the DOWNLOAD_FOLDER
    delete_files_in_directory(DOWNLOAD_FOLDER)

    flash("Integration complete and files deleted!")
    return redirect(url_for('index'))


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
