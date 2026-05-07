# University Management System (UMS)

A comprehensive, modular, and scalable web-based University Management System built with Django.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────────┐ │
│  │ Web UI   │  │ REST API │  │ Django Admin Panel     │ │
│  │(Templates│  │(DRF+JWT) │  │                       │ │
│  │+BS5)     │  │          │  │                       │ │
│  └──────────┘  └──────────┘  └───────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    APPLICATION LAYER                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │Accounts │ │Students │ │Academics│ │ Staff   │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │Finance  │ │Library  │ │ Hostel  │ │Comms    │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│  ┌─────────┐                                           │
│  │Reports  │                                           │
│  └─────────┘                                           │
├─────────────────────────────────────────────────────────┤
│                      DATA LAYER                          │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ SQLite/   │  │  Redis   │  │  File Storage    │    │
│  │ PostgreSQL│  │ (Cache)  │  │  (Media/Static)  │    │
│  └───────────┘  └──────────┘  └──────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 4.2, Django REST Framework |
| Frontend | Bootstrap 5, Chart.js, Bootstrap Icons |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Authentication | JWT (API) + Session-based (Web) |
| Task Queue | Celery + Redis |
| Static Files | WhiteNoise |
| API Docs | DRF Browsable API |

## Modules

### 1. Accounts (Authentication & Access Control)
- Custom User model with roles (Admin, Registrar, Lecturer, Student, Finance, Librarian, Hostel Manager)
- Role-based permissions via decorators
- JWT token authentication for API
- Session-based auth for web interface
- Audit logging

### 2. Students
- Student profiles linked to user accounts
- Admission application workflow
- Course registration per semester
- Academic history and transcript generation
- GPA/CGPA calculation

### 3. Academics
- Faculty and Department hierarchy
- Programme management (Certificate to PhD)
- Course creation with prerequisites
- Academic sessions and semesters
- Course allocation to lecturers
- Timetable/scheduling
- Attendance tracking
- Grading system with configurable grade scales
- Result entry and publication

### 4. Staff
- Staff profiles with ranks and qualifications
- Workload management (credit unit tracking)
- Performance evaluation
- Course allocation

### 5. Finance
- Fee structure configuration (per programme/level/session)
- Invoice generation
- Payment recording with multiple methods
- Receipt generation
- Scholarship management
- Financial reporting

### 6. Library
- Book catalog with categories
- ISBN-based tracking
- Borrowing and return system
- Overdue detection and fine calculation
- Borrower history

### 7. Hostel/Accommodation
- Hostel management by type (Male/Female/Mixed)
- Room allocation with capacity tracking
- Occupancy monitoring
- Maintenance request system

### 8. Communications
- System-wide announcements with audience targeting
- Direct messaging between users
- Notification system
- Priority levels

### 9. Reports & Analytics
- Dashboard with key metrics and charts
- Financial reports with collection trends
- Academic performance analysis
- Attendance reports
- Excel export functionality

## Installation

```bash
# 1. Navigate to the UMS directory
cd ums

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations accounts academics students staff finance library hostel communications
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Seed grade scale (optional)
python manage.py shell -c "
from academics.models import GradeScale
grades = [
    ('A', 70, 100, 5.0, 'Excellent'),
    ('B', 60, 69.99, 4.0, 'Very Good'),
    ('C', 50, 59.99, 3.0, 'Good'),
    ('D', 45, 49.99, 2.0, 'Fair'),
    ('E', 40, 44.99, 1.0, 'Pass'),
    ('F', 0, 39.99, 0.0, 'Fail'),
]
for g, mn, mx, gp, desc in grades:
    GradeScale.objects.get_or_create(grade=g, defaults={'min_score': mn, 'max_score': mx, 'grade_point': gp, 'description': desc})
print('Grade scale created.')
"

# 7. Run the server
python manage.py runserver
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/accounts/token/` | Obtain JWT token |
| POST | `/api/accounts/token/refresh/` | Refresh JWT token |
| GET | `/api/accounts/profile/` | Get user profile |
| GET | `/api/accounts/users/` | List users (admin) |

### Students
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/students/students/` | List students |
| GET | `/api/students/students/{id}/` | Student detail |
| GET | `/api/students/students/{id}/transcript/` | Student transcript |
| GET | `/api/students/enrollments/` | List enrollments |

### Academics
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/academics/departments/` | List departments |
| GET | `/api/academics/courses/` | List courses |
| GET | `/api/academics/sessions/` | List sessions |
| GET | `/api/academics/sessions/current/` | Current session |

### Finance
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/api/finance/invoices/` | List invoices |
| GET | `/api/finance/payments/` | List payments |

## Database Schema (Key Relationships)

```
User (accounts)
├── Student (1:1) ──→ Programme ──→ Department ──→ Faculty
├── StaffProfile (1:1) ──→ Department
├── Enrollment ──→ Course + Semester
├── CourseAllocation ──→ Course + Lecturer + Semester
├── StudentResult ──→ Student + CourseAllocation
├── Invoice ──→ Student + Session
├── Payment ──→ Invoice + Student
├── Borrowing ──→ Book + User
├── RoomAllocation ──→ Student + Room ──→ Hostel
├── Message ──→ Sender + Recipient
└── Notification ──→ User
```

## User Roles & Permissions

| Feature | Admin | Registrar | Lecturer | Student | Finance | Librarian |
|---------|-------|-----------|----------|---------|---------|-----------|
| User Management | ✓ | - | - | - | - | - |
| Student Records | ✓ | ✓ | View | Own | - | - |
| Course Management | ✓ | ✓ | - | - | - | - |
| Grade Entry | ✓ | - | Own | - | - | - |
| Attendance | ✓ | - | Own | - | - | - |
| Finance | ✓ | - | - | Own | ✓ | - |
| Library | ✓ | - | - | Own | - | ✓ |
| Hostel | ✓ | - | - | - | - | - |
| Reports | ✓ | ✓ | - | - | ✓ | - |
| Announcements | ✓ | ✓ | Create | View | - | - |

## Production Deployment

For production, update `settings.py`:
- Set `DEBUG = False`
- Use PostgreSQL database
- Configure proper `SECRET_KEY`
- Set `ALLOWED_HOSTS`
- Configure email backend (SMTP)
- Use proper static file hosting
- Enable HTTPS

## License

Internal university system - All rights reserved.
