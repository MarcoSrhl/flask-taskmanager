from datetime import date, timedelta
import os

from models import User, Task
from app import _build_postgres_uri


def test_task_is_overdue_true_for_past_due_and_not_completed(monkeypatch):
    yesterday = date.today() - timedelta(days=1)
    task = Task(due_date=yesterday, is_completed=False)

    assert task.is_overdue() is True


def test_task_is_overdue_false_when_completed(monkeypatch):
    yesterday = date.today() - timedelta(days=1)
    task = Task(due_date=yesterday, is_completed=True)

    assert task.is_overdue() is False


def test_task_is_overdue_false_when_no_due_date(monkeypatch):
    task = Task(due_date=None, is_completed=False)

    assert task.is_overdue() is False


def test_user_password_hashing():
    user = User(username="alice")
    user.set_password("secret123")

    # Password is not stored in clear text
    assert user.password_hash != "secret123"
    # Correct password passes
    assert user.check_password("secret123") is True
    # Wrong password fails
    assert user.check_password("wrong") is False


def test_build_postgres_uri_uses_database_url_if_set(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://override")
    uri = _build_postgres_uri()
    assert uri == "postgresql://override"


def test_build_postgres_uri_builds_from_parts(monkeypatch):
    # Ensure DATABASE_URL is not present
    monkeypatch.delenv("DATABASE_URL", raising=False)

    monkeypatch.setenv("POSTGRES_USER", "user1")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pwd1")
    monkeypatch.setenv("POSTGRES_HOST", "db-host")
    monkeypatch.setenv("POSTGRES_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "mydb")

    uri = _build_postgres_uri()
    assert uri == "postgresql+psycopg2://user1:pwd1@db-host:6543/mydb"
