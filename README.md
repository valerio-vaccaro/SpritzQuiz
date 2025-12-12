# SpritzQuiz

A quiz platform where users can create quizzes with multiple-choice questions and participate in quiz games. The platform tracks participants and maintains leaderboards based on correct answers.

## Features

- **Create Quizzes**: Create quizzes with multiple questions, each having 4 answer options
- **PIN Protection**: Secure PIN system with two PINs:
  - **Game PIN**: Required for participants to answer quizzes
  - **Stop PIN**: Required to manually stop a quiz before expiration
- **Participate**: Answer quizzes and compete with others (requires Game PIN)
- **Participant Tracking**: View list of all participants with their completion timestamps
- **Leaderboards**: View leaderboards based on correct answers (shown after quiz expiration)
- **One Answer Per User**: Each user can only answer a quiz once (enforced)
- **Username Normalization**: Usernames are automatically converted to lowercase and spaces are removed
- **Expiration System**: Quizzes automatically expire at a specified date/time, or can be stopped manually
- **QR Code Sharing**: Share quizzes easily via QR codes
- **Modern UI**: Beautiful, responsive design with Bootstrap 5
- **GitHub & Onion Links**: Footer links to GitHub repository and Onion service

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - **Linux/macOS**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Using the startup script (recommended)

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

### Option 2: Manual startup

1. Activate the virtual environment
2. Set environment variables (optional):
   ```bash
   export SPRITZQUIZ_DOMAIN=https://your-domain.com  # For QR codes
   ```
3. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5005`

## Project Structure

```
SpritzQuiz/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start.sh              # Startup script for Linux/macOS
├── start.bat             # Startup script for Windows
├── README.md             # This file
├── quizzes.db            # SQLite database (created automatically)
└── templates/
    ├── index.html        # Home page with quiz list
    ├── create.html       # Create new quiz page
    ├── quiz.html         # View quiz details, participants, and leaderboard
    └── answer.html       # Answer quiz page
```

## Database Schema

### Quizzes Table
- `quiz_id` (TEXT PRIMARY KEY): Unique identifier for the quiz
- `title` (TEXT): Quiz title
- `status` (TEXT): Quiz status ('active' or 'finished')
- `created_at` (DATETIME): Creation timestamp
- `expires_at` (DATETIME): Expiration date and time
- `game_pin_hash` (TEXT): SHA256 hash of the Game PIN (for security)
- `stop_pin_hash` (TEXT): SHA256 hash of the Stop PIN (for security)

### Questions Table
- `question_id` (INTEGER PRIMARY KEY): Unique identifier for the question
- `quiz_id` (TEXT): Foreign key to quizzes table
- `question_text` (TEXT): The question text
- `option1`, `option2`, `option3`, `option4` (TEXT): Answer options
- `correct_answer` (INTEGER): Correct answer (1-4)
- `question_order` (INTEGER): Order of the question in the quiz

### Answers Table
- `quiz_id` (TEXT): Foreign key to quizzes table
- `username` (TEXT): Participant username (normalized: lowercase, no spaces)
- `question_id` (INTEGER): Foreign key to questions table
- `selected_answer` (INTEGER): Selected answer (1-4)
- `is_correct` (INTEGER): 1 if correct, 0 if incorrect
- `timestamp` (DATETIME): Answer submission time
- PRIMARY KEY: (quiz_id, username, question_id)

## Features Details

### Username Normalization
- All usernames are automatically converted to lowercase
- All spaces are removed
- Example: "John Doe" becomes "johndoe"

### One Answer Per User
- Each user can only answer a quiz once
- The system checks if a username has already answered before allowing submission
- This is enforced at the database level with a composite primary key

### PIN System

- **Game PIN**: 
  - Required when creating a quiz (minimum 4 characters)
  - Must be shared with participants who want to answer the quiz
  - Required to submit answers to a quiz
  - Hashed using SHA256 before storage - never stored in plain text
  - Visible during entry but never shown again after quiz creation

- **Stop PIN**:
  - Required when creating a quiz (minimum 4 characters)
  - Allows quiz creator to manually stop the quiz before expiration
  - Used via the "Stop Quiz" button on the quiz page
  - Hashed using SHA256 before storage - never stored in plain text
  - Visible during entry but never shown again after quiz creation

**Security Best Practices**:
- Use strong PINs (at least 8 characters recommended)
- Share Game PIN securely with trusted participants only
- Keep Stop PIN confidential - only the quiz creator should have it
- Never share PINs publicly or in unsecured channels

### Expiration System
- When creating a quiz, you must specify an expiration date and time
- Quizzes automatically close when they expire
- Quizzes can also be manually stopped using the Stop PIN before expiration
- After expiration or manual stop, users can no longer answer the quiz
- Leaderboards are only shown after the quiz has expired or been stopped

### Participant Tracking
- The quiz page shows a list of all participants who have answered
- Each participant entry shows:
  - Username (with emoji)
  - Completion timestamp (when they first submitted their answers)

### Leaderboards
- **Global Leaderboard**: Shows top performers across all finished quizzes (on home page)
- **Quiz Leaderboard**: Shows participants for a specific quiz, ordered by correct answers (shown only after expiration)
- Scoring is based on the number of correct answers

### Quiz Status
- **Active**: Quiz is open for participation
- **Finished**: Quiz is closed (expired or manually finished), leaderboard is visible

## Configuration

### Environment Variables

- `SPRITZQUIZ_DOMAIN`: Domain URL for QR code generation (default: `https://quiz.satoshispritz.it`)
- `ONION_URL`: Onion service URL for the application (default: `http://spritzquiz.onion`)

