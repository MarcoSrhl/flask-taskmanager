import pytest

from app import create_app
from extensions import db
from models import User, Task


@pytest.fixture
def app(tmp_path, monkeypatch):
    # Use a temporary SQLite database for tests
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    app = create_app()
    app.config.update(
        TESTING=True,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def register(client, username="testuser", password="password123"):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "confirm": password,
        },
        follow_redirects=True,
    )


def login(client, username="testuser", password="password123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
        },
        follow_redirects=True,
    )


def test_register_and_login_flow(client, app):
    # Register
    rv = register(client)
    assert b"Registration successful" in rv.data

    # Login
    rv = login(client)
    assert b"Logged in successfully" in rv.data

    # Should reach index page
    assert rv.status_code == 200
    assert b"Tasks" in rv.data or b"Task" in rv.data


def test_create_task_via_post(client, app):
    register(client)
    login(client)

    rv = client.post(
        "/tasks/new",
        data={
            "title": "Integration Test Task",
            "description": "Created via POST",
            "due_date": "2099-01-01",
        },
        follow_redirects=True,
    )

    assert b"Task created." in rv.data

    with app.app_context():
        task = Task.query.filter_by(title="Integration Test Task").first()
        assert task is not None
        assert task.description == "Created via POST"


def test_toggle_task_completion(client, app):
    register(client)
    login(client)

    # Create a task first
    client.post(
        "/tasks/new",
        data={"title": "Toggle Me", "description": "", "due_date": ""},
        follow_redirects=True,
    )

    with app.app_context():
        task = Task.query.filter_by(title="Toggle Me").first()
        assert task is not None
        assert task.is_completed is False
        task_id = task.id

    # Toggle via endpoint
    rv = client.post(f"/tasks/{task_id}/toggle", follow_redirects=True)
    assert b"Task status updated." in rv.data

    with app.app_context():
        task = Task.query.get(task_id)
        assert task.is_completed is True
