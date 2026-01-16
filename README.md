# Team Tracker Application

## Project Overview
Team Tracker is a web-based system developed to support secure and structured management of organizational data. The system focuses on managing user roles, task assignments, and people-related records while ensuring proper access control and accountability.

This application is designed with maintainability and security in mind, making it suitable for environments that require controlled permissions and traceable user actions. The project was developed as part of an academic Secure Software Design assignment and follows standard version control and documentation practices.

## Repository Structure
The repository is organized into logical directories to clearly separate application logic, security components, templates, and static resources. This structure improves readability, maintainability, and overall project management.

.vscode/ - Development environment and editor configuration
assets/ - Images and screenshots (wireframes, documentation visuals)
dashboard/ - Dashboard module (views, templates, logic)
people_management/ - People and contract management module
security/ - Authentication, authorization, and RBAC-related logic
static/ - Static assets such as CSS, JavaScript, and images
staticfiles/ - Collected static files for deployment
task_management/ - Task creation and management module
team_tracker/ - Core Django project configuration (settings, URLs)
templates/ - Shared HTML templates

.gitignore - Git ignore rules
.gitpod.dockerfile - Gitpod container configuration
.gitpod.yml - Gitpod workspace configuration
Procfile - Deployment process configuration
README.md - Project documentation
manage.py - Django management entry point
requirements.txt - Python dependencies
runtime.txt - Runtime specification for deployment
mailmap - Commit author mapping file


## Version Control Practices
GitHub is used as the main version control platform for this project. All changes made during development are tracked using commits with descriptive messages. This allows clear monitoring of progress, responsibility tracking, and easier debugging. The commit history also provides transparency and accountability throughout the development lifecycle.

## Security Features Summary
The application implements several security-focused practices to protect data and control access:

- Role-Based Access Control (RBAC) to restrict system functionality based on user roles
- Authentication and authorization mechanisms to prevent unauthorized access
- Sensitive information such as secret keys and credentials excluded from the repository
- Environment variables documented using an `.env.example` file
- Repository access limited to authorized contributors only

## Installation Steps
Follow the steps below to set up the project locally:

1. Clone the repository
2. Create and activate a Python virtual environment
3. Install required dependencies
4. Configure environment variables based on `.env.example`
5. Run database migrations

```bash
pip install -r requirements.txt
python manage.py migrate

##How to Run the Application
To start the development server, run the following command:
  python manage.py runserver
Once running, the application can be accessed through a web browser using the local development address.

##Dependencies
All required Python libraries and frameworks for this project are listed in the requirements.txt file. These dependencies are installed using pip during the setup process.

##System Screenshots
Login Page
<h3>Login Page</h3>
<p align="center">
  <img src="assets/login/1.png" width="700" />
</p>
Dashboard View
<h3>Dashboard View</h3>
<p align="center">
  <img src="assets/manager/6.png" width="700" />
</p>