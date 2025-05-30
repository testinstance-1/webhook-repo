from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from dateutil.parser import parse
import os

app = Flask(__name__)

# MongoDB setup with hardcoded connection string
client = MongoClient('mongodb+srv://ggsmurf589:shashwat1810@cluster0.hmazqzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client['github_actions_db']
collection = db['actions']

# Webhook endpoint to receive GitHub events
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Check if payload is empty or invalid
        if not request.is_json or not request.get_data():
            return jsonify({'status': 'error', 'message': 'Empty or invalid JSON payload'}), 400

        data = request.json
        action_type = request.headers.get('X-GitHub-Event')

        # Initialize document for MongoDB
        doc = {}

        if action_type == 'push':
            commit = data['head_commit']
            doc = {
                'request_id': commit['id'],
                'author': data['pusher']['name'],
                'action': 'PUSH',
                'from_branch': None,  # Push doesn't have a from_branch
                'to_branch': data['ref'].split('/')[-1],  # Extract branch name
                'timestamp': parse(commit['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC')
            }

        elif action_type == 'pull_request':
            pr = data['pull_request']
            if data['action'] in ['opened', 'reopened']:
                doc = {
                    'request_id': str(pr['id']),
                    'author': pr['user']['login'],
                    'action': 'PULL_REQUEST',
                    'from_branch': pr['head']['ref'],
                    'to_branch': pr['base']['ref'],
                    'timestamp': parse(pr['created_at']).strftime('%Y-%m-%d %H:%M:%S UTC')
                }

        elif action_type == 'pull_request' and data['action'] == 'closed' and data['pull_request']['merged']:
            # Handle merge events (brownie points)
            pr = data['pull_request']
            doc = {
                'request_id': str(pr['id']),
                'author': pr['user']['login'],
                'action': 'MERGE',
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'timestamp': parse(pr['merged_at']).strftime('%Y-%m-%d %H:%M:%S UTC')
            }

        # Store in MongoDB if document is created
        if doc:
            collection.insert_one(doc)
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'ignored'}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

# UI endpoint to display actions
@app.route('/')
def index():
    # Fetch all actions from MongoDB, sorted by timestamp (newest first)
    actions = list(collection.find().sort('timestamp', -1).limit(50))  # Limit to avoid overload
    formatted_actions = []

    for action in actions:
        if action['action'] == 'PUSH':
            formatted = f"{action['author']} pushed to {action['to_branch']} on {action['timestamp']}"
        elif action['action'] == 'PULL_REQUEST':
            formatted = (f"{action['author']} submitted a pull request from "
                         f"{action['from_branch']} to {action['to_branch']} on {action['timestamp']}")
        elif action['action'] == 'MERGE':
            formatted = (f"{action['author']} merged branch {action['from_branch']} "
                         f"to {action['to_branch']} on {action['timestamp']}")
        formatted_actions.append(formatted)

    return render_template('index.html', actions=formatted_actions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
