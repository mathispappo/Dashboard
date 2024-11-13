from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import os

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"  # For flash messages

# Set upload folder (you can adjust this path as needed)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Check if the CSV format is correct
        if validate_csv(filepath):
            flash('File successfully uploaded and validated!')
            return redirect(url_for('index'))
        else:
            flash('Invalid CSV format. Please upload a file with correct columns: Artist, Album, Song, Date.')
            os.remove(filepath)  # Delete the invalid file
            return redirect(url_for('index'))
    else:
        flash('Allowed file type is CSV')
        return redirect(url_for('index'))


# Function to validate if the CSV has the correct format
def validate_csv(filepath):
    try:
        # Load the CSV file
        data = pd.read_csv(filepath)

        # Check if it has exactly 4 columns with the required names
        required_columns = ['Artist', 'Album', 'Song', 'Date']
        if list(data.columns) == required_columns:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error validating CSV: {e}")
        return False


# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


if __name__ == "__main__":
    app.run(debug=True)
