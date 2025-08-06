# app.py (save this in excel_uploader/app.py)

from flask import Flask, render_template, request, flash, redirect, url_for, session
import pandas as pd
import mysql.connector
from mysql.connector import Error
import numpy as np
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import tempfile

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

# Configure upload folder
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class DatabaseManager:
    @staticmethod
    def test_connection(host, user, password, database, port=3306):
        try:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            if conn.is_connected():
                conn.close()
                return True
        except Error as e:
            print(f"Error: {e}")
            return False
        return False

    @staticmethod
    def get_mysql_type(dtype):
        if pd.api.types.is_integer_dtype(dtype):
            return 'INT'
        elif pd.api.types.is_float_dtype(dtype):
            return 'FLOAT'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return 'DATETIME'
        elif pd.api.types.is_bool_dtype(dtype):
            return 'BOOLEAN'
        else:
            return 'VARCHAR(255)'

    @staticmethod
    def create_table_and_upload_data(db_config, df, table_name):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Clean column names (preserve original names but make them MySQL-safe)
            original_columns = df.columns.tolist()
            clean_columns = [''.join(e for e in column if e.isalnum() or e == '_') for column in original_columns]
            
            # Create mapping for renaming
            column_mapping = dict(zip(original_columns, clean_columns))
            df = df.rename(columns=column_mapping)

            # Create table with only the columns from the file (no auto-increment ID)
            columns = []
            for column, dtype in df.dtypes.items():
                mysql_type = DatabaseManager.get_mysql_type(dtype)
                columns.append(f"`{column}` {mysql_type}")

            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
            """
            cursor.execute(create_table_query)

            # Insert data
            columns_list = ', '.join([f"`{col}`" for col in df.columns])
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_query = f"INSERT INTO {table_name} ({columns_list}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples, handling NaN values
            data = [tuple(x) for x in df.replace({np.nan: None}).values]
            cursor.executemany(insert_query, data)
            conn.commit()

            rows_affected = len(data)
            return True, rows_affected

        except Error as e:
            return False, str(e)
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    host = request.form['host']
    user = request.form['user']
    password = request.form['password']
    database = request.form['database']
    port = request.form.get('port', 3306)  # Default to 3306 if not provided
    
    # Convert port to integer
    try:
        port = int(port)
    except (ValueError, TypeError):
        port = 3306
    
    if DatabaseManager.test_connection(host, user, password, database, port):
        session['db_config'] = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'port': port
        }
        flash('Database connection successful!', 'success')
        return redirect(url_for('upload'))
    else:
        flash('Failed to connect to database. Please check your credentials.', 'error')
        return redirect(url_for('index'))

@app.route('/upload')
def upload():
    if 'db_config' not in session:
        flash('Please connect to database first', 'error')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload'))
    
    file = request.files['file']
    table_name = request.form['table_name']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Read the file
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            # Process the file
            success, result = DatabaseManager.create_table_and_upload_data(
                session['db_config'], df, table_name
            )

            os.remove(filepath)  # Clean up the temporary file

            if success:
                flash(f'Successfully uploaded {result} records to table {table_name}', 'success')
            else:
                flash(f'Error uploading data: {result}', 'error')

        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
            
        return redirect(url_for('upload'))
    
    flash('Invalid file type. Please upload CSV or Excel files only.', 'error')
    return redirect(url_for('upload'))

if __name__ == '__main__':
    app.run(debug=True)