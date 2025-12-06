# 🛠 Recommended Tools for "Eskhata Bank" Project

## 1. Debugging & Development
| Tool | Package Name | Why it makes life easier |
|------|--------------|--------------------------|
| **Django Debug Toolbar** | `django-debug-toolbar` | **MUST HAVE.** Shows SQL queries, headers, error tracebacks, and template context directly in the browser side-panel. Best way to debug 500 errors. |
| **Django Extensions** | `django-extensions` | Adds `shell_plus` (auto-imports all models), `show_urls`, and graph generators. Saves typing in the console. |

## 2. UI & Forms
| Tool | Package Name | Why it makes life easier |
|------|--------------|--------------------------|
| **Crispy Forms** | `django-crispy-forms` `crispy-bootstrap5` | Renders beautiful Bootstrap 5 forms with one line: `{{ form|crispy }}`. Handles errors and layout automatically. No more manual HTML inputs! |
| **Django Widget Tweaks** | `django-widget-tweaks` | Allows adding CSS classes to form fields in templates without changing Python code. `{% render_field form.email class="form-control" %}` |

## 3. Data & APIs
| Tool | Package Name | Why it makes life easier |
|------|--------------|--------------------------|
| **Requests** | `requests` | Much easier than `urllib` for making HTTP requests (e.g., fetching real currency rates from an external API). |
| **Pandas** | `pandas` | (Already installed) Use it! It makes Case 4 (Expense Analysis) much shorter. Instead of manual loops, use `df.groupby('category').sum()`. |

## 4. Code Quality
| Tool | Package Name | Why it makes life easier |
|------|--------------|--------------------------|
| **Black** | `black` | "The Uncompromising Code Formatter". Run it, and your code is instantly perfectly formatted. No more arguments about indentation. |

---

## ⚡ Quick Start: Install the Essentials

Run this to install the most impactful tools:

```bash
pip install django-debug-toolbar django-crispy-forms crispy-bootstrap5 django-extensions
```

Then add to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

INTERNAL_IPS = ["127.0.0.1"]
```
