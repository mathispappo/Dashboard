# Dashboard

Step 1: Set up the Environment
1.	Install Python dependencies:
pip install -r requirements.txt
2.	Set up a MySQL database and update credentials in config.py.
Step 2: Run the Flask Application
1.	Start the server:
python app.py
2.	Access the application at http://localhost:5000.
Step 3: View Dashboards
1.	Import the Power BI file (power_bi_dashboard.pbix) and connect to the MySQL database.
2.	Interact with the visualizations.
Once you have installed all the dependencies previously announced, you must make some changes in the code to make the connection between the code and the MySQL database. 

Line 8-13 Add_file_to_sql.py:
You must change the information with your personal information. 
host='localhost',
        user=’<your mysql username>’,
        password=' your mysql password ',
        database=' your mysql project name ',
