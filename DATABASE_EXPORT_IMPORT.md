# Database Export/Import Feature Documentation

## Overview
The Hospital Meal System (HMS) now includes comprehensive database export and import functionality for data backup and portability. This feature allows superusers and admins to export all database records to JSON format and import them back into the system.

## Features

### 1. **Management Commands**
Django management commands for command-line export/import operations:

#### Export Database
```bash
python manage.py export_db
# Optional: Specify custom output path
python manage.py export_db --output /path/to/export.json
```

**Output:**
- Creates `media/backups/db_export_TIMESTAMP.json` by default
- Contains all app data (students, academics, finance, staff, library, hostel, communications)
- Excludes system models (auth, sessions, contenttypes)
- Default timestamp format: `YYYYMMDD_HHMMSS`

#### Import Database
```bash
python manage.py import_db media/backups/db_export_20260614_193953.json
# Optional: Clear existing data before import
python manage.py import_db media/backups/db_export_20260614_193953.json --clear
```

**Features:**
- Validates JSON file format before import
- Skips system models for security
- Provides confirmation prompt when using `--clear` flag
- Records count and handles errors gracefully

### 2. **REST API Endpoints**
HTTP endpoints for programmatic export/import:

#### Export API
- **Endpoint:** `POST /accounts/api/db/export/`
- **Authentication:** Login required (superuser/admin only)
- **Response:** JSON file download
- **Status Codes:**
  - `200`: Successful export
  - `403`: Permission denied
  - `500`: Export error

**Example:**
```bash
curl -X POST http://localhost:8000/accounts/api/db/export/ \
  -H "X-CSRFToken: {csrf_token}" \
  -b "csrftoken={csrf_token}"
```

#### Import API
- **Endpoint:** `POST /accounts/api/db/import/`
- **Authentication:** Login required (superuser/admin only)
- **Request:** Multipart form data with JSON file
- **Response:** JSON response with import status
- **Status Codes:**
  - `200`: Successful import
  - `400`: Invalid file format
  - `403`: Permission denied
  - `500`: Import error

**Example:**
```bash
curl -X POST http://localhost:8000/accounts/api/db/import/ \
  -H "X-CSRFToken: {csrf_token}" \
  -F "file=@db_export.json" \
  -b "csrftoken={csrf_token}"
```

**Response Format:**
```json
{
  "success": true,
  "message": "Imported 317 records",
  "imported": 317,
  "errors": []
}
```

### 3. **Web Interface**
User-friendly dashboard for export/import operations:

- **URL:** `/accounts/db-management/`
- **Access:** Superusers and admins only
- **Features:**
  - One-click export with automatic download
  - File upload for import
  - Optional "Clear existing data" checkbox
  - Progress indicators during operations
  - Success/error notifications

## Data Format

### Export Format
The exported JSON follows Django's serialization format:

```json
[
  {
    "model": "students.student",
    "pk": 1,
    "fields": {
      "user": 1,
      "student_id": "STU001",
      "status": "active",
      ...
    }
  },
  ...
]
```

### Supported Models
All app models except system models:
- **academics:** Course, Programme, Department, Faculty, AcademicSession, etc.
- **students:** Student, AdmissionApplication, Enrollment, etc.
- **finance:** Invoice, Payment, FeeStructure, etc.
- **staff:** Staff, Position, etc.
- **library:** Book, Category, Borrowing, etc.
- **hostel:** Room, Allocation, Maintenance, etc.
- **communications:** Message, etc.
- **reports:** Report records

## Usage Scenarios

### 1. Regular Database Backups
```bash
# Schedule daily exports
0 2 * * * cd /path/to/ums && python manage.py export_db
```

### 2. Development Environment Setup
1. Export production database
2. Transfer to development environment
3. Import into development database
```bash
python manage.py import_db db_export_prod.json
```

### 3. Testing and Staging
Create realistic test data by importing production exports into test environments.

### 4. Data Migration
Export from one HMS instance and import into another without manual data entry.

## Security Considerations

1. **Authentication:** All operations require login and admin/superuser role
2. **CSRF Protection:** API endpoints protected by Django CSRF middleware
3. **File Validation:** Imported files validated before processing
4. **System Models:** Auth system models excluded for security
5. **Confirmation Dialogs:** `--clear` flag requires explicit confirmation
6. **Error Handling:** Detailed error reporting without exposing sensitive data

## Backup Best Practices

1. **Regular Exports:** Schedule daily/weekly exports
2. **Backup Storage:** Keep exports in secure, accessible location
3. **Version Control:** Track export timestamps
4. **Test Imports:** Periodically test imports to ensure data integrity
5. **Off-site Storage:** Store critical backups off-site

## Troubleshooting

### Export Issues

**Problem:** "Export failed: Permission denied"
- **Solution:** Ensure user is superuser or admin

**Problem:** "No data found"
- **Solution:** Database may be empty; proceed with import if intended

### Import Issues

**Problem:** "Invalid JSON file"
- **Solution:** Ensure file is valid JSON exported from export_db command

**Problem:** "Import failed: Unique constraint violation"
- **Solution:** Try importing with `--clear` to avoid duplicates

**Problem:** "Some records skipped with errors"
- **Solution:** Check error messages; may be due to missing foreign key references

## Technical Details

### File Structure
```
media/
  backups/
    db_export_20260614_193953.json  (105KB)
    db_export_20260614_180000.json  (105KB)
    ...
```

### Database Operations
- **Export:** Reads all models, serializes to JSON, writes to file
- **Import:** Parses JSON, deserializes records, saves to database
- **Record Count:** 317+ records (includes all app data)

### Performance
- **Export Time:** ~1-2 seconds for 300+ records
- **Import Time:** ~5-10 seconds for 300+ records (per-record validation)
- **File Size:** ~100KB per complete database backup

## Future Enhancements

1. Compressed backup format (ZIP)
2. Incremental backups (delta-sync)
3. Scheduled exports via Celery
4. Backup history UI with restore point selection
5. Email notifications on export completion
6. Data validation and integrity checks
7. Selective model export/import

---

**Last Updated:** 2026-06-14  
**Version:** 1.0
