#!/usr/bin/env python3
"""
Annotate the generated SocialRobot workflow templates for n8n.io submission.

Replicates the logic of n8n's official "Auto-generate sticky notes and rename
nodes" workflow (n8n.io/workflows/13868):
  - strip existing sticky notes
  - rename nodes to descriptive Title Case names
  - add a main overview sticky ("How it works" + "Setup steps")
  - add one section sticky per logical group
  - place stickies on a left rail so nothing overlaps

The sticky note content format and naming conventions match the official
workflow's prompts exactly. The "AI" grouping/description step is done here with
deterministic rules since the templates are small and formulaic.

Handles the 2.0.0 per-platform node split: the nine "Publish to ..." node types
are actions, the generic "SocialRobot" node handles management operations.

Imported by generate_templates.py, which writes the final annotated templates.
"""
import json
import re
import uuid

NODE_TYPE = "@socialrobot-io/n8n-nodes-socialrobot.socialRobot"
STICKY_TYPE = "n8n-nodes-base.stickyNote"
MAIN_WIDTH = 480
SECTION_WIDTH = 360
# AI config sub-nodes (chat model, parser, tools) sit under an AI Agent and are
# not content sources in their own right, so they are excluded from the source list.
AI_CONFIG_TYPES = ("lmChatOpenAi", "outputParserStructured", "toolSerpApi", "memoryBufferWindow")

# 3.0.0: one SocialRobot node; the platform lives on the `resource` parameter.
PUBLISH_RESOURCES = (
    "instagram", "x", "linkedin", "tiktok", "facebook",
    "pinterest", "bluesky", "mastodon", "threads",
)
PLATFORM_LABELS = {
    "instagram": "Instagram", "x": "X (Twitter)", "linkedin": "LinkedIn",
    "tiktok": "TikTok", "facebook": "Facebook", "pinterest": "Pinterest",
    "bluesky": "Bluesky", "mastodon": "Mastodon", "threads": "Threads",
}


def platform_of(node):
    """Return the platform a SocialRobot node publishes to, or None if it is a
    management node or not a SocialRobot node at all."""
    if node.get("type") != NODE_TYPE:
        return None
    resource = (node.get("parameters") or {}).get("resource")
    return resource if resource in PUBLISH_RESOURCES else None


def is_publish(node):
    return platform_of(node) is not None


def is_management(node):
    return node.get("type") == NODE_TYPE and not is_publish(node)

INTERVAL_UNITS = {
    "seconds": "second", "minutes": "minute", "hours": "hour",
    "days": "day", "weeks": "week", "months": "month",
}


def join_names(names):
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def interval_name(field, n):
    unit = INTERVAL_UNITS.get(field, "interval")
    if n == 1:
        return f"Every {unit.capitalize()}"
    return f"Every {n} {unit.capitalize()}s"


def interval_phrase(field, n):
    unit = INTERVAL_UNITS.get(field, "interval")
    return f"every {unit}" if n == 1 else f"every {n} {unit}s"


def rid():
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# node renaming
# ---------------------------------------------------------------------------

def rename_node(node):
    t = node.get("type", "")
    params = node.get("parameters", {})

    if t == "n8n-nodes-base.manualTrigger":
        return "Manual Trigger"
    if t == "n8n-nodes-base.scheduleTrigger":
        interval = (params.get("rule", {}).get("interval") or [{}])[0]
        field = interval.get("field", "days")
        if field == "cronExpression":
            return "Scheduled Trigger"
        n = interval.get(field + "Interval", 1)
        return interval_name(field, n)
    if t == "n8n-nodes-base.rssFeedRead":
        url = params.get("url", "")
        return "Fetch Blog Feed" if "blog" in url.lower() else "Fetch RSS Feed"
    if t == "n8n-nodes-base.googleSheets":
        return "Read Content Calendar"
    platform = platform_of(node)
    if platform:
        return f"Publish to {PLATFORM_LABELS[platform]}"
    if t == NODE_TYPE:
        return rename_socialrobot(params)
    return node.get("name", "Node")


def rename_socialrobot(params):
    resource = params.get("resource")
    op = params.get("operation")
    if resource == "account":
        return "List Accounts"
    if op == "getAll":
        status = (params.get("filters") or {}).get("status")
        return f"List {status.title()} Posts" if status else "List Posts"
    if op == "get":
        return "Get Post"
    if op == "delete":
        return "Delete Post"
    if op == "reschedule":
        return "Reschedule Post"
    return "SocialRobot"


