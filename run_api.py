from flamengo_api.app import create_app

app = create_app()

if __name__ == "__main__":
    # Use FLASK_RUN_PORT / PORT if needed
    app.run(host="0.0.0.0", port=5000, debug=True)
