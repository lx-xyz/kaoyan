from app import create_app, db
from config import Config, BASE_DIR

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        import os
        os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    app.run(debug=True, host="127.0.0.1", port=5000)
