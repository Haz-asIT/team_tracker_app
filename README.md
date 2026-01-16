🔹 Project Overview

Team Tracker is a web-based system developed to support secure and structured management of organizational data, including user roles, task assignments, and audit-related activities. The system is designed with a strong focus on access control, accountability, and maintainability, making it suitable for environments that require controlled permissions and traceable actions.

This project was developed as part of an academic secure software design assignment and follows good version control and documentation practices.

---

## Repository Structure
The repository is organized into logical directories to clearly separate application logic, security components, templates, and static resources. This structure improves readability, maintainability, and overall project management.

```text
.vscode/            - Development environment and editor configuration
assets/             - Images and screenshots (wireframes, documentation visuals)
dashboard/          - Dashboard module (views, templates, logic)
people_management/  - People and contract management module
security/           - Authentication, authorization, and RBAC-related logic
static/             - Static assets such as CSS, JavaScript, and images
staticfiles/        - Collected static files for deployment
task_management/    - Task creation and management module
team_tracker/       - Core Django project configuration (settings, URLs)
templates/          - Shared HTML templates

.gitignore          - Git ignore rules
.gitpod.dockerfile  - Gitpod container configuration
.gitpod.yml         - Gitpod workspace configuration
Procfile            - Deployment process configuration
README.md           - Project documentation
manage.py           - Django management entry point
requirements.txt    - Python dependencies
runtime.txt         - Runtime specification for deployment
mailmap             - Commit author mapping file

---

Version Control Practices
GitHub is used as the main version control platform for this project. All changes made during development are tracked using commits with descriptive messages. This allows clear monitoring of progress, responsibility tracking, and easier debugging. The commit history also provides transparency and accountability throughout the development lifecycle.

🔹 Security & Configuration Notes

Sensitive information such as secret keys and credentials is excluded from the repository.
Environment variables are documented using an .env.example file for reference.
Access permissions within the system follow role-based access control (RBAC) principles.
Repository access is restricted to authorized contributors only.

🔹 Setup Instructions (Summary)

Clone the repository
Create and activate a virtual environment
Install required dependencies
Configure environment variables using .env.example
Run database migrations
pip install -r requirements.txt
python manage.py migrate

How to Run the Application
To start the development server, run:
python manage.py runserver
Once running, the application can be accessed through a web browser using the local development address.

Dependencies

All required Python libraries and frameworks for this project are listed in the requirements.txt file. These dependencies are installed using pip during the setup process.