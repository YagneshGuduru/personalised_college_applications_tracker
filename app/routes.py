from flask import render_template, request, redirect, url_for, flash
from app.db import db_connection
import pycountry

def init_app(app):

    # Route to Dashboard.
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
    
    # Route to add application form.
    @app.route("/add_application", methods=["GET", "POST"])
    def add_application():

        if request.method == "POST":
            form = request.form
            conn = db_connection()
            cursor = conn.cursor()

            university_name       = form["university_name"]
            country_name          = form["country_name"]
            course_name           = form["course_name"]
            degree_type           = form.get("degree_type")
            course_url            = form.get("course_url")
            intake_type           = form.get("intake_type")
            intake_year           = form.get("intake_year")
            application_open_date = form.get("application_open_date")
            deadline_date         = form.get("deadline_date")
            ielts_required        = form.get("ielts_required")
            german_required       = form.get("german_required")
            extra_requirements    = form.get("extra_requirements")
            application_mode      = form.get("application_mode")
            status                = form["status"]
            date_submitted        = None
            decision_date         = None
                

            cursor.execute("""
                INSERT INTO applications (
                    university_name, country_name, course_name,
                    degree_type, course_url,
                    intake_type, intake_year,
                    application_open_date, deadline_date,
                    ielts_required, german_required, extra_requirements,
                    application_mode, status, date_submitted, decision_date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                university_name, country_name, course_name,
                degree_type, course_url,
                intake_type, intake_year,
                application_open_date, deadline_date,
                ielts_required, german_required, extra_requirements,
                application_mode, status, date_submitted, decision_date
            ))

            conn.commit()

            return redirect(url_for("dashboard"))

        return render_template("add_application.html")
    
    # API route for countries.
    @app.route("/api/country_suggest")
    def country_suggest():
        q = request.args.get("q", "").lower()

        countries = [c.name for c in pycountry.countries]

        # filter by prefix or partial match.
        matches = [ c for c in countries if c.lower().startswith(q)]

        return matches[:10]
    
    # API route for universities.
    @app.route("/api/university_suggest")
    def university_suggest():
        q = request.args.get("q", "")
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                        SELECT DISTINCT university_name
                        FROM applications
                        WHERE university_name LIKE ?
                        LIMIT 10
                    ''', (F"{q}%",)
                    )
        universities_data = cursor.fetchall()
        return [row["university_name"] for row in universities_data]
    
    # Route for country wise applications.
    @app.route("/country/<string:country_name>")
    def country_applications(country_name):
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                        SELECT * FROM applications
                        WHERE country_name = ?
                       ORDER BY deadline_date ASC
                    ''', (country_name,))
        app_list = cursor.fetchall()

        def count_status(status):
            return sum(1 for a in app_list if a['status'] == status)
        
        summary = {
            "total" : len(app_list),
            "shortlisted" : count_status("shortlisted"),
            "preparing" : count_status("preparing"),
            "submitted" : count_status("submitted"),
            "admitted" : count_status("admitted"),
            "rejected" : count_status("rejected")
        }

        app_list = [dict(a) for a in app_list]

        return render_template("country_applications.html", country = country_name, apps = app_list, summary = summary)
    
    # Route for application details.
    @app.route("/applications/<int:app_id>")
    def application_details(app_id):
        
        conn = db_connection()
        cursor = conn.cursor()

        cursor.execute(''' SELECT * FROM applications WHERE app_id = ?''', (app_id,))
        applications_list = cursor.fetchone()

        if not applications_list:
            flash("Application not found.", "error")
            conn.close()
            return redirect(url_for('dashboard'))
        
        cursor.execute(" SELECT * FROM documents_required WHERE app_id = ? ", (app_id,))
        documents_required_list = cursor.fetchall()
        
        cursor.execute(" SELECT * FROM documents_status WHERE app_id = ? ", (app_id,))
        documents_status_list = cursor.fetchall()
        
        cursor.execute(" SELECT * FROM payments WHERE app_id = ?", (app_id,))
        payments = cursor.fetchall()

        cursor.execute(" SELECT * FROM submission_info WHERE app_id = ? ", (app_id,))
        submission_info = cursor.fetchone()
        
        cursor.execute("SELECT * FROM timeline WHERE app_id = ? ", (app_id,))
        timeline = cursor.fetchall()

        return render_template("application_details.html", app = dict(applications_list), 
                               documents_required_list = [dict(d) for d in documents_required_list],
                               documents_status_list = [dict(row) for row in documents_status_list],
                               payments = [dict(p) for p in payments],
                               submission_info = dict(submission_info) if submission_info else None,
                               timeline = [dict(row) for row in timeline]
                               )
    
    @app.route("/applications/<int:app_id>/update", methods=["GET", "POST"])
    def update_application(app_id):
        conn = db_connection()
        cursor = conn.cursor()
    
        if request.method == "GET":
            cursor.execute("SELECT * FROM applications WHERE app_id = ?", (app_id,))
            app_data = cursor.fetchone()
    
            if not app_data:
                flash("Application not found.", "error")
                return redirect(url_for("application_details", app_id=app_id))
    
            return render_template("update_application.html", app=dict(app_data))
    
        # POST logic:
        try:
            data = (
                request.form.get("university_name"),
                request.form.get("country_name"),
                request.form.get("course_name"),
                request.form.get("degree_type"),
                request.form.get("course_url"),
                request.form.get("intake_type"),
                request.form.get("intake_year"),
                request.form.get("application_open_date"),
                request.form.get("deadline_date"),
                request.form.get("ielts_required"),
                request.form.get("german_required"),
                request.form.get("extra_requirements"),
                request.form.get("application_mode"),
                request.form.get("status"),
                request.form.get("date_submitted"),
                request.form.get("decision_date"),
                app_id
            )
    
            cursor.execute("""
                UPDATE applications SET
                    university_name = ?, country_name = ?, course_name = ?,
                    degree_type = ?, course_url = ?, intake_type = ?, intake_year = ?,
                    application_open_date = ?, deadline_date = ?,
                    ielts_required = ?, german_required = ?, extra_requirements = ?,
                    application_mode = ?, status = ?, date_submitted = ?, decision_date = ?
                WHERE app_id = ?
            """, data)
    
            conn.commit()
            flash("Application updated successfully!", "success")
            return redirect(url_for("application_details", app_id=app_id))
        
        except Exception as e:
            flash("Error updating application: " + str(e), "error")
            return redirect(url_for("update_application", app_id=app_id))
    
    # Route for deleting an application
    @app.route("/applications/<int:app_id>/delete", methods=["POST"])
    def delete_application(app_id):
        try:
            conn = db_connection()
            cursor = conn.cursor()

            # Delete from related tables if needed
            cursor.execute("DELETE FROM documents_required WHERE app_id = ?", (app_id,))
            cursor.execute("DELETE FROM documents_status WHERE app_id = ?", (app_id,))
            cursor.execute("DELETE FROM payments WHERE app_id = ?", (app_id,))
            cursor.execute("DELETE FROM submission_info WHERE app_id = ?", (app_id,))
            cursor.execute("DELETE FROM timeline WHERE app_id = ?", (app_id,))

            # Delete main application
            cursor.execute("DELETE FROM applications WHERE app_id = ?", (app_id,))
            conn.commit()

            flash("Application deleted successfully!", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash("Error deleting application: " + str(e), "error")
            return redirect(url_for("application_details", app_id=app_id))