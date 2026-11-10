"""
Fetch "currently reading" and "recently finished" books from Hardcover.

Requires: pip install requests

Set your API token (from https://hardcover.app/account/api) in an
environment variable before running:
    Windows:   set HARDCOVER_API_TOKEN=Bearer eyJhbGciOi...
    Mac/Linux: export HARDCOVER_API_TOKEN="Bearer eyJhbGciOi..."

---------------------------------------------------------------------------
GraphQL in 30 seconds
---------------------------------------------------------------------------
GraphQL is just an HTTP POST to ONE URL. The body is JSON with two keys:
    {"query": "<the query text>", "variables": {...}}
The query text lists exactly which fields you want back, and the response
JSON has the same shape under a "data" key. If something is wrong, the
server still usually returns HTTP 200, but with an "errors" list in the
body, so you have to check for that yourself (run_query() below does).

`$name: Type!` in a query declares a variable; you pass its value in the
"variables" dict. `where`, `order_by` and `limit` work like SQL's
WHERE / ORDER BY / LIMIT.
---------------------------------------------------------------------------
"""

import os
import requests

API_URL = "https://api.hardcover.app/v1/graphql"

# Hardcover's status_id values for a book on your shelves
STATUS_WANT_TO_READ = 1
STATUS_CURRENTLY_READING = 2
STATUS_READ = 3

# The fields we want for each book. Reused by every query below.
BOOK_FIELDS = """
    id
    title
    slug
    pages
    release_year
    image { url }
    contributions { author { name } }
"""


def _token():
    token = os.environ.get("HARDCOVER_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Set the HARDCOVER_API_TOKEN environment variable.")
    if not token.lower().startswith("bearer "):
        token = "Bearer " + token
    return token


def run_query(query, variables=None):
    """Send one GraphQL query and return its "data" part."""
    resp = requests.post(
        API_URL,
        json={"query": query, "variables": variables or {}},
        headers={
            "authorization": _token(),
            "content-type": "application/json",
            "user-agent": "reading-tracker-script",
        },
        timeout=30,
    )
    if resp.status_code == 401:
        raise RuntimeError("Hardcover rejected the token (expired or invalid).")
    resp.raise_for_status()

    payload = resp.json()
    if payload.get("errors"):
        messages = "; ".join(e.get("message", str(e)) for e in payload["errors"])
        raise RuntimeError(f"GraphQL error: {messages}")
    return payload["data"]


def get_my_user_id():
    data = run_query("query { me { id username } }")
    me = data["me"]
    if isinstance(me, list):  # Hardcover returns `me` as a one-item list
        me = me[0]
    return me["id"]


def _to_record(user_book):
    """Flatten one user_book result into a simple dict for the database."""
    book = user_book["book"]
    reads = user_book.get("user_book_reads") or []
    latest_read = reads[-1] if reads else {}
    return {
        "book_id": book["id"],
        "title": book["title"],
        "authors": ", ".join(
            c["author"]["name"] for c in book.get("contributions") or [] if c.get("author")
        ),
        "pages": book.get("pages"),
        "release_year": book.get("release_year"),
        "cover_url": (book.get("image") or {}).get("url"),
        "book_url": f"https://hardcover.app/books/{book['slug']}" if book.get("slug") else None,
        "date_started": latest_read.get("started_at"),
        "date_finished": latest_read.get("finished_at") or user_book.get("last_read_date"),
        "progress_pages": latest_read.get("progress_pages"),
    }


def get_currently_reading(user_id):
    query = f"""
    query CurrentlyReading($userId: Int!) {{
      user_books(where: {{user_id: {{_eq: $userId}}, status_id: {{_eq: {STATUS_CURRENTLY_READING}}}}}) {{
        book {{ {BOOK_FIELDS} }}
        user_book_reads {{ started_at finished_at progress_pages }}
      }}
    }}
    """
    data = run_query(query, {"userId": user_id})
    return [_to_record(ub) for ub in data["user_books"]]


def get_recently_finished(user_id, n=2):
    # First choice: let Hardcover sort by the date you last finished each book.
    query = f"""
    query RecentlyFinished($userId: Int!, $limit: Int!) {{
      user_books(
        where: {{user_id: {{_eq: $userId}}, status_id: {{_eq: {STATUS_READ}}}}}
        order_by: {{last_read_date: desc_nulls_last}}
        limit: $limit
      ) {{
        last_read_date
        book {{ {BOOK_FIELDS} }}
        user_book_reads {{ started_at finished_at progress_pages }}
      }}
    }}
    """
    try:
        data = run_query(query, {"userId": user_id, "limit": n})
        return [_to_record(ub) for ub in data["user_books"]]
    except RuntimeError as err:
        if "GraphQL error" not in str(err):
            raise
        # Fallback if the API won't sort on last_read_date: grab the most
        # recently added read books and sort by finish date here in Python.
        fallback = f"""
        query RecentlyFinishedFallback($userId: Int!) {{
          user_books(
            where: {{user_id: {{_eq: $userId}}, status_id: {{_eq: {STATUS_READ}}}}}
            order_by: {{id: desc}}
            limit: 50
          ) {{
            book {{ {BOOK_FIELDS} }}
            user_book_reads {{ started_at finished_at progress_pages }}
          }}
        }}
        """
        data = run_query(fallback, {"userId": user_id})
        records = [_to_record(ub) for ub in data["user_books"]]
        records.sort(key=lambda r: r["date_finished"] or "", reverse=True)
        return records[:n]


if __name__ == "__main__":
    from pprint import pprint

    uid = get_my_user_id()
    print("Currently reading:")
    pprint(get_currently_reading(uid))
    print("\nLast two finished:")
    pprint(get_recently_finished(uid, 2))
