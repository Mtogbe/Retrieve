# Retrieve

Find UMBC research labs that fit you.

Built at hackUMBC 2026.

## The problem

Research at UMBC is hard to find. Most students commute. They leave right after class and miss hallway conversations about labs. Programs like Meyerhoff give their scholars strong mentoring and research connections. Everyone else digs through faculty pages and guesses which professors take students.

## What Retrieve does

- Puts UMBC research labs in one searchable directory
- Filters labs by the research interests you type in
- Matches your resume to labs with AI and explains why each one fits
- Answers questions about labs with a chatbot that only uses our lab data
- Drafts a first email to a lab's professor

## Tech stack

- Python and Flask
- HTML with Jinja templates, Bootstrap, and plain JavaScript
- Lab data stored in `data/labs.json`
- Anthropic API for matching, chat, and email drafts
- pypdf for reading resumes

## Project structure

```
retrieve/
  app.py               Flask app and all routes
  ai.py                AI and matching functions
  data/labs.json       real lab data
  data/fake_labs.json  sample labs for testing
  scraper/             data collection scripts
  templates/           HTML pages
  static/              CSS and JavaScript
  requirements.txt     Python packages
  .env.example         template for your API key
```

## Setup

1. Clone the repo.
```
git clone https://github.com/Mtogbe/retrieve.git
cd retrieve
```

2. Make a virtual environment and turn it on.
```
python -m venv venv
```
Mac or Linux
```
source venv/bin/activate
```
Windows
```
venv\Scripts\activate
```

3. Install packages.
```
pip install -r requirements.txt
```

4. Add your API key. Copy `.env.example` to a new file called `.env` and paste your key in. Never commit `.env`.

5. Run the app.
```
flask --app app run --debug
```
Then open http://127.0.0.1:5000 in your browser.

## Team

| Person | Role | Owns |
|---|---|---|
| Michael Togbe | AI and matching | `ai.py` |
| Nahom | Data pipeline | `data/`, `scraper/` |
| Isaac | Frontend and UX | `templates/`, `static/` |
| Harel | Backend and integration | `app.py`, deployment |

## How we work

- Each person works on their own branch.
- Commit whenever something works.
- We merge into `main` at team checkpoints.
- Do not change the lab format or API routes without telling the team.

## Lab data

Every lab is a JSON record with an id, name, department, research areas, and source URL. Other fields like description, website, and contact email are optional. We only use information that is publicly listed on UMBC websites. Each lab links to the page its info came from, so anyone can check it.

## API

| Method | Route | What it does |
|---|---|---|
| GET | `/api/labs` | List and filter labs |
| GET | `/api/labs/<id>` | Get one lab |
| POST | `/api/match` | Match labs to a resume or interests |
| POST | `/api/chat` | Ask the chatbot about labs |
| POST | `/api/email` | Draft an email to a professor |

## Future ideas

- Professors can post open positions
- Student profiles and saved labs
- Automatic data refresh from department pages

