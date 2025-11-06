from flask import render_template
from app.db import db_connection

def init_app(app):

    @app.route("/")
    def dashboard():
        conn = db_connection()
        cursor = conn.cursor()

        # Get distinct list of countries.
        cursor.execute(''' 
                        SELECT country_name, COUNT(*) as count 
                        FROM applications
                        GROUP BY country_name
                    ''')
        country_data = cursor.fetchall()
        countries = [(row["country_name"], row['count']) for row in country_data]

        return render_template("dashboard.html", countries = countries)