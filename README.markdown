# Webhook-Repo

This repository implements a Flask-based webhook receiver for GitHub actions from the `action-repo` repository. It stores events in MongoDB and displays them in a UI that refreshes every 15 seconds.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/webhook-repo.git
   cd webhook-repo
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up MongoDB**:
   - The MongoDB connection string is hardcoded in `app.py` to use a MongoDB Atlas cluster.
   - Ensure the cluster is accessible and the credentials are valid.

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Expose the Endpoint**:
   - Use a tool like `ngrok` to expose the local server:
     ```bash
     ngrok http 5000
     ```
   - Update the webhook URL in `action-repo` to the ngrok URL (e.g., `https://your-ngrok-id.ngrok.io/webhook`).

6. **Test the Application**:
   - Perform push, pull request, or merge actions in `action-repo`.
   - Visit `http://localhost:5000` to see the UI with the latest actions.

## MongoDB Schema
- `_id`: ObjectId (MongoDB default)
- `request_id`: String (Git commit hash or PR ID)
- `author`: String (GitHub username)
- `action`: String (Enum: PUSH, PULL_REQUEST, MERGE)
- `from_branch`: String (source branch, null for PUSH)
- `to_branch`: String (target branch)
- `timestamp`: String (UTC datetime)

## Notes
- The UI refreshes every 15 seconds to fetch the latest actions.
- Merge event handling is included for brownie points.
- Ensure proper error handling and date formatting as per requirements.
- **Security Warning**: The MongoDB connection string is hardcoded. Rotate credentials after use and avoid exposing them in public repositories.