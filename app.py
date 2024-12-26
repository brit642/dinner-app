from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Data Structure (replace with a database in a real app)
# We'll use a JSON file to simulate a database for now
DATA_FILE = 'data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"sessions": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Helper Functions ---

def get_current_session():
    data = load_data()
    session_id = session.get('session_id')
    if session_id and session_id in data['sessions']:
        return data['sessions'][session_id]
    return None

def calculate_scores(votes):
    scores = {}
    for host, host_votes in votes.items():
        voter_scores = []
        for voter, vote in host_votes.items():
            food = vote['food']
            creativity = vote['creativity']
            activity = vote['activity']
            global_score = vote['global'] * 1.2
            voter_score = food + creativity + activity + global_score
            voter_scores.append(voter_score)

            # Store individual votes (anonymously at first)
            if 'detailed_votes' not in scores:
                scores['detailed_votes'] = {}
            if host not in scores['detailed_votes']:
                scores['detailed_votes'][host] = []
            scores['detailed_votes'][host].append({
                'voter': voter,  # Initially hidden
                'food': food,
                'creativity': creativity,
                'activity': activity,
                'global': global_score
            })
        if voter_scores:
            scores[host] = sum(voter_scores) / len(voter_scores)
        else:
            scores[host] = 0 # Handle cases with no votes

    return scores

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()
    participants = ["Kassia", "Said", "Alex", "David", "Papé"]

    if request.method == 'POST':
        host = request.form.get('host')
        session_id = host + "_session"  # Simple session ID for now
        session['session_id'] = session_id

        # Initialize session data
        if session_id not in data['sessions']:
            data['sessions'][session_id] = {
                'host': host,
                'votes': {host: {}},  # Votes for the current host
                'voters': [p for p in participants if p != host],
                'stage': 'voting'  # Initial stage
            }
            save_data(data)

        return redirect(url_for('voting'))

    return render_template('index.html', participants=participants)

@app.route('/voting', methods=['GET', 'POST'])
def voting():
    current_session = get_current_session()

    if not current_session or current_session['stage'] != 'voting':
        return redirect(url_for('index'))

    voters = current_session['voters']
    host = current_session['host']

    if request.method == 'POST':
        data = load_data()
        current_session_data = data['sessions'][session['session_id']]
        voter = request.form.get('voter')
        
        # Handle opt-out
        if 'opt_out' in request.form:
            current_session_data['votes'][host][voter] = 'opt_out'
        else:
            current_session_data['votes'][host][voter] = {
                'food': int(request.form['food']),
                'creativity': int(request.form['creativity']),
                'activity': int(request.form['activity']),
                'global': int(request.form['global'])
            }
        
        current_session_data['voters'].remove(voter)

        if not current_session_data['voters']:
            current_session_data['stage'] = 'results'
            current_session_data['scores'] = calculate_scores(current_session_data['votes'])

        save_data(data)

        if current_session_data['stage'] == 'results':
            return redirect(url_for('results'))
        else:
            return redirect(url_for('voting'))

    return render_template('voting.html', voters=voters, host=host)

@app.route('/results', methods=['GET', 'POST'])
def results():
    current_session = get_current_session()

    if not current_session or current_session['stage'] != 'results':
        return redirect(url_for('index'))

    reveal_names = 'reveal_names' in request.form
    
    # Prepare detailed votes with or without names based on reveal_names
    detailed_votes = current_session['scores']['detailed_votes']
    if reveal_names:
        # If revealing names, we don't need to do anything special
        pass  
    else:
        # If not revealing names, replace voter names with anonymous labels
        for host_votes in detailed_votes.values():
            for vote in host_votes:
                vote['voter'] = 'Anonymous'

    return render_template('results.html', scores=current_session['scores'], detailed_votes=detailed_votes, host=current_session['host'], reveal_names=reveal_names)

if __name__ == '__main__':
    app.run(debug=True)