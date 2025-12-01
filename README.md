# Discussions.ru

<p align="center">
  <img src="users/static/img/home/home_1.svg" width="350">
</p>

**Discussions.ru** is a structured Q&A and communication platform built for online schools in the Commonwealth of Independent States (CIS).  
It has been successfully integrated into **Obrazavr.ru**, where it currently supports over **600,000 active users**.

The platform provides an organized, searchable environment for students and instructors, serving as a scalable alternative to unstructured messenger-based communication.

---

## Features

- **Course-based discussions** with categories
- **Anonymous questions** for students
- **Rich editor** with LaTeX support and syntax-highlighted code blocks
- **Fast global search** across questions and answers
- **Instructor tools:** announcements, highlighting answers, co-instructors
- **Email notifications** for replies and updates

---

## Running Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/discussions.git
   cd discussions

2. **Create and activate a virtual environment**
    ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   
3. **Install dependencies**
    ```bash
   pip install -r requirements.txt

4. **Run migrations**
    ```bash
   python manage.py migrate

5. **Start the development server**
    ```bash
   python manage.py runserver

The application will be available at:
http://127.0.0.1:8000
