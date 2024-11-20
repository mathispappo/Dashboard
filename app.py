from flask import Flask, request, render_template, flash, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

UPLOAD_FOLDER = 'uploaded_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist


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

    # Process each file
    for file in files:
        if file and file.filename.endswith('.csv'):
            # Save file to the upload folder
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    flash(f'Successfully uploaded {len(files)} files.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
