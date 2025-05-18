# RedditStockAnalyzer

Small project I have made during the weekend.

## Features

- User registration, login, and profile management
- Add/remove favourite stocks
- View sentiment analysis for stocks based on Reddit data
- Switch between classic and ML-based sentiment analysis views

## Tech Stack

- Python 3
- Django
- HTML/CSS (Tailwind CSS recommended)
- SQLite (default, can be changed)

## Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/yourusername/RedditStockAnalyzer.git
   cd RedditStockAnalyzer
   ```
   
2. **Create a virtual environment:**
```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
 ```
3. **Create a .env file:**
```bash
    cp .env.example .env
```
   - Fill in the required environment variables in the `.env` file.
4. **Install dependencies:**
```bash
    pip install -r requirements.txt
```

5. **Run migrations:**
```bash
    python manage.py migrate
```

6. **Run tailiwind CSS build:**
```bash
    python manage.py tailwind build
```

7. **Run the development server:**
```bash
    python manage.py runserver
```

8. **Enjoy :>**