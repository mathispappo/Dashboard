from flask import Flask, request, render_template, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from fonctions import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Use the existing 'data' folder for uploads
UPLOAD_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        flash('No files part in the request')
        return redirect(url_for('index'))

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))

    files_uploaded = 0
    files_skipped = 0
    files_invalid = 0

    # Process each file
    for file in files:
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)  # Sanitize filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Check if the file already exists in the 'data' folder
            if os.path.exists(file_path):
                files_skipped += 1  # Skip the file if it already exists
            else:
                # Validate the number of columns
                if validate_csv_columns(file):
                    try:
                        # Save file to the upload folder if validation is successful
                        file.seek(0)  # Reset file pointer before saving
                        file.save(file_path)
                        files_uploaded += 1
                    except Exception as e:
                        flash(f"Error saving file {filename}: {e}")
                        continue
                else:
                    files_invalid += 1  # Count as invalid if it doesn't have 4 columns

    # Flash a message indicating the result
    flash(f'Successfully uploaded {files_uploaded} new files. {files_skipped} files were skipped (already existed).')
    if files_invalid > 0:
        flash(f'{files_invalid} files were invalid (not exactly 4 columns) and were not uploaded.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
