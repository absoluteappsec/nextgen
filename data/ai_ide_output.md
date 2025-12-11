# 1. APPLICATION BEHAVIOR ANALYSIS

## 1.1 Business Purpose

- **Primary function**
  - Multi-user task/project management web app.
  - Users manage:
    - **Projects** ([Project](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:21:0-51:20) model)
    - **Tasks** ([Task](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:54:0-79:43) model)
    - **Notes** ([Notes](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:82:0-91:24) model)
    - **Files** ([File](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:94:0-101:24) model)
    - **User profiles** with PII ([UserProfile](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:11:0-18:78) model).
  - UI and REST API:
    - HTML views under `/taskManager/` ([taskManager/taskManager_urls.py](cci:7://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/taskManager_urls.py:0:0-0:0)).
    - DRF viewsets under `/api/` (`taskManager/urls.py`, [taskManager/serializers.py](cci:7://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/serializers.py:0:0-0:0)).

- **Critical workflows**
  - **User registration & login**:
    - Registration: [register](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:516:0-562:59) (`taskManager/views.py:517+`).
    - Login with JWT cookies + Redis lockout: [login](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:59:0-113:56) (`views.py:60–114`).
  - **Password reset**:
    - [reset_password](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:839:0-877:61) (`views.py:839–872`) via short reset tokens.
  - **Role/group management & RBAC**:
    - [manage_groups](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:192:0-247:58) (`views.py:193–248`).
    - Group assignments: `admin_g`, `project_managers`, `team_member`.
  - **Project/task lifecycle**:
    - Project create/edit/delete: [project_create](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:437:0-463:15), [project_edit](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:467:0-496:91), [project_delete](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:499:0-506:45).
    - Task create/edit/delete/complete: [task_create](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:339:0-368:77), [task_edit](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:371:0-400:88), [task_delete](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:403:0-412:71), [task_complete](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:415:0-425:71).
  - **File upload/download**:
    - [upload](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:250:0-303:59), [download](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:306:0-323:19), [download_profile_pic](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:325:0-332:29) (`views.py:250+`).
  - **Search**:
    - [search](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:756:0-777:41) view using raw SQL (`views.py:757–778`).
  - **REST API**:
    - `/api/users`, `/api/userprofiles`, `/api/tasks`, `/api/projects`, `/api/notes`, `/api/files` (`taskManager/urls.py:17–23`, [serializers.py](cci:7://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/serializers.py:0:0-0:0)).

- **Security-sensitive operations**
  - Handling credentials, JWT tokens and DRF tokens.
  - Password reset via short reset tokens stored in DB.
  - Storage and exposure of **SSN**, **DOB**, and profile images.
  - Arbitrary URL-based file retrieval in [upload](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:250:0-303:59) (SSRF vector).
  - Raw SQL queries and `.extra()` queries with user input.

- **Regulatory implications**
  - [UserProfile](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:11:0-18:78) stores **SSN** and **DOB** as plain text (`models.py:12–19`).
  - This immediately raises:
    - **PII/PCI/GLBA** concerns (SSN).
    - **HIPAA**-like expectations if any health data later added.
    - **GDPR/CCPA** obligations due to identifiable data.
  - No visible data retention/erasure policies in code.

## 1.2 Target Audience

- **User types**
  - Internal-like roles:
    - `admin_g` (admin), `project_managers`, `team_member` (`views.py:571–607`).
  - Likely multi-tenant internal teams; app is exposed via web and API, potentially internet-facing.
- **Security implications**
  - If internet-facing with SSNs and weak auth, risk is **very high**.
  - Wide permissions and weak checks around profile/group management suggest easy lateral and vertical escalation by any authenticated user.

## 1.3 Data Handling

- **Data types**
  - **Authentication data**: username, password, JWT tokens, DRF tokens.
  - **PII**:
    - `UserProfile.dob`, `UserProfile.ssn` (`models.py:12–19`).
    - Name, email on `User`.
  - **Business data**: tasks, projects, notes, file metadata ([models.py](cci:7://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:0:0-0:0)).
  - **Files & images** stored under `MEDIA_ROOT` (`settings.py:142–143`).
  - **Reset tokens**: `UserProfile.reset_token`, `reset_token_expiration`.

- **Sensitive data handling**
  - SSN and DOB stored as **plain text** (`models.py:17–18`).
  - [UserProfileSerializer](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/serializers.py:152:0-159:9) exposes these fields via API:
    - `fields = ('uuid', 'image', 'reset_token', 'reset_token_expiration', 'dob', 'ssn', 'user')` (`serializers.py:153–160`).
  - DRF filters allow searching by `ssn` substring (`serializers.py:162–169`).

- **Data flows**
  - Web UI (session + JWT via cookie) → Django views → ORM / raw SQL / Redis / filesystem.
  - REST API: DRF viewsets using `TokenAuthentication` and `IsAuthenticated` (`settings.py:177–184`).
  - File uploads:
    - Browser upload or URL fetch via `requests` in [upload](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:250:0-303:59) (`views.py:250–304`).
    - Files stored via `store_uploaded_file` / `store_url_data` and then DB insert via raw SQL.
  - Password reset:
    - Token set in `UserProfile.reset_token`, checked on `/taskManager/reset_password/`.

- **Data retention**
  - No explicit retention or deletion policies for PII or logs.
  - Logs include **credentials in clear** on failed login (`views.py:106–111`).

---

# 2. LANGUAGE & FRAMEWORK ANALYSIS

## 2.1 Programming Language

- **Language**: Python (Django).
- **Version/stack**:
  - `Django==5.1.4` (`requirements.txt`).
  - Use of legacy patterns (e.g., `RequestContext`, `.extra()`) suggests port from older Django.

- **Language-specific concerns evident**
  - Raw SQL string interpolation (`views.py:765–768`, [project_details](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:614:0-620:65) at `views.py:615–621`).
  - Use of weak hashers: `MD5PasswordHasher` (`settings.py:168`).
  - Insecure logging of secrets.

## 2.2 Framework

- **Django**
  - `INSTALLED_APPS` includes `django.contrib.auth`, `sessions`, DRF, `rest_framework_simplejwt`, `drf_spectacular`, `django-health-check` (`settings.py:63–82`).
  - CSRF middleware **commented out**:
    - `# 'django.middleware.csrf.CsrfViewMiddleware',` (`settings.py:87`).

- **DRF**
  - `REST_FRAMEWORK`:
    - `DEFAULT_AUTHENTICATION_CLASSES`: `TokenAuthentication` only (`settings.py:179–181`).
    - `DEFAULT_PERMISSION_CLASSES`: `IsAuthenticated` (`settings.py:182–184`).
  - JWT via `rest_framework_simplejwt` but used manually via cookies + custom middleware.

- **JWT**
  - `SIMPLE_JWT`:
    - `ACCESS_TOKEN_LIFETIME` and `REFRESH_TOKEN_LIFETIME` set to **365 days** (`settings.py:188–191`).
    - No rotation, no blacklist (`settings.py:192–193`).
    - `SIGNING_KEY = SECRET_KEY` with `SECRET_KEY = 'secret'` (`settings.py:15, 195`).

- **Framework configuration risks**
  - `DEBUG = True` (`settings.py:18`).
  - `ALLOWED_HOSTS = ['*']` (`settings.py:21`).
  - CSRF disabled for **entire app** (`settings.py:84–90`) and several views manually marked `@csrf_exempt` (e.g., [profile_by_id](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:786:0-835:93), [reset_password](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:839:0-877:61)).
  - `PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']` → **MD5** for passwords.

## 2.3 Architecture Pattern

- **Pattern**
  - Monolithic Django app:
    - Traditional Django HTML views (MVC-like).
    - DRF viewsets for API.
    - Shared database (SQLite by default) (`settings.py:100–107`).

- **Security boundaries**
  - No clear separation between admin and user functionality beyond group checks.
  - JWT middleware affects all requests by setting `request.user` from cookie (`middleware.py:13–23`).
  - CSRF disabled, so browser and API share same trust boundary; CSRF on authenticated operations is broadly possible.

## 2.4 Build & Deployment

- **Observed config**
  - Default SQLite DB in code; MySQL example commented out (`settings.py:102–117`).
  - No CI/CD scripts in the inspected files.
  - Static/media paths go to `/tmp/static-tm` and `/tmp/static-tm/taskManager/uploads` (`settings.py:137–143`), suggesting dev/test environment.

- **Deployment-related concerns**
  - Using `DEBUG = True` and `ALLOWED_HOSTS=['*']` in any non-local environment is dangerous.
  - SECRET_KEY hard-coded and trivial.
  - Redis config is hard-coded to `localhost:6379` with no auth (`settings.py:206–211`).

---

# 3. COMPONENTS & LIBRARIES ANALYSIS

## 3.1 Security Components

- **Authentication**
  - Django auth (`django.contrib.auth`).
  - DRF TokenAuth: `rest_framework.authtoken` (`settings.py:78–79`, `views.py:38`).
  - JWT:
    - `rest_framework_simplejwt` (`settings.py:80`, `middleware.py`, `views.py:45–52`).
    - Custom `JWTAuthenticationMiddleware` uses cookie `access_token`:
      - No CSRF protection, no origin checking.
      - On invalid token, sets `AnonymousUser` (`middleware.py:13–25`).

- **Authorization**
  - `login_required` and `user_passes_test` decorators widely used (e.g., [manage_groups](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:192:0-247:58), [project_create](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:437:0-463:15), [view_all_users](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:590:0-593:93)).
  - Ad-hoc `has_perm` checks:
    - `user.has_perm('auth.change_group')`, `'taskManager.add_project'`, `'taskManager.change_project'`, `'taskManager.delete_project'`.
  - **Serious gaps**:
    - [profile_by_id](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:786:0-835:93) is `@login_required` but **CSRF-exempt** and allows arbitrary group additions to any user (`views.py:787–836`).
    - Some views with high impact (e.g., [dashboard](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:724:0-733:46)) are not decorated with `login_required` (`views.py:725–734`).

- **Encryption/crypto**
  - No use of cryptographic hashing for PII fields.
  - Passwords with MD5 hasher.
  - JWT secret is trivially guessable (`'secret'`).

- **Input validation & encoding**
  - Limited validation via Django forms for some views (`UserForm`, `ProfileForm`), but:
    - Raw SQL with direct interpolation of user input in [search](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:756:0-777:41) and [project_details](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:614:0-620:65).
    - Template rendering with potential unescaped data from external HTTP responses in [upload](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:250:0-303:59) error path (`views.py:277`).

## 3.2 Database Components

- **ORM**
  - Standard Django models (SQLite backend by default).
  - Mixed use:
    - Regular ORM queries.
    - Dangerous `.extra()` query: [project_details](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:614:0-620:65) (`views.py:615–621`).
    - Direct SQL in [search](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:756:0-777:41) (`views.py:765–768`).

- **SQL construction**
  - [search](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:756:0-777:41):
    - `sql = "select * from ... WHERE t.text LIKE '%s' OR t.title LIKE '%s' AND a.user_id = %d" % (task_query, task_query, request.user.id)` (`views.py:765–768`).
    - `task_query` derived from `query` → **SQL injection**.
  - [project_details](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:614:0-620:65):
    - `.extra(select={'total_completed_tasks': "100 * (select count(*) ... project_id = %s)/(select count(*) ... project_id = %s)" % (project_id, project_id)})`.
    - `project_id` from URL pattern `(?P<project_id>.+)` → **SQL injection + IDOR**.

- **Parameterized queries**
  - File insert uses parameterized `cursor.execute` with parameters tuple (`views.py:285–288`), which is safer.

## 3.3 Frontend Components

- **Templating**
  - Django templates (`TEMPLATES` config in `settings.py:149–163`).
  - No explicit custom filters for escaping; relies on Django defaults.

- **Client-side security**
  - No CSP/HSTS/secure headers configuration visible.
  - Cookies for JWTs are set with `httponly=False` and `secure=False` (`views.py:85–87`) → accessible to JavaScript, MITM risk on HTTP.

## 3.4 API & Integration Components

- **External services**
  - `requests` for fetching arbitrary URLs in [upload](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:250:0-303:59) (`views.py:269–273`) → **SSRF** potential.
  - `django-health-check` for health endpoints `/ht/` (`taskManager/urls.py:29`).
  - Redis for login lockout (`settings.REDIS`, `views.py:65–101`, [reset_password](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:839:0-877:61)).

- **API security**
  - DRF endpoints under `/api/` use `TokenAuthentication` + `IsAuthenticated`.
  - As long as DRF views are not protected by JWT cookies directly, they require tokens in Authorization header; but CSRF disabled still broadens risk.

- **Secret management**
  - API keys/secrets not seen; but JWT signing key and Django SECRET_KEY are hard-coded insecurely.

---

# 4. DATASTORES & TEMPLATING ANALYSIS

## 4.1 Datastores

- **Primary DB**
  - SQLite: `DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'` (`settings.py:104–107`).
- **Redis**
  - For failed login counters: `REDIS = redis.StrictRedis(host='localhost', port=6379, db=0)` (`settings.py:206–211`).
  - No password/auth, no TLS.

- **Filesystem**
  - `MEDIA_ROOT = '/tmp/static-tm/taskManager/uploads'`.
  - [File](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:94:0-101:24) model stores `path` (string path) and `uuid`, and app reads from filesystem using these.

## 4.2 Database Schema & Sensitive Data

- **Key tables (models)**
  - [UserProfile](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:11:0-18:78):
    - Fields: `image`, `reset_token`, `reset_token_expiration`, `dob`, `ssn`, `uuid` (`models.py:12–19`).
    - **Risk**: SSN & DOB in clear text.
  - [Task](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:54:0-79:43), [Project](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:21:0-51:20), [Notes](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:82:0-91:24), [File](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/models.py:94:0-101:24) as described.

- **Schema security**
  - No DB-level constraints on SSN format beyond `CharField`.
  - Reset tokens short (`CharField(max_length=7)`) and used for auth in [reset_password](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:839:0-877:61).

## 4.3 Data Access Patterns

- **Access control in queries**
  - Many views filter by `users_assigned` or require membership, but:
    - [project_details](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:614:0-620:65) uses `.extra` and `get(pk=project_id.split()[0])` **without** checking project membership.
    - [view_all_users](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:590:0-593:93) restricted to superuser via `@user_passes_test(lambda u: u.is_superuser)`.

- **Potential leakage**
  - DRF [UserProfileViewSet](cci:2://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/serializers.py:174:0-185:52) returns full profile, including SSN, reset_token. It filters by user but staff can see everything; if misconfigured, large data exfil possible.
  - [download_profile_pic](cci:1://file:///Users/kennyjohnson/code/absolute_appsec/vtm/taskManager/views.py:325:0-332:29) returns redirect to arbitrary `user.userprofile.image` without checking requesting user’s rights (`views.py:327–333`).

## 4.4 Templating

- **User data in templates**
  - Login error path for upload uses `_file.decode("utf-8")` inside template context in a very odd expression:
    - `{'data': (_file.decode("utf-8"),"Good effort but we can't give you everything!")["security-credentials" in url], ... }` (`views.py:277`).
    - If remote resource contains HTML/JS and is rendered unescaped, could lead to reflected or stored XSS via SSRF result.

---

# 5. CONFIGURATION & ENVIRONMENT ANALYSIS

## 5.1 Configuration Files

- **`taskManager/settings.py` risks**
  - `SECRET_KEY = 'secret'` (line 15).
  - `DEBUG = True` (line 18).
  - `ALLOWED_HOSTS = ['*']` (line 21).
  - `CSRF` middleware disabled (`settings.py:84–90`, with CSRF line commented).
  - Weak hash: `MD5PasswordHasher` (`settings.py:168`).
  - JWT tokens with 1-year lifetime and no rotation/blacklisting (`settings.py:188–196`).
  - Static/media roots in `/tmp` (possibly OK for dev, but insecure for prod persistence).

- **Hard-coded secrets**
  - JWT signing key is `SECRET_KEY`.
  - No use of `python-decouple` (despite in `requirements.txt`) to externalize secrets.

## 5.2 Environment Variables

- **Usage**
  - Not used in the visible code; all key settings (DB, Redis, secret key) are hard-coded.

- **Risk**
  - Cannot easily vary configuration per environment without code changes.
  - Leakage of configuration from repo → instant compromise of JWT auth, cookie signing, and potentially DB if migrated to MySQL later with similar patterns.

## 5.3 Infrastructure & Logging

- **Logging**
  - Logging configured to `mysite.log`, including debug logs (`settings.py:23–59`).
  - Logs include **usernames and passwords in clear**:
    - `logger.info('Failed login (%s:%s)' % (username, password))` (`views.py:106`).
    - `logger.info('Invalid User (%s:%s)' % (username, password))` (`views.py:110`).
  - This is a severe credential-handling flaw.

- **Network / Web server**
  - No web server config (Nginx/Apache) visible; assume default Django dev server or externally configured reverse proxy.

---

# 6. AUTHENTICATION & AUTHORIZATION ANALYSIS

## 6.1 Authentication

- **Mechanisms**
  - Django username/password login (`login` view).
  - JWT stored as cookies (non-HttpOnly, non-secure).
  - DRF TokenAuthentication for API.
  - Password reset via short token.

- **Credential storage**
  - Passwords stored using MD5 hasher.
  - Logging of plaintext passwords in attempts.

- **Session/JWT handling**
  - JWT cookie parsed by `JWTAuthenticationMiddleware`:
    - Only uses `AccessToken(token)`; no audience, IP, device binding.
    - On error, silently makes user anonymous; may hide tampering.
  - Cookies set with:
    - `httponly=False`, `secure=False` (`views.py:86–87`) → accessible via XSS, transmitted over HTTP.

- **MFA**
  - None observed.

- **Account recovery**
  - `reset_password` validates `reset_token` and expiration:
    - Token stored in `UserProfile.reset_token`.
    - Length 7 → low entropy if not cryptographically generated.
    - No rate limiting or account binding checks beyond token lookup.

## 6.2 Authorization

- **Global approach**
  - Mix of:
    - `login_required`.
    - `user_passes_test`.
    - `has_perm`.
    - Custom group checks (`request.user.groups.filter(name='admin_g')` etc.).

- **Notable issues**
  - **Profile editing / privilege escalation**:
    - `profile_by_id` (`views.py:787–836`) is:
      - `@login_required` + `@csrf_exempt`.
      - Allows any logged-in user to:
        - Change another user’s groups by specifying arbitrary `groups` string.
        - Change their name, email, DOB, SSN, password, and profile image.
      - No check that `request.user` matches `user_id` or is admin.
      → **High-severity horizontal & vertical privilege escalation**; CSRF makes this remotely triggerable.
  - **Project/task access checks**
    - Many views rely on `belongs_to_project(request.user, project_id)` (e.g., `task_create`, `task_edit`, `task_delete`, `task_complete`).
    - However `project_details` does **not** check membership; any logged-in user can view project-level info via project ID.
  - **CSRF disabled**:
    - Combined with cookie-based JWT auth, **every state-changing POST is CSRF-vulnerable** unless explicitly protected otherwise.

## 6.3 Security Middleware/Decorators

- **JWTAuthenticationMiddleware**
  - Applied globally (`MIDDLEWARE` in `settings.py:84–91`).
  - Bypasses standard DRF/JWT auth integration and uses cookies directly.
  - No CSRF or origin checks.

- **CSRF**
  - `@csrf_exempt` used on:
    - `profile_by_id` (`views.py:787–789`).
    - `reset_password` (`views.py:839–841`).
  - Combined with cookie auth, this makes critical endpoints easily CSRF’d.

---

# 7. API & ENDPOINT ANALYSIS

## 7.1 HTTP Routes

### Main routes (HTML)

From `taskManager/taskManager_urls.py`:

- **Auth/profile**
  - `/taskManager/register/` → `register`.
  - `/taskManager/login/` → `login`.
  - `/taskManager/logout/` → `logout_view`.
  - `/taskManager/manage_groups/` → `manage_groups`.
  - `/taskManager/profile/` → `profile`.
  - `/taskManager/profile/<user_id>` → `profile_by_id`.
  - `/taskManager/profile_view/<user_id>` → `profile_view`.
  - `/taskManager/change_password/`, `/forgot_password/`, `/reset_password/` (reset is implemented, forgot/change not fully visible).

- **Projects & tasks**
  - `/taskManager/project_create`, `/<project_id>/edit_project`, `/manage_projects`, `/<project_id>/project_delete`, `/<project_id>/project_details`.
  - `/<project_id>/task_create`, `/<project_id>/<task_id>`, `/<project_id>/task_edit/<task_id>`, `/<project_id>/task_delete/<task_id>`, `/<project_id>/task_complete/<task_id>`, `/task_list`, `/<project_id>/manage_tasks`.

- **Notes**
  - `/<project_id>/<task_id>/note_create`, `note_edit`, `note_delete`.

- **Files**
  - `/download/<file_id>`, `/<project_id>/upload`, `/downloadprofilepic/<user_id>`.

- **Misc**
  - `/dashboard`, `/search`, `/settings`, `/view_img`, `/ping`.

### API routes (DRF)

From `taskManager/urls.py`:

- `/api/users/`, `/api/userprofiles/`, `/api/tasks/`, `/api/projects/`, `/api/notes/`, `/api/files/` via router.
- `/api-token/` → DRF auth token.
- `/schema/`, `/swagger-ui/`, `/redoc/` for docs.

## 7.2 Endpoint Security Concerns

- **Unauthenticated/public**
  - `login`, `register`, `reset_password` endpoints are public.
  - Others mostly `login_required`, but CSRF is globally disabled.

- **Validation & sanitization**
  - Significant endpoints with **raw SQL injection risk**:
    - `search` (`views.py:757–778`).
    - `project_details` `.extra()` query (`views.py:615–621`).
  - File upload URL (`upload`):
    - Takes arbitrary URL, performs `requests.get(url, timeout=15)` (`views.py:269`) → SSRF; limited MIME check only.

- **Rate limiting / anti-automation**
  - Only login brute-force protection via Redis counters in `login` view.
  - No rate limiting on sensitive endpoints like `reset_password`, `profile_by_id`, or search.

---

# 8. RISK ANALYSIS & SECURITY RECOMMENDATIONS

## 8.1 Major Vulnerabilities (OWASP Mapping)

- **Broken Access Control (A01:2021)**
  - `profile_by_id` allows any logged-in user to modify any user profile and groups (`views.py:787–836`).
  - `project_details` accessible to any logged-in user without membership check.
  - `download_profile_pic` and other lookups by user_id/file_id without strong authorization checks.

- **Cryptographic Failures (A02:2021)**
  - MD5 password hashing (`settings.py:168`).
  - Hard-coded `SECRET_KEY = 'secret'` (`settings.py:15`).
  - 1-year JWT tokens, no rotation or blacklist (`settings.py:188–196`).
  - SSNs stored in plaintext.

- **Injection (A03:2021)**
  - SQL injection via:
    - `search` raw SQL (`views.py:765–768`).
    - `project_details` `.extra()` with unvalidated project_id (`views.py:615–621`).

- **Insecure Design / CSRF (A04/A08:2021)**
  - CSRF middleware globally disabled.
  - Critical endpoints `profile_by_id`, `reset_password` are `@csrf_exempt`.
  - JWT in cookies but no CSRF protection → broad CSRF on any state-changing endpoint.

- **Security Misconfiguration (A05:2021)**
  - `DEBUG = True`, `ALLOWED_HOSTS=['*']`, hard-coded secrets.
  - Redis unauthenticated localhost connection.

- **Vulnerable & Outdated Components (A06:2021)**
  - Not enough info about patch levels besides `Django==5.1.4`; but the app deliberately uses known-bad patterns.

- **Identification & Authentication Failures (A07:2021)**
  - Logging plaintext credentials.
  - Weak reset token mechanism (short token, no binding besides lookup).
  - Long-lived JWT with insecure transport/storage.

- **Software & Data Integrity Failures / SSRF (A08/A10:2021)**
  - `upload` fetches arbitrary URLs with `requests.get` without restricting to images until after fetch (`views.py:269–273`) → SSRF.
  - Potential XSS via rendering fetched content in template (`views.py:277`).

- **Data Exposure (A02/A01:2017)**
  - `UserProfileSerializer` exposes SSN and reset_token (`serializers.py:153–160`).
  - DRF filters allow ssn substring search (`serializers.py:162–169`).

## 8.2 Security Control Evaluation

- **Effective controls**
  - Use of `login_required` and some `user_passes_test` checks on admin-like views.
  - DRF’s `IsAuthenticated` for API endpoints (given proper token handling).
  - Redis-based login lockout provides basic brute-force mitigation.

- **Inadequate/missing controls**
  - No CSRF protection.
  - Insufficient authorization on critical profile and project views.
  - No encryption for PII fields.
  - No secret management or environment-based configuration.

## 8.3 Third-Party Risk

- **`rest_framework_simplejwt` / `djangorestframework`**
  - Good libraries but misconfigured (token lifetimes, cookies, CSRF).
- **`redis`**
  - Used without authentication; if exposed, attacker can reset counters, etc.
- **`requests` SSRF**
  - Any network resource accessible to the server can be queried by attackers via `upload`.

## 8.4 Prioritized Recommendations

### High Priority (Immediate)

- **Fix access control & CSRF**
  - Re-enable `CsrfViewMiddleware` in `MIDDLEWARE`.
  - Remove `@csrf_exempt` from `profile_by_id` and `reset_password` or add alternative CSRF protection.
  - In `profile_by_id`, enforce:
    - Either: `user_id == request.user.id`, or
    - Admin-only access with strict group/permission check.
  - Add membership checks (e.g., `belongs_to_project`) to `project_details` and any other project/task views.

- **Eliminate credential leakage & weak crypto**
  - Remove logging of passwords in all `logger.info('...(%s:%s)'...)` lines (`views.py:106–111`).
  - Replace `MD5PasswordHasher` with Django’s default PBKDF2 or better.
  - Change `SECRET_KEY` to a strong, random value and load from environment; rotate it.
  - Reduce JWT token lifetimes drastically (minutes, not days) and enable rotation/blacklisting.

- **Fix SQL injection**
  - Rewrite `search` to use ORM filtering rather than raw SQL:
    - `Task.objects.filter(users_assigned=request.user.id, text__icontains=query) | Task.objects.filter(..., title__icontains=query)`.
  - Replace `.extra()` in `project_details` with ORM annotations or at least parameterized raw queries.

- **Restrict PII exposure**
  - Remove `ssn`, `reset_token`, and possibly `dob` from `UserProfileSerializer`.
  - Add explicit PII access controls on user profile endpoints (admin-only or self-only).

### Medium Priority

- **Secure file handling**
  - In `upload`:
    - Restrict URL schemes to http/https.
    - Use allowlist for domains or disallow arbitrary URLs in production.
    - Enforce content-type and size limits before storing.
    - Do not render remote content back to template; show generic error instead.
  - Validate that file paths are not attacker-controlled beyond expected patterns; use storage backends rather than manual path building.

- **Harden JWT usage**
  - Use HttpOnly, Secure cookies, and consider SameSite for JWT cookies.
  - Or move JWT to Authorization header and treat browser auth via regular Django sessions with CSRF protection.

- **Encrypt PII at rest**
  - Encrypt SSN and DOB fields, or at least tokenize/mask them.
  - Implement access logging and monitoring for profile data access.

### Lower Priority / Long-Term

- **Configuration management**
  - Move secrets and environment-dependent settings (DB, Redis, SECRET_KEY) to environment variables using `python-decouple` or similar.
  - Separate dev/test/prod settings files.

- **Logging & monitoring**
  - Implement structured logging for security events (auth failures, permission denials) without sensitive data.
  - Integrate with SIEM for anomaly detection if used in production.

- **Defense in depth**
  - Add rate limiting (e.g., via middleware) to login, reset_password, profile update, and search endpoints.
  - Add security headers (CSP, HSTS, X-Content-Type-Options, etc.).

---

## Task Status Summary

- **Analyzed**: authentication/authorization flows, data models and PII handling, configuration and environment, core endpoints and APIs, libraries and integrations.
- **Identified**: multiple high-impact issues (broken access control, SQLi, CSRF, weak crypto, PII exposure, SSRF).
- **Provided**: prioritized remediation recommendations with concrete code locations for reviewers to act on.
