"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Competitive basketball team for varsity and JV players",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu", "alex@mergington.edu"],
        "waitlist": []
    },
    "Tennis Club": {
        "description": "Learn tennis skills and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["sarah@mergington.edu"],
        "waitlist": []
    },
    "Music Band": {
        "description": "Learn to play instruments and perform in school concerts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["lily@mergington.edu", "noah@mergington.edu"],
        "waitlist": []
    },
    "Drama Club": {
        "description": "Participate in theatrical productions and stage performances",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 30,
        "participants": ["grace@mergington.edu"],
        "waitlist": []
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["mia@mergington.edu"],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def activity_is_full(activity: dict) -> bool:
    return len(activity["participants"]) >= activity["max_participants"]


def add_to_waitlist(activity: dict, email: str):
    activity["waitlist"].append(email)


def add_to_activity(activity: dict, email: str):
    activity["participants"].append(email)


def participant_enrolled_message(email: str, activity_name: str) -> dict:
    return {"message": f"Signed up {email} for {activity_name}", "status": "enrolled"}


def participant_waitlisted_message(email: str, activity_name: str) -> dict:
    return {"message": f"{email} has been added to the waitlist for {activity_name}", "status": "waitlisted"}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already a participant
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Validate student is not already on the waitlist
    if email in activity["waitlist"]:
        raise HTTPException(status_code=400, detail="Student already on the waitlist for this activity")

    # Enroll or waitlist based on capacity
    if activity_is_full(activity):
        add_to_waitlist(activity, email)
        return participant_waitlisted_message(email, activity_name)

    add_to_activity(activity, email)
    return participant_enrolled_message(email, activity_name)


@app.delete("/activities/{activity_name}/participants")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if email in activity["participants"]:
        # Remove from participants
        activity["participants"].remove(email)
        # Auto-promote the first waitlisted student if any
        if activity["waitlist"]:
            promoted = activity["waitlist"].pop(0)
            activity["participants"].append(promoted)
            return {
                "message": f"Unregistered {email} from {activity_name}. {promoted} has been enrolled from the waitlist.",
                "status": "removed_from_participants",
                "promoted": promoted
            }
        return {"message": f"Unregistered {email} from {activity_name}", "status": "removed_from_participants"}

    if email in activity["waitlist"]:
        activity["waitlist"].remove(email)
        return {"message": f"Removed {email} from the waitlist for {activity_name}", "status": "removed_from_waitlist"}

    raise HTTPException(status_code=404, detail="Student is not registered for this activity")
