from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app, follow_redirects=False)


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant():
    email = "new.student@mergington.edu"

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in activities["Art Club"]["participants"]


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant():
    email = "new.student@mergington.edu"
    client.post("/activities/Art Club/signup", params={"email": email})

    response = client.post("/activities/Art Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert activities["Art Club"]["participants"].count(email) == 1


def test_unregister_removes_participant():
    email = "new.student@mergington.edu"
    activities["Art Club"]["participants"].append(email)

    response = client.delete(f"/activities/Art Club/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Art Club"}
    assert email not in activities["Art Club"]["participants"]


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown Club/participants/student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant():
    response = client.delete(
        "/activities/Art Club/participants/missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
