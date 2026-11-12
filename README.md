# VAULT — A Monochrome Password Manager

A self-hosted password manager built with Django. Stored credentials are
encrypted with Fernet (AES-128 + HMAC-SHA256); master passwords are hashed
with Argon2. The UI is intentionally retro: black and white only, monospace
type, inverting buttons, no colors, no icons.

---

## Features

- **Registration & login** with a master password (Argon2-hashed)
- **Add / view / edit / delete** saved credentials
  (website, username, password, notes)
- **Encrypted storage** — every saved password is encrypted with Fernet
  before touching the database
- **Per-user vault isolation** — one user cannot access another user's
  entries, even by guessing the URL
- **Retro monochrome UI** — black background, white text, Courier, no
  rounded corners, no shadows
- **Flash messages** on create / update / delete
- **Per-view access control** via `@login_required` and queryset filtering
- **Strong master password enforcement** — minimum 12 characters with
  uppercase, lowercase, digit, and special character requirements
- **Password generator** — one-click generation of a cryptographically
  secure 16-character password when adding or editing an entry

---

## Tech Stack

| Layer | Choice | Version |
| :--- | :--- | :--- |
| Language | Python | 3.10 |
| Framework | Django | 5.2.19 (LTS) |
| Database | SQLite (development) | bundled |
| Password hashing | Argon2 (via `django[argon2]`) | argon2-cffi 25.1.0 |
| Symmetric encryption | Fernet (`cryptography`) | 50.0.2 |
| Config | python-dotenv | 1.2.4 |

No DRF, no separate JavaScript frontend. Django templates, forms, and session
auth are sufficient for a single-client server-rendered application.

---

## Security Architecture

### Two separate password concerns

A password manager deals with **two different kinds of passwords**, stored and
protected in two different ways. Conflating them is the most common mistake in
beginner password-manager projects.

| | **Master password** | **Stored passwords** |
| :--- | :--- | :--- |
| Purpose | Login to this app | Saved credentials for other sites |
| Where entered | Login / registration page | "Add New Entry" form (post-login) |
| How protected | Argon2 **hash** (one-way) | Fernet **encryption** (reversible) |
| Who can read it | Only the user (server can't) | Only the logged-in user |

### Flow

```
REGISTER  ──► master password ──► Argon2 hash ──► auth_user table
LOGIN     ──► master password ──► Argon2 hash ──► compared to stored hash
ADD ENTRY ──► site password   ──► Fernet encrypt ──► vault_vaultentry table
VIEW      ──► ciphertext      ──► Fernet decrypt ──► shown to logged-in user
```

### What is protected

- **Argon2 hashing** — master passwords are never stored or recoverable
- **Fernet encryption** — saved passwords in the database are ciphertext
  (they begin with `gAAAAA...`), unreadable without the application key
- **CSRF protection** — enabled by default; every POST form includes
  `{% csrf_token %}`
- **Per-user isolation** — `get_object_or_404(VaultEntry, pk=pk, user=request.user)`
  means a user requesting another user's entry receives a `404`
- **`SECRET_KEY` and `DEBUG`** — loaded from `.env`, which is git-ignored
- **`venv/` and `db.sqlite3`** — git-ignored; no secrets in version control

### Known limitations (MVP scope)

Documented deliberately — each is a *decision*, not an oversight:

1. **Fernet key derived from `SECRET_KEY`.** A server administrator with
   access to `SECRET_KEY` could decrypt every vault. A production password
   manager would derive the key from the **user's master password** so even
   the server can't decrypt.
2. **Default session lifetime (14 days).** Django's built-in default. A
   production password manager would use a 15-minute inactivity timeout
   (`SESSION_COOKIE_AGE = 900`, `SESSION_SAVE_EVERY_REQUEST = True`).
3. **No master password re-prompt.** Once logged in, clicking **VIEW**
   immediately reveals a password.
4. **No 2FA.** No TOTP, no hardware key.
5. **No rate limiting** on login attempts.
6. **SQLite database** — fine for local use; multi-user deployment should
   move to PostgreSQL.
7. **`DEBUG=True`** in development — must be `False` in production, with
   `ALLOWED_HOSTS` configured.

---

## Setup

```bash
git clone https://github.com/alankamei/passWordmanagementSys.git
cd passWordmanagementSys

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# paste the output as SECRET_KEY='...' in .env

python3 manage.py migrate
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

**Requirements:** Python 3.10 or newer, Linux / macOS / WSL.

---

## Usage

1. Click **REGISTER** and create an account. This sets your **master
   password** — it is hashed and cannot be recovered.
2. Click **+ ADD NEW ENTRY** and fill in website, username, password, and
   optional notes.
3. The password field is shown as plain text **while you type** so you can
   verify it; it is encrypted before being stored.
4. Click **VIEW** on any row to decrypt and display the saved password.
5. Click **EDIT** to change fields, **DELETE** to remove an entry.
6. Click **LOG OUT** when finished.

---

## Project Structure

```
password_manager_project/
├── config/                          Django project settings and root URLs
│   ├── settings.py                  settings, PASSWORD_HASHERS, dotenv wiring
│   └── urls.py                      includes vault.urls and auth.urls
├── vault/                           main application
│   ├── models.py                    VaultEntry model
│   ├── forms.py                     RegisterForm, VaultEntryForm
│   ├── views.py                     register, list, create, detail, update, delete
│   ├── urls.py                      app URL routes
│   ├── utils.py                     encrypt_password / decrypt_password (Fernet)
│   ├── migrations/
│   ├── static/vault/style.css       monochrome stylesheet
│   └── templates/
│       ├── registration/login.html
│       └── vault/
│           ├── base.html
│           ├── home.html
│           ├── register.html
│           ├── list.html
│           ├── form.html
│           ├── detail.html
│           └── confirm_delete.html
├── .env                             LOCAL ONLY — git-ignored
├── .env.example                     template committed to Git
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## Future Enhancements

- **Per-user encryption keys** — derive the Fernet key from the user's
  master password so the server cannot decrypt vaults
- **Master password re-prompt** before revealing any password
- **Session inactivity timeout** (`SESSION_COOKIE_AGE = 900`)
- **Password generator** with configurable length and character classes
- **Copy-to-clipboard** button on the detail page
- **Search / filter** on the list view
- **Password strength meter** (`zxcvbn`)
- **Two-factor authentication** via `django-otp`
- **Change master password** flow (`PasswordChangeView`)
- **PostgreSQL + production deployment** (Gunicorn, Nginx, HTTPS,
  `DEBUG=False`, `ALLOWED_HOSTS`, Whitenoise for static files)

---


## License

Educational project. No warranty. Do not use as a production password
manager without addressing every item in **Known Limitations**.