def apply_renames(wf):
    """Rename nodes and rewrite connections + expressions to stay consistent."""
    old_to_new = {}
    for node in wf.get("nodes", []):
        if node.get("type") == STICKY_TYPE:
            continue
        old_to_new[node["name"]] = rename_node(node)

    used = set()
    for node in wf.get("nodes", []):
        if node.get("type") == STICKY_TYPE:
            continue
        base = old_to_new[node["name"]]
        new_name = base
        i = 1
        while new_name in used:
            i += 1
            new_name = f"{base} {i}"
        used.add(new_name)
        old_to_new[node["name"]] = new_name
        node["name"] = new_name

    # rewrite connections keys + targets
    new_conns = {}
    for src, conn_def in (wf.get("connections") or {}).items():
        new_src = old_to_new.get(src, src)
        new_conn_def = json.loads(json.dumps(conn_def))
        for ctype, outputs in new_conn_def.items():
            if not isinstance(outputs, list):
                continue
            for arr in outputs:
                if not isinstance(arr, list):
                    continue
                for c in arr:
                    if isinstance(c, dict) and c.get("node"):
                        c["node"] = old_to_new.get(c["node"], c["node"])
        new_conns[new_src] = new_conn_def
    wf["connections"] = new_conns

    # rewrite $('Old Name') expression references inside parameters
    def fix_string(s):
        if not isinstance(s, str):
            return s
        for old, new in old_to_new.items():
            s = re.sub(r"\$\('" + re.escape(old) + r"'\)", f"$('{new}')", s)
            s = re.sub(r'\$\("' + re.escape(old) + r'"\)', f'$("{new}")', s)
        return s

    def fix(obj):
        if isinstance(obj, str):
            return fix_string(obj)
        if isinstance(obj, list):
            return [fix(x) for x in obj]
        if isinstance(obj, dict):
            return {k: fix(v) for k, v in obj.items()}
        return obj

    for node in wf.get("nodes", []):
        if "parameters" in node:
            node["parameters"] = fix(node["parameters"])

    # rewrite pinData keys
    if wf.get("pinData"):
        new_pin = {}
        for k, v in wf["pinData"].items():
            new_pin[old_to_new.get(k, k)] = v
        wf["pinData"] = new_pin

    return old_to_new


# ---------------------------------------------------------------------------
# content generation
# ---------------------------------------------------------------------------

def describe_trigger(node):
    t = node.get("type", "")
    if t.endswith("manualTrigger"):
        return "Runs when you click Execute Workflow."
    if t.endswith("scheduleTrigger"):
        interval = (node.get("parameters", {}).get("rule", {}).get("interval") or [{}])[0]
        field = interval.get("field", "days")
        if field == "cronExpression":
            return "Runs on the configured cron schedule."
        n = interval.get(field + "Interval", 1)
        return f"Runs automatically {interval_phrase(field, n)}."
    return "Starts the workflow."


def describe_source(node):
    t = node.get("type", "")
    if "rssFeedRead" in t:
        return "Fetches the latest items from the configured RSS feed."
    if "googleSheets" in t:
        return "Reads the rows of your content calendar spreadsheet."
    if t == "n8n-nodes-base.set":
        return "Sets the topic, text, or other inputs used to build the post."
    if "httpRequest" in t:
        return "Calls an external API over HTTP (media generation, status polling, or download)."
    if "langchain.agent" in t:
        return "Generates platform-optimized post text with the OpenAI model."
    if t == "n8n-nodes-base.code":
        return "Converts the generated image into binary data for upload."
    if t == "n8n-nodes-base.wait":
        return "Pauses between status checks while the AI media renders."
    if t == "n8n-nodes-base.if":
        return "Checks whether the AI media finished generating; retries until ready."
    return ""


def publish_node_platforms(node):
    """Platform keys for one publish node."""
    platform = platform_of(node)
    return [platform] if platform else []


