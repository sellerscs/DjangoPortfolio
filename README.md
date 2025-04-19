# Esports for Education

**Esports for Education** is a full-stack web application built to support the operational needs of scholastic esports organizations. Designed with educators in mind, the platform provides a centralized, intuitive hub for managing leagues, teams, players, matches, and scores — all while supporting real-time coordination between coaches.

## Project Purpose

This application was developed to address the complex, often disjointed workflows that school-based esports programs face. By providing an all-in-one system, it enables educators to focus more on students and gameplay rather than administration through 3rd party applications.

## Key Features

- **Multi-Organization Support**: Each organization functions as its own tenant with isolated data
- **League and Season Management**: Create and manage esports seasons per organization
- **Team Registration and Roster Management**: Coaches can register teams, submit rosters, and manage players
- **Automatic Match Scheduling**: Seamlessly generates matchups for registered teams
- **Score Reporting System**: Teachers/coaches can enter and verify match results
- **Real-Time Communication**: WebSocket-powered live match screens allow coaches to chat and coordinate during matches
- **Upcoming Matches and Rosters**: Easy-to-navigate views for all scheduled matches and teams

## Tech Stack & Tools

### Backend

- **Python 3 / Django**: Core backend framework
- **Django-Tenants**: Enables multi-tenant support for multiple organizations
- **PostgreSQL**: Schema-based separation for each organization’s data
- **Django Channels / WebSockets**: Real-time communication between coaches during matches
- **OAuth 2.0 (Google and Microsoft)**: Secure login and identity management
- **Custom Middleware**: Routes requests to the correct schema and handles tenant logic

### Frontend

- **Bootstrap 5**: Responsive, accessible UI components
- **Django Templates**: Rapid rendering with server-side context

### Tooling & DevOps

- **Virtualenv**: Isolated Python environment for dependable dependency management
- **dotenv (.env)**: Environment-specific configurations
- **Logging**: Application-level logging using Django’s built-in logging system
- **Git**: Version control with well-documented, semantic commit history
- **VS Code**: Primary development environment

## My Role

As the sole developer and project architect, I was responsible for:

- Full-stack design and development
- Schema design for multi-tenant data architecture
- Implementing user roles, authentication, and secure access
- Real-time communication features using Django Channels and WebSockets
- Creating intuitive, easy to navigate UI/UX for educators
- Writing maintainable, testable code
- Gathering and applying feedback from real-world educator users
- Supporting deployment and documentation for live use

## Real-World Impact

This platform is currently used by over 300 schools in a statewide scholastic esports league. It has replaced several disconnected tools and significantly reduced the time and effort required by coaches and organizers to manage teams and matches.

## Future Enhancements

- Export match and roster reports as CSV or PDF
- Role-specific dashboards (e.g., player vs coach views)
- Integrations with LMS platforms like Google Classroom
- In-app notifications for league admins and match scheduling
- Enhanced Admin analytics and metrics dashboards

## Project Status

Actively maintained and in real-world use. Built with feedback from educators and esports coaches, with ongoing enhancements based on practical needs.

---

If you'd like to see a demo, or discuss technical decisions, feel free to connect. I'm always excited to talk about building software that helps educators and students succeed.
