"""Supabase token verification and server-only administrator operations."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict

import requests


DEFAULT_SUPABASE_URL = "https://pprhoevhbpjiucubsmlw.supabase.co"
DEFAULT_PUBLISHABLE_KEY = "sb_publishable_gejpN-iGtqsKYwo8Aq8PVQ_zpnOd-ZT"


class AuthService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL).rstrip("/")
        self.publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", DEFAULT_PUBLISHABLE_KEY)
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()

    @property
    def admin_configured(self) -> bool:
        return bool(self.admin_email)

    @property
    def user_metrics_configured(self) -> bool:
        return bool(self.service_role_key)

    def verify_token(self, authorization: str | None) -> Dict[str, Any] | None:
        if not authorization or not authorization.lower().startswith("bearer "):
            return None
        token = authorization.split(" ", 1)[1].strip()
        if not token:
            return None
        try:
            response = requests.get(
                f"{self.url}/auth/v1/user",
                headers={"apikey": self.publishable_key, "Authorization": f"Bearer {token}"},
                timeout=8,
            )
            if response.status_code != 200:
                return None
            return response.json()
        except requests.RequestException:
            return None

    def is_admin(self, user: Dict[str, Any] | None) -> bool:
        if not user:
            return False
        email = str(user.get("email", "")).lower()
        role = str(user.get("app_metadata", {}).get("role", "")).lower()
        # Both checks are mandatory: ADMIN_EMAIL pins administration to one identity,
        # while app_metadata can only be assigned by the trusted server bootstrap.
        email_matches = bool(self.admin_email and email == self.admin_email)
        return email_matches and role == "admin"

    def list_user_metrics(self) -> Dict[str, Any]:
        if not self.service_role_key:
            return {
                "configured": False,
                "total_users": None,
                "message": "Set SUPABASE_SERVICE_ROLE_KEY on the server to load user totals.",
            }

        users = []
        page = 1
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
        }
        while True:
            response = requests.get(
                f"{self.url}/auth/v1/admin/users",
                params={"page": page, "per_page": 1000},
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            batch = payload.get("users", payload if isinstance(payload, list) else [])
            users.extend(batch)
            if len(batch) < 1000:
                break
            page += 1

        now = datetime.now(timezone.utc)

        def recent(value: str | None, days: int = 30) -> bool:
            if not value:
                return False
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return (now - parsed).days <= days
            except (ValueError, TypeError):
                return False

        return {
            "configured": True,
            "total_users": len(users),
            "confirmed_users": sum(bool(u.get("email_confirmed_at") or u.get("confirmed_at")) for u in users),
            "unconfirmed_users": sum(not bool(u.get("email_confirmed_at") or u.get("confirmed_at")) for u in users),
            "recent_users": sum(recent(u.get("created_at")) for u in users),
        }