def describe_action(action):
    """Describe one action node, or a list of action nodes, as a sentence."""
    if isinstance(action, dict):
        action = [action]
    descs = []
    for node in action or []:
        t = node.get("type", "")
        params = node.get("parameters", {})
        if is_publish(node):
            label = PLATFORM_LABELS[platform_of(node)]
            mode = params.get("publishMode", "NOW")
            if mode == "SCHEDULE":
                descs.append(f"Schedules a post to {label} at the given date and time.")
            elif mode == "DRAFT":
                descs.append(f"Saves a draft post to {label} in SocialRobot for review.")
            else:
                descs.append(f"Publishes a post to {label} via the SocialRobot API.")
        elif t == NODE_TYPE:
            resource = params.get("resource")
            op = params.get("operation")
            if resource == "account":
                descs.append("Lists your connected SocialRobot accounts.")
            elif op == "getAll":
                descs.append("Lists posts from SocialRobot.")
            elif op == "get":
                descs.append("Fetches a single post by ID.")
            elif op == "delete":
                descs.append("Deletes a post by ID.")
            elif op == "reschedule":
                descs.append("Reschedules a post to a new date.")
            else:
                descs.append("Calls the SocialRobot API.")
    return " ".join(descs)


def build_overview(wf, nodes, trigger, sources, action):
    name = wf.get("name", "Untitled workflow")

    how = ["1. " + describe_trigger(trigger) if trigger else "1. Starts the workflow."]
    seen_how = set()
    for s in sources:
        d = describe_source(s)
        if d and d not in seen_how:
            seen_how.add(d)
            how.append(f"{len(how) + 1}. " + d)
    desc = describe_action(action)
    if desc:
        how.append(f"{len(how) + 1}. " + desc)
    how_text = "\n".join(how)

    steps = [
        "[ ] Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.",
    ]
    seen_step_types = set()
    for s in sources:
        t = s.get("type", "")
        if t in seen_step_types:
            continue
        seen_step_types.add(t)
        if "rssFeedRead" in t:
            steps.append("[ ] Set the RSS feed URL to your own feed.")
        elif "googleSheets" in t:
            steps.append("[ ] Connect Google Sheets and pick your spreadsheet and sheet.")
        elif t == "n8n-nodes-base.set":
            steps.append("[ ] Edit the fields in the Set node to set your topic or text.")
        elif "httpRequest" in t:
            steps.append("[ ] Connect your Replicate account in the HTTP Request nodes (media generation, status checks, and download).")
        elif "langchain.agent" in t:
            steps.append("[ ] Connect your OpenAI account in the OpenAI Chat Model node.")

    actions = action if isinstance(action, list) else ([action] if action else [])
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if is_management(n)]

    if publish_nodes:
        steps.append("[ ] Select your connected account in each Publish node.")
    seen_publish_steps = set()
    for n in publish_nodes:
        platform = platform_of(n)
        params = n.get("parameters", {})
        if platform == "pinterest" and "pin" not in seen_publish_steps:
            seen_publish_steps.add("pin")
            steps.append("[ ] Set the Pinterest board ID in the Pinterest Publish node.")
        if platform == "instagram" and params.get("mediaSource") == "binary" and "igbin" not in seen_publish_steps:
            seen_publish_steps.add("igbin")
            steps.append("[ ] Make sure an upstream node provides the image as binary data (for example an HTTP Request node).")
        if params.get("publishMode") == "SCHEDULE" and "sched" not in seen_publish_steps:
            seen_publish_steps.add("sched")
            steps.append("[ ] Confirm the schedule date, or map it from an upstream field.")

    has_media_placeholder = json.dumps([n.get("parameters", {}) for n in publish_nodes]).count("example.com") > 0
    if has_media_placeholder:
        steps.append("[ ] Replace the placeholder media URLs with your real public media URLs.")

    if management_nodes:
        op = management_nodes[0].get("parameters", {}).get("operation")
        if op in ("get", "delete", "reschedule"):
            steps.append("[ ] Provide the Post ID, mapped from an upstream node or typed directly.")
        elif op == "getAll":
            steps.append("[ ] Optionally set the status, platform, and date filters.")

    who_for = _who_is_it_for(sources, actions)
    requirements = _requirements(sources, actions)
    customization = ""
    return name, who_for, how_text, steps, requirements, customization


