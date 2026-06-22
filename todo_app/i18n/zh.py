"""Chinese text constants."""
TEXTS = {
    "task": {
        "added": "任务 '{title}' 已添加 (ID: {id})",
        "completed": "任务 {id} 已标记为完成。",
        "reopened": "任务 {id} 已重新打开。",
        "deleted": "任务 '{title}' (ID: {id}) 已删除。",
        "updated": "任务 {id} 已更新。",
    },
    "error": {
        "storage": "数据文件错误，请查看 logs/ 目录了解详情。",
        "not_found": "任务 {id} 未找到。",
    },
    "status": {
        "pending": "[ ]",
        "done": "[✓]",
    },
    "prompt": {
        "no_tasks": "暂无任务，使用 'todo add' 创建一个。",
        "confirm_delete": "删除 '{title}' (ID: {id})？",
    },
    "table": {
        "header_id": "编号",
        "header_title": "标题",
        "header_status": "状态",
    },
    "list": {
        "title": "我的任务",
    },
    "show": {
        "label_title": "标题",
        "label_description": "描述",
        "label_status": "状态",
        "label_priority": "优先级",
        "label_created": "创建时间",
        "label_completed": "完成时间",
        "status_done": "已完成",
        "status_pending": "待完成",
        "na": "无",
        "not_yet": "尚未",
    },
    "edit": {
        "no_fields_error": "错误：至少需要提供一个更新字段 (-t, -d, -p)。",
    },
}
