from flask import Flask, request, render_template, redirect, url_for, abort, flash, jsonify
import sqlite3
from datetime import datetime
import uuid
import os
import json
import hashlib

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Get domain from environment variable, default to production URL
DOMAIN = os.environ.get('SPRITZQUIZ_DOMAIN', 'https://quiz.satoshispritz.it')
# Get Onion URL from environment variable, default to spritzquiz.onion
ONION_URL = os.environ.get('ONION_URL', 'http://spritzquiz.onion')

# List of emojis for participants (common emojis well-supported by browsers)
PARTICIPANT_EMOJIS = [
    '🎯', '🚀', '⭐', '🔥', '💎', '🎲', '🎪', '🎨', '🎭', '🎬',
    '🏆', '🥇', '🥈', '🥉', '🎖️', '🏅', '🎗️', '🎟️', '🎫', '🎴',
    '🃏', '🀄', '🎰', '🎮', '🕹️', '🎳', '🎱', '🏓', '🏸', '⚽',
    '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🌍', '🌎', '🌏', '🌐',
    '🗺️', '🧭', '🏔️', '⛰️', '🌋', '🗻', '🏕️', '🏖️', '🏜️', '🏝️',
    '🏞️', '🏟️', '🏛️', '🏗️', '🏘️', '🏚️', '🏠', '🏡', '🏢', '🏣',
    '🏤', '🏥', '🏦', '🏨', '🏩', '🦄', '🐉', '🐲', '🦁', '🐯',
    '🐰', '🐻', '🐼', '🐨', '🐵', '🦊', '🐺', '🐗', '🐴', '🦓',
    '🦌', '🐮', '🐷', '🐽', '🐸', '🐊', '🐢', '🦎', '🐍', '🦕',
    '🦖', '🐳', '🐋', '🐬', '🐟', '🐠', '🐡', '🦈', '🐙', '🐚',
    '🐌', '🦋', '🐛', '🐜', '🐝', '🐞', '🦗', '🕷️', '🦂', '🦟',
    '💐', '🌸', '💮', '🏵️', '🌹', '🥀', '🌺', '🌻', '🌼', '🌷',
    '🌱', '🌲', '🌳', '🌴', '🌵', '🌶️', '🌾', '🌿', '☘️', '🍀',
    '🍁', '🍂', '🍃', '🍇', '🍈', '🍉', '🍊', '🍋', '🍌', '🍍',
    '🥭', '🍎', '🍏', '🍐', '🍑', '🍒', '🍓', '🥝', '🍅', '🥥',
    '🥑', '🍆', '🥔', '🥕', '🌽', '🥒', '🥬', '🥦', '🥗', '🥘',
    '🥙', '🥚', '🥛', '🥜', '🥞', '🥟', '🥠', '🥡', '🥢', '🥣',
    '🥤', '🥧', '🥨', '🥩', '🥪', '🥫', '🥮', '🥯', '🥰', '🥱',
    '🥲', '🥳', '🥴', '🥵', '🥶', '🥷', '🥸', '🥹', '🥺', '🦀',
    '🦂', '🦃', '🦄', '🦅', '🦆', '🦇', '🦈', '🦉', '🦊', '🦋',
    '🦌', '🦍', '🦎', '🦏', '🦐', '🦑', '🦒', '🦓', '🦔', '🦕',
    '🦖', '🦗', '🦘', '🦙', '🦚', '🦛', '🦜', '🦝', '🦞', '🦟',
    '🦡', '🦢', '🧀', '🧁', '🧂', '🧃', '🧄', '🧅', '🧆', '🧇',
    '🧈', '🧉', '🧊', '🧋', '🧍', '🧎', '🧏', '🧐', '🧑', '🧒',
    '🧓', '🧔', '🧕', '🧖', '🧗', '🧘', '🧙', '🧚', '🧛', '🧜',
    '🧝', '🧞', '🧟', '🧠', '🧡', '🧢', '🧣', '🧤', '🧥', '🧦',
    '🧧', '🧨', '🧩', '🧪', '🧫', '🧬', '🧭', '🧮', '🧯', '🧰',
    '🧱', '🧲', '🧳', '🧴', '🧵', '🧶', '🧷', '🧸', '🧹', '🧺',
    '🧻', '🧼', '🧽', '🧾', '🧿', '🩰', '🩱', '🩲', '🩳', '🩴',
    '🩵', '🩶', '🩷', '🩸', '🩹', '🩺', '🪀', '🪁', '🪂', '🪃',
    '🪄', '🪅', '🪆', '🪇', '🪈', '🪉', '🪊', '🪋', '🪌', '🪍',
    '🪎', '🪏', '🪐', '🪑', '🪒', '🪓', '🪔', '🪕', '🪖', '🪗',
    '🪘', '🪙', '🪚', '🪛', '🪜', '🪝', '🪞', '🪟', '🪠', '🪡',
    '🪢', '🪣', '🪤', '🪥', '🪦', '🪧', '🪨', '🪩', '🪪', '🪫',
    '🪬', '🪭', '🪮', '🪯', '🪰', '🪱', '🪲', '🪳', '🪴', '🪵',
    '🪶', '🪷', '🪸', '🪹', '🪺', '🪻', '🪼', '🪽', '🪾', '🪿',
    '🫀', '🫁', '🫂', '🫃', '🫄', '🫅', '🫆', '🫇', '🫈', '🫉',
    '🫊', '🫋', '🫌', '🫍', '🫎', '🫏', '🫐', '🫑', '🫒', '🫓',
    '🫔', '🫕', '🫖', '🫗', '🫘', '🫙', '🫚', '🫛', '🫜', '🫝',
    '🫞', '🫟', '🫠', '🫡', '🫢', '🫣', '🫤', '🫥', '🫦', '🫧',
    '🫨', '🫩', '🫪', '🫫', '🫬', '🫭', '🫮', '🫯', '🫰', '🫱',
    '🫲', '🫳', '🫴', '🫵', '🫶', '🫷', '🫸', '🫹', '🫺', '🫻',
    '🫼', '🫽', '🫾', '🫿'
]

