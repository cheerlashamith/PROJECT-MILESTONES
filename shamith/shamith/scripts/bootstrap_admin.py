"""Create or update the single CIH administrator using Supabase Admin REST APIs.

Required environment variables:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
    ADMIN_EMAIL
    ADMIN_PASSWORD

The service-role key and password are never written to the repository.
"""

from __future__ import annotations

import os
import sys

import requests


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    url = required("SUPABASE_URL").rstrip("/")
    service_key = required("SUPABASE_SERVICE_ROLE_KEY")
    email = required("ADMIN_EMAIL").lower()
    password = required("ADMIN_PASSWORD")
    if len(password) < 12:
        raise RuntimeError("ADMIN_PASSWORD must contain at least 12 characters.")

    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{url}/auth/v1/admin/users",
        params={"page": 1, "per_page": 1000},
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    users = payload.get("users", payload if isinstance(payload, list) else [])
    existing = next((user for user in users if str(user.get("email", "")).lower() == email), None)
    attributes = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "app_metadata": {"role": "admin"},
    }

    if existing:
        result = requests.put(
            f"{url}/auth/v1/admin/users/{existing['id']}",
            json=attributes,
            headers=headers,
            timeout=20,
        )
        action = "updated"
    else:
        result = requests.post(
            f"{url}/auth/v1/admin/users",
            json=attributes,
            headers=headers,
            timeout=20,
        )
        action = "created"
    result.raise_for_status()
    print(f"Administrator {action}: {email}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, requests.RequestException) as exc:
        print(f"Admin bootstrap failed: {exc}", file=sys.stderr)
        raise SystemExit(1)