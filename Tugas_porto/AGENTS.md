# AI Agent Guide - Portfolio Application

This is a **Flask-based portfolio application** with an admin dashboard for managing portfolio content (projects, skills, experiences). The codebase uses Python backend with HTML/CSS/JS frontend.

## Quick Start

### Setup & Run
```bash
# Install dependencies
pip install flask flask-cors python-dotenv mysql-connector-python PyJWT werkzeug cloudinary resend

# Run the Flask app
python app.py
```

**Default admin credentials** (when database unavailable):
- Username: `admin`
- Password: `password123`

### Environment Configuration
All configuration is driven by environment variables in `.env` file. Key variables:
- `DB_TYPE`: `mysql` or `sqlite` (default: mysql)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: MySQL connection details
- `DB_FALLBACK_TO_SQLITE`: Fallback to SQLite if MySQL unavailable (default: False)
- `SECRET_KEY`: JWT secret for token signing
- `CLOUDINARY_*`: Image upload configuration
- `RESEND_API_KEY`: Email service API key

## Architecture

### Backend Structure
```
Backend/
├── admin/                 # Admin-only endpoints (CRUD operations)
│   ├── login.py          # Authentication & JWT token generation
│   ├── dashboard.py      # Statistics and overview
│   ├── profiles.py       # User profile management
│   ├── experience.py     # Experience/work history CRUD
│   ├── projects.py       # Project portfolio CRUD
│   ├── skills.py         # Skills CRUD
│   └── upload.py         # Cloudinary file upload integration
└── utama/
    └── utama.py          # Public endpoints (read-only)
```

### Frontend Structure
```
Frontend/
├── admin/                 # Admin dashboard (authenticated)
│   ├── dashboard.html
│   ├── login.html
│   ├── profile.html
│   ├── experience.html
│   ├── project.html
│   ├── skill.html
│   ├── css/dashboard.css
│   └── js/api.js, dashboard.js
└── utama/                 # Public portfolio pages
    ├── css/style.css
    └── js/script.js
```

### Database Layer (`model.py`)
- **Singleton pattern**: `Database()` returns single instance with connection pooling
- **Supports MySQL & SQLite**: Automatic fallback if MySQL unavailable
- **Methods**:
  - `execute_query()`: Execute SELECT/INSERT/UPDATE/DELETE
  - `create_admin()`: Initialize default admin user
  - Connection pooling for MySQL (pool_size=5)

### Configuration (`config.py`)
- Centralized `Config` class with all environment variables
- Database configuration for MySQL and SQLite
- TiDB Cloud support (MySQL-compatible)
- Third-party API keys (Cloudinary, Resend)

## Key Patterns & Conventions

### Authentication
- **JWT-based**: Tokens signed with `SECRET_KEY` using HS256
- **Decorator pattern**: Use `@token_required` on protected endpoints
- **Token sources** (in priority order):
  1. `Authorization: Bearer <token>` header (for API/fetch requests)
  2. Session cookie fallback (for direct browser navigation)

```python
@login_bp.route('/protected')
@token_required
def protected_endpoint(current_user):
    # current_user contains the user_id from token
    pass
```

### API Endpoints Pattern
- All endpoints are Flask blueprints registered in `app.py`
- Endpoints return JSON responses
- Authentication-required endpoints use `@token_required` decorator
- Standard REST pattern: GET (read), POST (create), PUT (update), DELETE (delete)

Example public endpoint:
```python
@utama_bp.route('/api/projects', methods=['GET'])
def get_projects():
    # Public read-only endpoint
    return jsonify({'data': projects})
```

Example admin endpoint:
```python
@admin_bp.route('/api/projects', methods=['POST'])
@token_required
def create_project(current_user):
    # Admin-only endpoint, requires valid JWT token
    return jsonify({'success': True})
```

### Database Queries
- Use `Database().execute_query(sql, params, fetch=True/False)`
- Always use parameterized queries (`%s` placeholders) to prevent SQL injection
- `fetch=True` returns all rows, `fetch=False` for INSERT/UPDATE/DELETE

```python
db = Database()
users = db.execute_query(
    "SELECT * FROM users WHERE username = %s",
    (username,),
    fetch=True
)
```

### File Uploads
- Images uploaded via Cloudinary API (not local storage)
- See `Backend/admin/upload.py` for implementation
- Configuration in `config.py` (CLOUDINARY_* env vars)

### Error Handling
- Endpoints should catch database exceptions and fallback gracefully
- See `login.py` for example: fallback to hardcoded admin if DB unavailable
- Log exceptions using Python `logging` module for debugging

### Language & Comments
- Code comments written in **Indonesian** (Bahasa Indonesia)
- API responses can be in Indonesian or English
- Variable/function names follow camelCase for JavaScript, snake_case for Python

## Testing

Test files available in `tests/`:
- `test_public_endpoints.py`: Test public API endpoints
- `test_admin_uploads.py`: Test file upload functionality

Run tests:
```bash
python -m pytest tests/
```

## API Endpoints Reference

See [README.md](README.md) for complete API endpoint documentation.

### Main Endpoint Groups
- **Authentication**: `/api/login`, `/api/logout`, `/api/auth/check`
- **Dashboard**: `/api/dashboard/stats`, `/api/dashboard/recent-activity`
- **Profiles**: `/api/profil` (public) and `/api/akun` (admin)
- **Content CRUD**: `/api/experiences`, `/api/projects`, `/api/skills`
- **Uploads**: `/api/upload`

## Common Tasks

### Adding a New Admin Endpoint
1. Create a new route function in `Backend/admin/*.py`
2. Use `@token_required` decorator for authentication
3. Register blueprint in `app.py`
4. Create corresponding frontend form in `Frontend/admin/*.html`
5. Add JavaScript handler in `Frontend/admin/js/api.js`

### Modifying Database Schema
1. Update query in relevant `Backend/admin/*.py` file
2. Test with both MySQL and SQLite (check `model.py` compatibility)
3. If adding new tables, update `_initialize_mysql()` and `_initialize_sqlite()` in `model.py`

### Debugging Database Issues
- Check `.env` file for correct database credentials
- MySQL may fallback to SQLite automatically if connection fails
- Enable `DB_FALLBACK_TO_SQLITE=True` to test SQLite mode
- Check logs for "Database unavailable" messages

### Handling CORS Issues
- CORS is enabled for all origins (configured in `app.py`)
- If frontend can't reach backend, verify both are running and check browser console for CORS errors

## Important Notes

⚠️ **Security**: The hardcoded default admin credentials in `login.py` are for development/fallback only. Ensure proper database setup in production.

⚠️ **Environment Variables**: Never commit `.env` file to git. It contains sensitive API keys and database credentials.

⚠️ **HTTPS in Production**: Change `SECRET_KEY` and use proper authentication in production. The current implementation is suitable for portfolio/learning purposes.

## Tools & Dependencies

| Tool | Purpose |
|------|---------|
| Flask | Web framework |
| flask-cors | CORS support |
| python-dotenv | Environment variable loading |
| mysql-connector-python | MySQL driver |
| PyJWT | JWT token generation/verification |
| werkzeug | Password hashing (security) |
| cloudinary | Cloud image storage |
| resend | Email API for contact form |

## Links to Documentation

- [README.md](README.md) - Complete API endpoint reference and installation guide
- [Backend/admin/](Backend/admin/) - Individual endpoint implementations
- [Frontend/admin/](Frontend/admin/) - Admin dashboard UI
- [config.py](config.py) - Configuration reference
- [model.py](model.py) - Database abstraction layer
