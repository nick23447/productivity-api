from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from taskflow import db, bcrypt
from taskflow.models import User, Task
import datetime

tasks = Blueprint("tasks", __name__, url_prefix="/api")


@tasks.route("/create/task", methods=["POST"])
@jwt_required()
def add_task():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    due_date_raw = data.get("due_date")          # "2026-01-10" (required)
    due_time_raw = data.get("due_time")          # "10:30" (optional, 24h)
    duration_minutes_raw = data.get("duration_minutes")
    priority = (data.get("priority") or "").strip()

    reminder_offset_raw = data.get("reminder_minutes")  # optional int
    tags = (data.get("tags") or "").strip() or None
    notes = (data.get("notes") or "").strip() or None

    # ----- required validation -----
    if not title:
        return jsonify({"error": "title is required"}), 400
    if not due_date_raw:
        return jsonify({"error": "due_date is required (YYYY-MM-DD)"}), 400
    if duration_minutes_raw is None:
        return jsonify({"error": "duration_minutes is required"}), 400
    if not priority:
        return jsonify({"error": "priority is required"}), 400

    # Parse due_date
    try:
        due_date = datetime.date.fromisoformat(str(due_date_raw))
    except Exception:
        return jsonify({"error": "due_date must be YYYY-MM-DD"}), 400

    # Parse duration
    try:
        duration_minutes = int(duration_minutes_raw)
        if duration_minutes < 5:
            return jsonify({"error": "duration_minutes must be >= 5"}), 400
    except Exception:
        return jsonify({"error": "duration_minutes must be an integer"}), 400

    # Optional time -> due_at
    due_at = None
    if due_time_raw:
        try:
            t = datetime.datetime.strptime(str(due_time_raw), "%H:%M").time()
            due_at = datetime.datetime.combine(due_date, t)

        except Exception:
            return jsonify({"error": "due_time must be HH:MM (24-hour)"}), 400

    # Optional reminder
    reminder_offset_minutes = None
    if reminder_offset_raw is not None:
        # Reminder requires a specific time
        if due_at is None:
            return jsonify({"error": "reminder_offset_minutes requires due_time"}), 400
        try:
            reminder_offset_minutes = int(reminder_offset_raw)
            if reminder_offset_minutes <= 0:
                return jsonify({"error": "reminder_offset_minutes must be > 0"}), 400
        except Exception:
            return jsonify({"error": "reminder_offset_minutes must be an integer"}), 400

    new_task = Task(
        user_id=user_id,
        title=title,
        due_date=due_date,
        due_at=due_at,
        duration_minutes=duration_minutes,
        priority=priority,
        reminder_minutes=reminder_offset_minutes,
        tags=tags,
        notes=notes,
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "due_date": new_task.due_date.isoformat(),
            "due_at": new_task.due_at.isoformat() if new_task.due_at else None,
            "duration_minutes": new_task.duration_minutes,
            "priority": new_task.priority,
            "reminder_minutes": new_task.reminder_minutes,
            "tags": new_task.tags,
            "notes": new_task.notes,
        }
    }), 201


@tasks.route("/tasks", methods=["GET"])
@jwt_required()
def get_user_tasks():
    user_id = get_jwt_identity()

    user_tasks = (
        Task.query
        .filter(Task.user_id == user_id)
        .order_by(Task.due_date.asc(), Task.due_at.asc().nulls_last())
        .all()
    )

    return jsonify({
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat(),
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "reminder_minutes": t.reminder_minutes,
                "tags": t.tags,
                "notes": t.notes,
            }
            for t in user_tasks
        ]
    }), 200
