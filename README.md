# Django Quotes Project

A dynamic and feature-rich web application for collecting, sharing, and rating quotes from movies and books. This project is built with Django and demonstrates a range of functionalities including database modeling, asynchronous voting, fuzzy string matching for duplicate prevention, and deployment on a live server using Nginx and Gunicorn.

## Live Demo

You can view the live version of this project here:
https://quotes-project.chickenkiller.com

*(Note: If the server is offline for maintenance, please check back later.)*

## Features

- **Random Quote Display**: The homepage displays a random quote from the database, with the probability of appearance weighted by its `weight` attribute.
- **Add Quotes**: Any visitor can add new quotes, specifying the text, the source (e.g., a movie title or book name), and the source type (Movie/Book).
- **Smart Duplicate Prevention**:
    - **Exact Match Blocking**: The system uses text normalization (lowercase, punctuation removal) to prevent identical quotes from being added.
    - **Fuzzy Matching Warning**: If a user tries to submit a quote that is very similar (>90% similarity) to an existing one, the system displays a warning and asks for confirmation before proceeding.
- **Voting System**: Users can upvote (like) and downvote (dislike) quotes. Votes are tracked per session to allow one vote per quote per user session.
- **Top Quotes Page**: A "Top 10" page that ranks quotes based on the total number of likes.
- **Quote Listing and Search**: A comprehensive list of all quotes with a built-in search functionality to filter by quote text or source name.
- **Source Management**:
    - Automatic creation of new sources (movies/books) if they don't already exist.
    - A limit of a maximum of 3 quotes per source to ensure content diversity.
- **Admin Panel**: A fully configured Django admin panel for easy management of quotes, sources, and votes.

## Tech Stack

- **Backend**: Django 5.x, Python 3.10+
- **Database**: SQLite.
- **Frontend**: Plain HTML5, CSS3 (no JavaScript frameworks).
- **Key Python Libraries**:
    - `django`: The core web framework.
    - `gunicorn`: WSGI HTTP Server for production deployment.
    - `fuzzywuzzy`: Library for fuzzy string matching to detect similar quotes.
- **Deployment**:
    - **Server**: Ubuntu/Debian Linux
    - **Web Server**: Nginx (as a reverse proxy)
    - **Process Manager**: Systemd (for managing the Gunicorn service)
    - **SSL/TLS**: Let's Encrypt with Certbot for HTTPS.

## Project Structure

```markdown
<details>
  <summary><b>Project Structure</b></summary>

```text
quotes-project/
├── project/
├── quotes/
│   ├── migrations/
│   ├── templates/
│   │   └── quotes/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── static/
│   └── css/
│       └── base.css
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
</details>
```
## Local Development Setup

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/veanyk/quotes-project.git
    cd quotes-project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser** to access the admin panel:
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000/`.
The admin panel will be at `http://127.0.0.1:8000/admin/`.

## Key Code Highlights

### Smart Validation in `forms.py`

The `QuoteForm` contains custom validation logic in its `clean()` method to handle business rules before saving data:
- It checks for exact duplicates using normalized text.
- It enforces the 3-quotes-per-source limit.
- It uses `fuzzywuzzy` to detect similar quotes and raises a special `ValidationError` with a code `similar_quote`, which is then handled by the template to show a confirmation dialog.

```bash
# quotes/forms.py
from fuzzywuzzy import fuzz

class QuoteForm(forms.ModelForm):
    def clean(self):
        # ...
        normalized_new = normalize_text(text)
        
        # Check for exact duplicates
        if Quote.objects.filter(normalized_text=normalized_new).exists():
            raise ValidationError("This quote already exists.")

        # Check for similar quotes if not confirmed by user
        if not confirmed:
            for quote in existing_quotes:
                similarity_ratio = fuzz.ratio(normalized_new, quote.normalized_text)
                if similarity_ratio > 90:
                    raise ValidationError("Found a similar quote. Please confirm.", code='similar_quote')
        # ...
```

### Weighted Random Quote in models.py
The QuoteQuerySet includes a custom method weighted_random() that selects a quote based on its weight field, ensuring that more important quotes appear more frequently. It also excludes the last seen quote (stored in the session) to avoid immediate repetition.

```bash
# quotes/models.py (simplified example)
class QuoteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, weight__gt=0)

    def weighted_random(self, exclude_pk=None):
        qs = self.active()
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)

        agg = qs.aggregate(total=Sum("weight"))
        total = agg.get("total") or 0
        if total <= 0:
            return None

        import random
        r = random.randint(1, int(total))
        cumulative = 0
        for row in qs.values("id", "weight").order_by("id"):
            cumulative += row["weight"]
            if cumulative >= r:
                return self.get(pk=row["id"])
        return None
```

Contact
Created by Veanyk - feel free to contact me!