def get_participant_emoji(name):
    """Get a consistent emoji for a participant based on their name."""
    if not name:
        return '👤'
    hash_value = hash(name)
    emoji_index = abs(hash_value) % len(PARTICIPANT_EMOJIS)
    return PARTICIPANT_EMOJIS[emoji_index]

app.jinja_env.globals['get_participant_emoji'] = get_participant_emoji

# Hash PIN function
def hash_pin(pin):
    """Hash a PIN using SHA256"""
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_pin(pin, pin_hash):
    """Verify a PIN against its hash"""
    return hash_pin(pin) == pin_hash

# DB init
def init_db():
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes
                 (quiz_id TEXT PRIMARY KEY, title TEXT, status TEXT, created_at DATETIME, expires_at DATETIME,
                  game_pin_hash TEXT, stop_pin_hash TEXT)''')
    # Add expires_at column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE quizzes ADD COLUMN expires_at DATETIME')
    except sqlite3.OperationalError:
        pass  # Column already exists
    # Add PIN columns if they don't exist (for existing databases)
    try:
        c.execute('ALTER TABLE quizzes ADD COLUMN game_pin_hash TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute('ALTER TABLE quizzes ADD COLUMN stop_pin_hash TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (question_id INTEGER PRIMARY KEY AUTOINCREMENT, quiz_id TEXT, 
                  question_text TEXT, option1 TEXT, option2 TEXT, option3 TEXT, option4 TEXT,
                  correct_answer INTEGER, question_order INTEGER,
                  FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS answers
                 (quiz_id TEXT, username TEXT, question_id INTEGER, selected_answer INTEGER,
                  is_correct INTEGER, timestamp DATETIME, response_time REAL,
                  PRIMARY KEY (quiz_id, username, question_id),
                  FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
                  FOREIGN KEY (question_id) REFERENCES questions(question_id))''')
    # Add response_time column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE answers ADD COLUMN response_time REAL')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    # Get quizzes with participant count
    c.execute('''SELECT q.quiz_id, q.title, q.status, q.created_at, q.expires_at,
                        COUNT(DISTINCT a.username) as participant_count
                 FROM quizzes q
                 LEFT JOIN answers a ON q.quiz_id = a.quiz_id
                 GROUP BY q.quiz_id, q.title, q.status, q.created_at, q.expires_at
                 ORDER BY q.created_at DESC''')
    quizzes_raw = c.fetchall()
    
    # Process quizzes to add expiration status
    quizzes = []
    now = datetime.now()
    for quiz in quizzes_raw:
        quiz_id, title, status, created_at, expires_at, participant_count = quiz
        is_expired = False
        if expires_at:
            expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            if now > expires_dt:
                is_expired = True
        quizzes.append((quiz_id, title, status, created_at, expires_at, participant_count, is_expired))
    
    # Get global leaderboard: all participants from finished quizzes, ordered by correct answers
    c.execute('''SELECT q.quiz_id, q.title, a.username,
                        COUNT(CASE WHEN a.is_correct = 1 THEN 1 END) as correct_count,
                        COUNT(*) as total_questions,
                        MAX(a.timestamp) as last_answer_time
                 FROM quizzes q
                 INNER JOIN answers a ON q.quiz_id = a.quiz_id
                 WHERE q.status = 'finished'
                 GROUP BY q.quiz_id, q.title, a.username
                 ORDER BY correct_count DESC, total_questions DESC, last_answer_time ASC
                 LIMIT 100''')
    leaderboard = c.fetchall()
    
    conn.close()
    return render_template('index.html', quizzes=quizzes, leaderboard=leaderboard, onion_url=ONION_URL)

