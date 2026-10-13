
# AI-Powered HR Recruitment Assistant

An intelligent recruitment management web application built with Django to help HR professionals streamline candidate screening, resume analysis, and recruitment workflows.

## Features

- Secure HR login and authentication
- Interactive recruitment dashboard
- Job creation and management
- Candidate resume upload and parsing
- Automated candidate-job skill matching
- Candidate match score calculation
- Candidate ranking and filtering
- Side-by-side candidate comparison
- Recruitment insights and analytics

## Tech Stack

**Backend:** Python, Django

**Frontend:** HTML, CSS, JavaScript

**Database:** SQLite

**Resume Processing:** Python-based resume parsing

**Version Control:** Git, GitHub

## Project Structure

```text
ai-hr-recruitment-assistant/
├── recruitment/
│   ├── migrations/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── recruitment_project/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/elakiyasakthivel27/ai-hr-recruitment-assistant.git
cd ai-hr-recruitment-assistant
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the required Django environment variables before running the project.

Run migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

## Security

- Django secret key is managed using environment variables.
- Uploaded resumes and local database files are excluded from Git.
- Debug mode is disabled by default.

## Future Enhancements

- Cloud deployment
- Advanced AI-based resume screening
- Interview scheduling
- Recruitment reporting and exports

## Developer

**Elakiya S**

GitHub: https://github.com/elakiyasakthivel27

Portfolio: https://elakiya-s-portfolio.netlify.app/
