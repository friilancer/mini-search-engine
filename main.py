from app import create_app
import os

DEBUG_MODE = os.getenv("ENVIRONMENT", "dev").lower() != "production"

app = create_app()

print("Starting Flask app...")

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)