def _who_is_it_for(sources, action):
    actions = action if isinstance(action, list) else ([action] if action else [])
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if is_management(n)]
    if management_nodes:
        return "Teams that manage SocialRobot posts programmatically."
    if any("rssFeedRead" in s.get("type", "") for s in sources):
        return "Publishers and bloggers who want new content shared to social media automatically."
    if any(s.get("type") == "n8n-nodes-base.googleSheets" for s in sources):
        return "Social media teams that plan content in a spreadsheet and want it published on schedule."
    if any("langchain.agent" in s.get("type", "") for s in sources):
        return "Creators and marketers who want AI written posts published automatically."
    platforms = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
    if len(platforms) > 1:
        return "Marketers and creators who post to multiple social platforms and want to write once, publish everywhere."
    if platforms:
        return f"Anyone who wants a simple, repeatable way to post to {platforms[0]}."
    return "Anyone who wants to automate social media publishing."


def _requirements(sources, action):
    reqs = ["A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key."]
    seen_req_types = set()
    for s in sources:
        t = s.get("type", "")
        if t in seen_req_types:
            continue
        seen_req_types.add(t)
        if "rssFeedRead" in t:
            reqs.append("A public RSS feed URL.")
        elif t == "n8n-nodes-base.googleSheets":
            reqs.append("A Google account and a Google Sheet with date and caption columns.")
        elif "langchain.agent" in t:
            reqs.append("An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.")

    actions = action if isinstance(action, list) else ([action] if action else [])
    seen_platform_reqs = set()
    for n in actions:
        platform = platform_of(n)
        if platform is None:
            continue
        params = n.get("parameters", {})
        if platform == "pinterest" and "pin" not in seen_platform_reqs:
            seen_platform_reqs.add("pin")
            reqs.append("A Pinterest board ID.")
        if platform == "instagram" and params.get("mediaSource") == "binary" and "igbin" not in seen_platform_reqs:
            seen_platform_reqs.add("igbin")
            reqs.append("An upstream node that provides the image as binary data (for example an HTTP Request node).")
        elif ("medias" in params or "mediaUrl" in params) and platform not in seen_platform_reqs and platform != "pinterest" and not (platform == "instagram" and params.get("mediaSource") == "binary"):
            seen_platform_reqs.add(platform)
            reqs.append(f"A public image or video URL for {PLATFORM_LABELS[platform]}.")
    return reqs


def build_group_stickies(nodes, trigger, sources, actions):
    """Return (title, description, anchor_node_name) for each logical section.
    The anchor is the node the section sticky should sit above."""
    groups = []
    if sources:
        if any("langchain.agent" in s.get("type", "") for s in sources):
            anchor = next(s["name"] for s in sources if "langchain.agent" in s.get("type", ""))
            groups.append(("Generate content", "Writes platform-optimized post text with the OpenAI model.", anchor))
        elif len(sources) == 1 and sources[0].get("type", "").endswith("rssFeedRead"):
            groups.append(("Fetch content", "Reads new items from the RSS feed to turn them into posts.", sources[0]["name"]))
        elif len(sources) == 1 and sources[0].get("type") == "n8n-nodes-base.googleSheets":
            groups.append(("Read the calendar", "Loads scheduled posts from your Google Sheets content calendar.", sources[0]["name"]))
        elif len(sources) == 1 and sources[0].get("type") == "n8n-nodes-base.set":
            groups.append(("Set input", "Holds the topic, text, or image used to build the post.", sources[0]["name"]))
        elif len(sources) == 1 and "httpRequest" in sources[0].get("type", ""):
            groups.append(("Fetch media", "Downloads the image from a URL into binary data for the post.", sources[0]["name"]))
        else:
            groups.append(("Prepare content", "Gathers and prepares the content to publish.", sources[0]["name"]))

    actions = actions if isinstance(actions, list) else ([actions] if actions else [])
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if is_management(n)]

    if publish_nodes:
        platforms = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
        if len(publish_nodes) > 4:
            params = publish_nodes[0].get("parameters", {})
            mode = params.get("publishMode", "NOW")
            if mode == "SCHEDULE":
                groups.append(("Schedule posts", f"Schedules the content to {join_names(platforms)} at each node's date.", publish_nodes[0]["name"]))
            elif mode == "DRAFT":
                groups.append(("Create drafts", f"Saves draft posts to {join_names(platforms)} in SocialRobot for review.", publish_nodes[0]["name"]))
            else:
                groups.append(("Publish", f"Publishes the content to {join_names(platforms)}.", publish_nodes[0]["name"]))
        else:
            for n in publish_nodes:
                label = PLATFORM_LABELS[platform_of(n)]
                mode = n.get("parameters", {}).get("publishMode", "NOW")
                if mode == "SCHEDULE":
                    groups.append((f"Schedule {label}", f"Schedules the content to {label} at the given date.", n["name"]))
                elif mode == "DRAFT":
                    groups.append((f"Draft {label}", f"Saves a draft post to {label} in SocialRobot for review.", n["name"]))
                else:
                    groups.append((f"Publish to {label}", f"Publishes the content to {label}.", n["name"]))

    if management_nodes:
        op = management_nodes[0].get("parameters", {}).get("operation")
        if op == "getAll" and management_nodes[0].get("parameters", {}).get("resource") != "account":
            groups.append(("List posts", "Lists posts from SocialRobot with optional filters.", management_nodes[0]["name"]))
        else:
            groups.append(("Manage posts", "Reads, deletes, or reschedules posts through the SocialRobot API.", management_nodes[0]["name"]))
    return groups


