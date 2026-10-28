#!/usr/bin/env python3
"""PermissionRequest hook: asks for approval in Telegram with Allow/Deny buttons.

Needs env vars TG_BOT_TOKEN and TG_CHAT_ID. Without them, or if nobody answers
in time, it prints nothing and Claude Code shows its usual approval dialog.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid

TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
WAIT_SECONDS = int(os.environ.get("TG_WAIT_SECONDS", "540"))


def api(method, **params):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = urllib.parse.urlencode(
        {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in params.items()}
    ).encode()
    with urllib.request.urlopen(url, data=data, timeout=60) as resp:
        return json.load(resp)["result"]


def describe(event):
    tool = event.get("tool_name", "?")
    inp = event.get("tool_input", {}) or {}
    if tool == "Bash":
        body = inp.get("command", "")
    elif "file_path" in inp:
        body = inp["file_path"]
    else:
        body = json.dumps(inp, ensure_ascii=False, indent=1)
    project = os.path.basename(event.get("cwd", "") or "")
    return f"🔐 Claude просит разрешение\n📁 {project}\n🛠 {tool}\n\n{body[:3000]}"


def decide(behavior, message=None):
    decision = {"behavior": behavior}
    if message:
        decision["message"] = message
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": decision}}))


def main():
    if not TOKEN or not CHAT_ID:
        return
    event = json.load(sys.stdin)
    rid = uuid.uuid4().hex[:12]
    msg = api(
        "sendMessage",
        chat_id=CHAT_ID,
        text=describe(event),
        reply_markup={"inline_keyboard": [[
            {"text": "✅ Разрешить", "callback_data": f"a:{rid}"},
            {"text": "❌ Запретить", "callback_data": f"d:{rid}"},
        ]]},
    )
    offset = None
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        params = {"timeout": 25, "allowed_updates": ["callback_query"]}
        if offset is not None:
            params["offset"] = offset
        for upd in api("getUpdates", **params):
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query") or {}
            action, _, got = (cq.get("data") or "").partition(":")
            if got != rid:
                continue
            allowed = action == "a"
            api("answerCallbackQuery", callback_query_id=cq["id"],
                text="Разрешено" if allowed else "Запрещено")
            api("editMessageReplyMarkup", chat_id=CHAT_ID, message_id=msg["message_id"],
                reply_markup={"inline_keyboard": [[{
                    "text": "✅ Разрешено" if allowed else "❌ Запрещено",
                    "callback_data": "done"}]]})
            if allowed:
                decide("allow")
            else:
                decide("deny", "Пользователь запретил это действие в Telegram.")
            return
    api("editMessageReplyMarkup", chat_id=CHAT_ID, message_id=msg["message_id"],
        reply_markup={"inline_keyboard": [[{"text": "⏰ Время вышло — ответьте в приложении",
                                            "callback_data": "done"}]]})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never block Claude because of the bot
        print(f"tg_approve: {exc}", file=sys.stderr)
