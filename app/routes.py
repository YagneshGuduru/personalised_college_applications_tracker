def init_app(app):
    @app.route("/")
    def home():
        return "App running!"
