"""English text constants."""
TEXTS = {
    "task": {
        "added": "Task '{title}' added (ID: {id})",
        "completed": "Task {id} marked as done.",
        "reopened": "Task {id} reopened.",
        "deleted": "Task '{title}' (ID: {id}) deleted.",
        "updated": "Task {id} updated.",
    },
    "error": {
        "storage": "Data file error. Check logs/ for details.",
        "not_found": "Task {id} not found.",
    },
    "status": {
        "pending": "[ ]",
        "done": "[✓]",
    },
    "prompt": {
        "no_tasks": "No tasks yet. Use 'todo add' to create one.",
        "confirm_delete": "Delete '{title}' (ID: {id})?",
    },
    "table": {
        "header_id": "ID",
        "header_title": "Title",
        "header_status": "Status",
    },
    "list": {
        "title": "My Tasks",
    },
    "show": {
        "label_title": "Title",
        "label_description": "Description",
        "label_status": "Status",
        "label_priority": "Priority",
        "label_created": "Created",
        "label_updated": "Updated",
        "label_completed": "Completed",
        "status_done": "Done",
        "status_pending": "Pending",
        "na": "N/A",
        "not_yet": "Not yet",
    },
    "edit": {
        "no_fields_error": "Error: At least one field (-t, -d, -p) must be provided for update.",
    },
}
