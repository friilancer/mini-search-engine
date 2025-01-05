from app import create_app
import os

DEBUG_MODE = os.getenv("ENVIRONMENT", "dev").lower() != "production"
PORT = int(os.getenv("PORT", 5000))

app = create_app()

print("Starting Flask app...")

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=PORT)