Examples:
```bash
export SPRITZQUIZ_DOMAIN=https://quiz.example.com
export ONION_URL=http://your-onion-address.onion
```

The Onion URL is displayed in the footer links section along with the GitHub repository link.

### Port Configuration

The application runs on port **5005** by default. To change it, modify `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5005)  # Change port number here
```

## Workflow

1. **Create Quiz**: 
   - Go to "Create New Quiz"
   - Enter quiz title
   - Set expiration date/time
   - **Enter Game PIN** (minimum 4 characters) - required for participants to answer
   - **Enter Stop PIN** (minimum 4 characters) - required to stop quiz early
   - Add questions with 4 options each
   - Specify correct answer for each question
   - **Save your PINs** - they will NOT be shown again after creation!

2. **Share Quiz**:
   - After creation, you're redirected to the quiz page
   - Share the QR code or URL with participants
   - **Share the Game PIN** with participants who want to answer

3. **Participate**:
   - Click "Answer This Quiz" button
   - **Enter the Game PIN** (obtained from quiz creator)
   - Enter username (will be normalized automatically)
   - Answer all questions
   - Submit answers

4. **Stop Quiz Early** (Optional):
   - On the quiz page, click "Stop Quiz" button
   - Enter the Stop PIN
   - Quiz will be immediately closed and leaderboard will be shown

5. **View Results**:
   - Quiz page shows list of participants with completion times
   - After expiration or manual stop, leaderboard is displayed showing scores

## Security Notes

- The application uses a simple secret key for Flask sessions. For production, use a secure random key.
- SQLite database is stored locally. For production, consider using PostgreSQL or MySQL.
- Input validation is performed, but always validate user input on the server side.
- Username normalization prevents duplicate entries with different casing/spacing.
- Each user can only answer once per quiz (enforced at database level).
- **PIN Security**:
  - PINs are hashed using SHA256 before storage - original PINs are never stored
  - PINs are visible during entry but never displayed after quiz creation
  - Game PIN controls who can participate in quizzes
  - Stop PIN controls who can manually stop quizzes
  - Always use strong PINs and share them securely

## License

This project is open source and available for use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