def estimate_height(content, width):
    chars_per_line = max(20, width // 8)
    h = 60
    for line in content.split("\n"):
        if line.startswith("## "):
            h += 40
        elif line.startswith("### "):
            h += 32
        elif line.strip() == "":
            h += 16
        else:
            h += max(1, (len(line) // chars_per_line) + 1) * 22
    return h + 60


def make_sticky(content, width, height, x, y, name, color=None):
    s = {
        "parameters": {"content": content, "width": width, "height": height},
        "id": rid(),
        "name": name,
        "type": STICKY_TYPE,
        "typeVersion": 1,
        "position": [x, y],
    }
    if color is not None:
        s["parameters"]["color"] = color
    return s


def annotate(wf):
    # deep copy
    wf = json.loads(json.dumps(wf))

    nodes = wf.get("nodes", [])
    non_sticky = [n for n in nodes if n.get("type") != STICKY_TYPE]
    trigger = next((n for n in non_sticky if n.get("type", "").endswith(("Trigger", "trigger", "webhook"))), None)
    sources = [n for n in non_sticky if n is not trigger and n.get("type") != NODE_TYPE
               and not any(t in n.get("type", "") for t in AI_CONFIG_TYPES)]
    actions = [n for n in non_sticky if n.get("type") == NODE_TYPE]

    # rename nodes (and rewrite connections/expressions)
    apply_renames(wf)
    # re-read after rename
    nodes = wf.get("nodes", [])
    non_sticky = [n for n in nodes if n.get("type") != STICKY_TYPE]
    trigger = next((n for n in non_sticky if n.get("type", "").endswith(("Trigger", "trigger", "webhook"))), None)
    sources = [n for n in non_sticky if n is not trigger and n.get("type") != NODE_TYPE
               and not any(t in n.get("type", "") for t in AI_CONFIG_TYPES)]
    actions = [n for n in non_sticky if n.get("type") == NODE_TYPE]

    name, who_for, how_text, steps, requirements, customization = build_overview(wf, non_sticky, trigger, sources, actions)

    main_content = f"## {name}\n\n### Who's it for\n\n{who_for}\n\n### How it works\n\n{how_text}\n\n### How to set up\n\n"
    for step in steps:
        main_content += f"- {step}\n"
    main_content += "\n### Requirements\n\n"
    for req in requirements:
        main_content += f"- {req}\n"
    if customization:
        main_content += f"\n### How to customize\n\n{customization}"

    main_height = max(420, estimate_height(main_content, MAIN_WIDTH))

    stickies = [make_sticky(main_content, MAIN_WIDTH, main_height, 40, 40, "Sticky Note")]

    # Place each section sticky directly above the node group it describes so it
    # reads as a section header rather than drifting to the bottom of the canvas.
    name_to_pos = {n["name"]: n.get("position", [620, 360]) for n in non_sticky}
    for i, (title, desc, anchor) in enumerate(build_group_stickies(non_sticky, trigger, sources, actions), 1):
        content = f"## {title}"
        if desc:
            content += f"\n\n{desc}"
        h = estimate_height(content, SECTION_WIDTH)
        ax, ay = name_to_pos.get(anchor, (620, 360))
        sx, sy = ax, max(40, ay - h - 60)
        stickies.append(make_sticky(content, SECTION_WIDTH, h, sx, sy, f"Sticky Note{i}", color=7))

    # stickies first (render behind nodes), then nodes
    wf["nodes"] = stickies + [n for n in nodes if n.get("type") != STICKY_TYPE]
    wf["meta"] = {"instanceId": rid(), "templateCredsSetupCompleted": False}
    return wf