@app.route('/create', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        try:
            title = request.form['title'].strip()
            if not title:
                flash("Title is required!", "danger")
                return render_template('create.html')
            
            expires_at_str = request.form.get('expires_at', '').strip()
            if not expires_at_str:
                flash("Expiration date/time is required!", "danger")
                return render_template('create.html')
            
            # Parse expiration datetime
            try:
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%dT%H:%M').strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                flash("Invalid date/time format!", "danger")
                return render_template('create.html')
            
            # Check if expiration is in the future
            if datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") <= datetime.now():
                flash("Expiration date/time must be in the future!", "danger")
                return render_template('create.html')
            
            # Get and validate PINs
            game_pin = request.form.get('game_pin', '').strip()
            stop_pin = request.form.get('stop_pin', '').strip()
            
            if not game_pin or len(game_pin) < 4:
                flash("Game PIN is required and must be at least 4 characters!", "danger")
                return render_template('create.html')
            
            if not stop_pin or len(stop_pin) < 4:
                flash("Stop PIN is required and must be at least 4 characters!", "danger")
                return render_template('create.html')
            
            quiz_id = str(uuid.uuid4())[:8]
            questions_data = json.loads(request.form['questions_json'])
            
            if not questions_data or len(questions_data) == 0:
                flash("At least one question is required!", "danger")
                return render_template('create.html')
            
            conn = sqlite3.connect('quizzes.db')
            c = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            game_pin_hash = hash_pin(game_pin)
            stop_pin_hash = hash_pin(stop_pin)
            c.execute("INSERT INTO quizzes (quiz_id, title, status, created_at, expires_at, game_pin_hash, stop_pin_hash) VALUES (?, ?, 'active', ?, ?, ?, ?)",
                      (quiz_id, title, created_at, expires_at, game_pin_hash, stop_pin_hash))
            
            for idx, q in enumerate(questions_data):
                question_text = q.get('question', '').strip()
                option1 = q.get('option1', '').strip()
                option2 = q.get('option2', '').strip()
                option3 = q.get('option3', '').strip()
                option4 = q.get('option4', '').strip()
                correct = int(q.get('correct', 1))
                
                if not all([question_text, option1, option2, option3, option4]):
                    flash("All question fields are required!", "danger")
                    conn.rollback()
                    conn.close()
                    return render_template('create.html')
                
                if not (1 <= correct <= 4):
                    flash("Correct answer must be between 1 and 4!", "danger")
                    conn.rollback()
                    conn.close()
                    return render_template('create.html')
                
                c.execute('''INSERT INTO questions 
                            (quiz_id, question_text, option1, option2, option3, option4, correct_answer, question_order)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (quiz_id, question_text, option1, option2, option3, option4, correct, idx + 1))
            
            conn.commit()
            conn.close()
            flash("Quiz created successfully! Remember your PINs - Game PIN is needed for participants, Stop PIN is needed to stop the quiz early.", "success")
            return redirect(url_for('quiz', quiz_id=quiz_id))
        except Exception as e:
            flash(f"Error creating quiz: {str(e)}", "danger")
    
    return render_template('create.html')

@app.route('/quiz/<quiz_id>')
def quiz(quiz_id):
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    c.execute("SELECT title, status, created_at, expires_at, stop_pin_hash FROM quizzes WHERE quiz_id = ?", (quiz_id,))
    quiz_data = c.fetchone()
    if not quiz_data:
        abort(404)
    
    title, status, created_at, expires_at, stop_pin_hash = quiz_data
    
    # Check if quiz has expired
    is_expired = False
    if expires_at:
        expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_dt and status == 'active':
            # Auto-close expired quizzes
            c.execute("UPDATE quizzes SET status = 'finished' WHERE quiz_id = ?", (quiz_id,))
            conn.commit()
            status = 'finished'
            is_expired = True
        elif datetime.now() > expires_dt:
            is_expired = True
    
    # Get list of participants with their completion timestamp
    c.execute('''SELECT DISTINCT a.username, MIN(a.timestamp) as completion_time
                 FROM answers a
                 WHERE a.quiz_id = ?
                 GROUP BY a.username
                 ORDER BY completion_time ASC''', (quiz_id,))
    participants = c.fetchall()
    
    # Get leaderboard only if quiz is closed (expired or manually stopped)
    leaderboard = []
    is_closed = (status == 'finished') or is_expired
    if is_closed:
        c.execute('''SELECT a.username,
                            COUNT(CASE WHEN a.is_correct = 1 THEN 1 END) as correct_count,
                            COUNT(*) as total_answered,
                            COALESCE(SUM(a.response_time), 0) as total_time,
                            MAX(a.timestamp) as last_answer_time
                     FROM answers a
                     WHERE a.quiz_id = ?
                     GROUP BY a.username
                     ORDER BY correct_count DESC, total_time ASC, last_answer_time ASC''', (quiz_id,))
        leaderboard = c.fetchall()
    
    conn.close()
    
    # Get current timestamp
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate full URL for QR code
    quiz_url = f"{DOMAIN}{url_for('quiz', quiz_id=quiz_id)}"
    
    return render_template('quiz.html',
                         quiz_id=quiz_id,
                         title=title,
                         status=status,
                         created_at=created_at,
                         expires_at=expires_at,
                         is_expired=is_expired,
                         is_closed=is_closed,
                         participants=participants,
                         leaderboard=leaderboard,
                         current_timestamp=current_timestamp,
                         quiz_url=quiz_url,
                         has_stop_pin=bool(stop_pin_hash))

@app.route('/quiz/<quiz_id>/answer', methods=['GET', 'POST'])
def answer_quiz(quiz_id):
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    c.execute("SELECT title, status, expires_at, game_pin_hash FROM quizzes WHERE quiz_id = ?", (quiz_id,))
    quiz_data = c.fetchone()
    if not quiz_data:
        abort(404)
    
    title, status, expires_at, game_pin_hash = quiz_data
    
    # Check if quiz has expired
    is_expired = False
    if expires_at:
        expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_dt:
            is_expired = True
            if status == 'active':
                c.execute("UPDATE quizzes SET status = 'finished' WHERE quiz_id = ?", (quiz_id,))
                conn.commit()
                status = 'finished'
    
    if status != 'active' or is_expired:
        flash("The quiz is not active or has expired, you cannot answer!", "danger")
        conn.close()
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    # Get questions
    c.execute('''SELECT question_id, question_text, option1, option2, option3, option4, correct_answer, question_order
                 FROM questions WHERE quiz_id = ? ORDER BY question_order''', (quiz_id,))
    questions = c.fetchall()
    
    if request.method == 'POST':
        # Get and verify game PIN
        game_pin = request.form.get('game_pin', '').strip()
        if not game_pin:
            flash("Game PIN is required!", "danger")
            conn.close()
            return render_template('answer.html', quiz_id=quiz_id, title=title, questions=questions, total_questions=len(questions))
        
        if not verify_pin(game_pin, game_pin_hash):
            flash("Invalid Game PIN! Please check your PIN and try again.", "danger")
            conn.close()
            return render_template('answer.html', quiz_id=quiz_id, title=title, questions=questions, total_questions=len(questions))
        
        # Normalize name: lowercase and remove all spaces
        username = request.form['username'].strip().lower().replace(' ', '')
        
        if not username:
            flash("Username is required!", "danger")
            conn.close()
            return render_template('answer.html', quiz_id=quiz_id, title=title, questions=questions, total_questions=len(questions))
        
        # Check if user has already answered
        c.execute('''SELECT COUNT(*) FROM answers WHERE quiz_id = ? AND username = ?''',
                  (quiz_id, username))
        if c.fetchone()[0] > 0:
            flash("You have already answered this quiz! Each user can only answer once.", "danger")
            conn.close()
            return redirect(url_for('quiz', quiz_id=quiz_id))
        
        # Store username and game_pin in session for the quiz session
        # We'll use a simple approach: redirect to first question
        conn.close()
        return redirect(url_for('answer_question', quiz_id=quiz_id, question_index=0, username=username, game_pin=game_pin))
    
    conn.close()
    return render_template('answer.html', quiz_id=quiz_id, title=title, questions=questions, total_questions=len(questions))

@app.route('/quiz/<quiz_id>/question/<int:question_index>', methods=['GET', 'POST'])
def answer_question(quiz_id, question_index):
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    c.execute("SELECT title, status, expires_at, game_pin_hash FROM quizzes WHERE quiz_id = ?", (quiz_id,))
    quiz_data = c.fetchone()
    if not quiz_data:
        abort(404)
    
    title, status, expires_at, game_pin_hash = quiz_data
    
    # Check if quiz has expired
    is_expired = False
    if expires_at:
        expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_dt:
            is_expired = True
            if status == 'active':
                c.execute("UPDATE quizzes SET status = 'finished' WHERE quiz_id = ?", (quiz_id,))
                conn.commit()
                status = 'finished'
    
    if status != 'active' or is_expired:
        flash("The quiz is not active or has expired, you cannot answer!", "danger")
        conn.close()
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    # Get questions
    c.execute('''SELECT question_id, question_text, option1, option2, option3, option4, correct_answer, question_order
                 FROM questions WHERE quiz_id = ? ORDER BY question_order''', (quiz_id,))
    questions = c.fetchall()
    
    if question_index >= len(questions):
        # All questions answered, redirect to quiz page
        conn.close()
        flash("Quiz completed successfully!", "success")
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    # Get username and game_pin from query params or form
    username = request.args.get('username') or request.form.get('username', '')
    game_pin = request.args.get('game_pin') or request.form.get('game_pin', '')
    
    if not username or not game_pin:
        flash("Session expired. Please start again.", "danger")
        conn.close()
        return redirect(url_for('answer_quiz', quiz_id=quiz_id))
    
    # Verify game PIN
    if not verify_pin(game_pin, game_pin_hash):
        flash("Invalid Game PIN! Please check your PIN and try again.", "danger")
        conn.close()
        return redirect(url_for('answer_quiz', quiz_id=quiz_id))
    
    # Check if user has already answered this question
    current_question = questions[question_index]
    question_id = current_question[0]
    c.execute('''SELECT COUNT(*) FROM answers WHERE quiz_id = ? AND username = ? AND question_id = ?''',
              (quiz_id, username, question_id))
    if c.fetchone()[0] > 0:
        # Already answered, skip to next question
        conn.close()
        return redirect(url_for('answer_question', quiz_id=quiz_id, question_index=question_index + 1, username=username, game_pin=game_pin))
    
    if request.method == 'POST':
        # Handle answer submission
        start_time = float(request.form.get('start_time', 0))
        selected_answer = request.form.get('selected_answer', '').strip()
        timeout = request.form.get('timeout', 'false') == 'true'
        
        # Calculate response time
        end_time = datetime.now().timestamp()
        response_time = end_time - start_time if start_time > 0 else None
        
        # If timeout (30 seconds) or no answer selected, mark as unanswered
        if timeout or not selected_answer or response_time is None or response_time > 30:
            response_time = None
            selected_answer = None
            is_correct = 0
        else:
            try:
                selected_int = int(selected_answer)
                correct_answer = current_question[6]
                is_correct = 1 if selected_int == correct_answer else 0
            except (ValueError, TypeError):
                # Invalid answer format, mark as unanswered
                response_time = None
                selected_answer = None
                is_correct = 0
        
        # Save answer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''INSERT INTO answers 
                    (quiz_id, username, question_id, selected_answer, is_correct, timestamp, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (quiz_id, username, question_id, selected_answer, is_correct, timestamp, response_time))
        conn.commit()
        conn.close()
        
        # Redirect to next question
        return redirect(url_for('answer_question', quiz_id=quiz_id, question_index=question_index + 1, username=username, game_pin=game_pin))
    
    # GET request - show question
    conn.close()
    return render_template('question.html', 
                         quiz_id=quiz_id,
                         title=title,
                         question=current_question,
                         question_index=question_index,
                         total_questions=len(questions),
                         username=username,
                         game_pin=game_pin)

@app.route('/quiz/<quiz_id>/stop', methods=['POST'])
def stop_quiz(quiz_id):
    conn = sqlite3.connect('quizzes.db')
    c = conn.cursor()
    c.execute("SELECT status, stop_pin_hash FROM quizzes WHERE quiz_id = ?", (quiz_id,))
    quiz_data = c.fetchone()
    if not quiz_data:
        abort(404)
    
    status, stop_pin_hash = quiz_data
    
    if status == 'finished':
        flash("Quiz is already finished!", "info")
        conn.close()
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    # Get and verify stop PIN
    stop_pin = request.form.get('stop_pin', '').strip()
    if not stop_pin:
        flash("Stop PIN is required!", "danger")
        conn.close()
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    if not verify_pin(stop_pin, stop_pin_hash):
        flash("Invalid Stop PIN! Please check your PIN and try again.", "danger")
        conn.close()
        return redirect(url_for('quiz', quiz_id=quiz_id))
    
    # Stop the quiz
    c.execute("UPDATE quizzes SET status = 'finished' WHERE quiz_id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    flash("Quiz stopped successfully!", "success")
    return redirect(url_for('quiz', quiz_id=quiz_id))

if __name__ == '__main__':
    app.run(debug=True, port=5005)

