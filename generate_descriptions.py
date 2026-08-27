#!/usr/bin/env python3
"""
Generate ~200 word n8n.io submission descriptions for each template.

Outputs submission-descriptions.md, one ready-to-paste description per template,
covering the sections n8n's guidelines require: Who's it for, How it works,
How to set up, Requirements, How to customize.

Run: python3 generate_descriptions.py
"""
import json
import os
import re

from annotate_templates import (
    build_overview,
    describe_action,
    is_publish,
    NODE_TYPE,
    AI_CONFIG_TYPES,
    PLATFORM_LABELS,
    platform_of,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "workflows")
OUT = os.path.join(HERE, "submission-descriptions.md")


def split_nodes(wf):
    nodes = wf.get("nodes", [])
    non_sticky = [n for n in nodes if n.get("type") != "n8n-nodes-base.stickyNote"]
    trigger = next((n for n in non_sticky if n.get("type", "").endswith(("Trigger", "trigger", "webhook"))), None)
    sources = [n for n in non_sticky if n is not trigger and n.get("type") != NODE_TYPE
               and not any(t in n.get("type", "") for t in AI_CONFIG_TYPES)]
    actions = [n for n in non_sticky if n.get("type") == NODE_TYPE]
    return non_sticky, trigger, sources, actions


def how_items(how_text):
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in how_text.split("\n") if line.strip()]


def benefit(sources, action):
    actions = action if isinstance(action, list) else ([action] if action else [])
    publish_nodes = [n for n in actions if is_publish(n)]
    if not publish_nodes:
        return ""
    if any("rssFeedRead" in s.get("type", "") for s in sources):
        return " It removes the manual work of copying new articles into social posts."
    if any(s.get("type") == "n8n-nodes-base.googleSheets" for s in sources):
        return " It removes the manual work of posting every spreadsheet row by hand."
    if any("langchain.agent" in s.get("type", "") for s in sources):
        return " It removes the manual work of writing captions for every platform by hand."
    if len(publish_nodes) > 1:
        return " It removes the manual work of posting the same update to every platform separately."
    return " It removes the manual work of logging in and posting by hand."


def customization_hint(sources, trigger, action):
    actions = action if isinstance(action, list) else ([action] if action else [])
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if n.get("type") == NODE_TYPE and not is_publish(n)]

    if management_nodes:
        op = management_nodes[0].get("parameters", {}).get("operation")
        if op in ("get", "delete", "reschedule"):
            return "Map the Post ID from an upstream node, or feed the SocialRobot node from a workflow that produces post IDs."
        if op == "getAll":
            return "Adjust the status, platform, and date filters to list exactly the posts you need."
        return "Adjust the fields to match your account setup."

    hints = []
    if any("langchain.agent" in s.get("type", "") for s in sources):
        hints.append("Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node.")
    elif any(s.get("type") == "n8n-nodes-base.set" for s in sources):
        hints.append("Edit the text or image URL in the Set node to change what gets posted.")
    if trigger and trigger.get("type", "").endswith("scheduleTrigger"):
        hints.append("Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence.")
    elif publish_nodes and publish_nodes[0].get("parameters", {}).get("publishMode") == "SCHEDULE":
        hints.append("Change the schedule date, or map it from an upstream field like a spreadsheet column.")
    elif publish_nodes and publish_nodes[0].get("parameters", {}).get("publishMode") in ("NOW", "DRAFT"):
        hints.append("Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first.")
    if publish_nodes:
        labels = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
        hints.append(f"Add or remove Publish nodes ({', '.join(labels)}) and edit each node's caption and media fields to fit your brand voice.")
    return " ".join(hints)


def describe(wf):
    non_sticky, trigger, sources, actions = split_nodes(wf)
    _, who_for, how_text, steps, requirements, customization = build_overview(
        wf, non_sticky, trigger, sources, actions
    )

    parts = []
    action_desc = describe_action(actions)
    who_lower = who_for[0].lower() + who_for[1:]
    benefit_text = benefit(sources, actions)
    if action_desc:
        intro = f"This workflow {action_desc[0].lower() + action_desc[1:]} It's for {who_lower}"
        if benefit_text:
            intro += benefit_text
        parts.append(intro)
    else:
        parts.append(who_for)
    parts.append("")

    parts.append("**How it works**")
    for i, item in enumerate(how_items(how_text), 1):
        parts.append(f"{i}. {item}")
    parts.append("")

    parts.append("**How to set up**")
    for i, s in enumerate(steps, 1):
        parts.append(f"{i}. {s.replace('[ ] ', '').strip()}")
    parts.append("")

    parts.append("**Requirements**")
    for r in requirements:
        parts.append(f"- {r}")
    parts.append("")

    parts.append("**How to customize**")
    parts.append(customization if customization else customization_hint(sources, trigger, actions))

    return "\n".join(parts)


def main():
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".json"))
    out = [
        "# n8n.io submission descriptions\n\n"
        "Paste each description into the n8n.io template submission form. Each is about\n"
        "150 to 200 words and covers Who's it for, How it works, How to set up,\n"
        "Requirements, and How to customize.\n",
    ]
    for fn in files:
        wf = json.load(open(os.path.join(SRC, fn)))
        out.append(f"## {wf['name']}\n")
        out.append(describe(wf))
        out.append("\n---\n")
    with open(OUT, "w") as f:
        f.write("\n".join(out))
    print(f"Wrote {len(files)} descriptions to {OUT}")


if __name__ == "__main__":
    main()
