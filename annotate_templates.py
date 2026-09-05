#!/usr/bin/env python3
"""
Annotate the generated SocialRobot workflow templates for n8n.io submission.

Replicates the logic of n8n's official "Auto-generate sticky notes and rename
nodes" workflow (n8n.io/workflows/13868):
  - strip existing sticky notes
  - rename nodes to descriptive Title Case names
  - add a main overview sticky ("How it works" + "Setup steps")
  - add one white section sticky per logical group
  - place stickies so nothing overlaps a node or another sticky

Main sticky conventions (n8n template sticky-note guidelines):
  - YELLOW (no `color` parameter), upper-left of the canvas
  - 100-300 words, structured as `## <workflow name>`, `### How it works`
    (numbered steps), `### Setup steps` (checkboxes `- [ ]`), and an optional
    `### Customization` paragraph. No extra sections; requirements are folded
    into the setup steps and platforms are listed once via join_names().
  - width 440-520 so it is never a long narrow column.

Section stickies: WHITE (color 7), `## <title>` plus at most one short
sentence. Colors are only yellow (main) and white (sections).

Placement: each section sticky sits above its group's node bounding box with
padding. Groups whose sticky would start above y=40 or collide with any node
or another sticky are shifted DOWN as a whole column cluster, so the final
canvas has no overlaps and every sticky starts at y >= 40. Nodes only move
vertically, and only when required by their own group's sticky.

The "AI" grouping/description step is done here with deterministic rules since
the templates are small and formulaic.

Handles the consolidated 3.0.0 SocialRobot node: platforms are `resource`
parameters on the single node type.

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

# Sticky placement geometry. Node boxes are assumed ~200x80 (n8n default size).
NODE_W, NODE_H = 200, 80
STICKY_TOP = 40        # stickies never start above this canvas y
GAP_STICKY_NODE = 60   # gap between a sticky's bottom and its group's top node
GAP_OBSTACLE = 40      # min clearance between a sticky and any other box above it

MAIN_WORDS_MIN = 100
MAIN_WORDS_MAX = 320


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


def as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


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


# Assignment-name -> readable phrase for Set nodes. Phrase is used after the
# word "the", so it must not carry its own article (matches canonical wording).
_ASSIGN_LABELS = {
    "topic": "post topic", "tone": "desired tone", "theme": "post theme",
    "caption": "caption", "text": "text", "imageUrl": "image URL",
    "imagePrompt": "image idea", "content": "source content", "url": "URL",
}


def set_items(node):
    """Readable, comma/and-joined list of a Set node's assignment names."""
    assigns = ((node.get("parameters", {}).get("assignments") or {}).get("assignments") or [])
    names = []
    for a in assigns:
        raw = (a or {}).get("name")
        if not raw:
            continue
        names.append(_ASSIGN_LABELS.get(str(raw).lower(), str(raw)))
    return join_names(names)


def describe_source(node, has_agent=False):
    """One short sentence describing what a source node contributes."""
    t = node.get("type", "")
    params = node.get("parameters", {})
    if "rssFeedRead" in t:
        return "Fetches the latest items from the RSS feed."
    if "googleSheets" in t:
        return "Reads the scheduled posts from your content calendar spreadsheet."
    if t == "n8n-nodes-base.set":
        items = set_items(node)
        if items:
            if has_agent:
                return f"Sets the {items} that guide the AI-written content."
            return f"Sets the {items} used to build the post."
        return "Sets the topic, text, or other inputs used to build the post."
    if "httpRequest" in t:
        url = str(params.get("url", ""))
        if "images/generations" in url:
            return "Generates the image with OpenAI (gpt-image-2)."
        if url.startswith("https://api.replicate.com") and params.get("method") == "POST":
            return "Generates the video with Seedance on Replicate, waits for it to finish, and downloads the file."
        if params.get("responseFormat") == "file" and not url.startswith("="):
            return "Downloads the image from the given URL into binary data."
        return ""
    if "langchain.agent" in t:
        return "Uses OpenAI to write the post copy and parses it into per-platform fields."
    return ""


def describe_action(action):
    """Describe the SocialRobot action node(s) as one or two short sentences.

    Platforms are listed once (join_names form), never repeated per node."""
    actions = as_list(action)
    if not actions:
        return ""
    descs = []
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if is_management(n)]

    modes = {}
    for n in publish_nodes:
        mode = (n.get("parameters") or {}).get("publishMode", "NOW")
        modes.setdefault(mode, []).append(PLATFORM_LABELS[platform_of(n)])

    for mode in ("NOW", "DRAFT", "SCHEDULE"):
        names = modes.get(mode)
        if not names:
            continue
        joined = join_names(names)
        if mode == "DRAFT":
            plural = "a draft post" if len(names) == 1 else "draft posts"
            descs.append(f"Saves {plural} to {joined} in SocialRobot for review.")
        elif mode == "SCHEDULE":
            plural = "a post" if len(names) == 1 else "posts"
            descs.append(f"Schedules {plural} to {joined} for the date and time you set.")
        else:
            plural = "a post" if len(names) == 1 else "posts"
            descs.append(f"Publishes {plural} to {joined} via the SocialRobot API.")

    for n in management_nodes:
        params = n.get("parameters", {})
        resource = params.get("resource")
        op = params.get("operation")
        if resource == "account":
            descs.append("Lists your connected SocialRobot accounts.")
        elif op == "getAll":
            descs.append("Lists posts from SocialRobot with optional filters.")
        elif op == "get":
            descs.append("Fetches a single post by its ID.")
        elif op == "delete":
            descs.append("Deletes the post with the given ID.")
        elif op == "reschedule":
            descs.append("Reschedules the post to a new date.")
        else:
            descs.append("Calls the SocialRobot API.")
    return " ".join(descs)


def _source_action_partition(actions):
    """Returns (publish_nodes, management_nodes) from an actions list."""
    actions = as_list(actions)
    return [n for n in actions if is_publish(n)], [n for n in actions if is_management(n)]


def build_how_items(trigger, sources, actions):
    """'How it works' steps (2-6, short numbered sentences)."""
    publish_nodes, management_nodes = _source_action_partition(actions)
    has_agent = any("langchain.agent" in s.get("type", "") for s in sources)

    items = []
    items.append(describe_trigger(trigger) if trigger else "Runs when you click Execute Workflow.")
    seen = {items[0]}

    def add(d):
        if d and d not in seen:
            seen.add(d)
            items.append(d)

    for s in sources:
        add(describe_source(s, has_agent=has_agent))

    for sentence in describe_action(publish_nodes + management_nodes).split(". "):
        sentence = sentence.strip()
        if sentence:
            add(sentence if sentence.endswith(".") else sentence + ".")

    if len(items) > 6:
        items = items[:6]
    return items


def build_setup_steps(sources, actions):
    """Checkbox setup steps ('- [ ] ...') for the main sticky.

    Requirements are folded in here; platforms are named only when a step
    genuinely targets a single platform."""
    publish_nodes, management_nodes = _source_action_partition(actions)
    steps = []
    seen = set()

    def add(step, key=None):
        key = key or step
        if key not in seen:
            seen.add(key)
            steps.append(step)

    add("[ ] Install the SocialRobot community node and connect your SocialRobot API credential "
        "(API key: socialrobot.io, Scheduler -> API Keys).", "install")

    for s in sources:
        t = s.get("type", "")
        if "rssFeedRead" in t:
            add("[ ] Set the RSS feed URL to your own feed.", "rss")
        elif "googleSheets" in t:
            add("[ ] Connect Google Sheets and select your spreadsheet and sheet.", "sheets")

    # one step per non-SocialRobot credential type, naming every node that uses it
    cred_nodes = {}
    for n in sources + publish_nodes + management_nodes:
        for cred in (n.get("credentials") or {}):
            if cred in ("socialRobotApi", "googleSheetsOAuth2Api"):
                continue
            cred_nodes.setdefault(cred, []).append(n["name"])
    cred_label = {"openAiApi": "OpenAI", "replicateApi": "Replicate"}
    for cred in sorted(cred_nodes):
        names = sorted(set(cred_nodes[cred]))
        label = cred_label.get(cred, cred)
        if len(names) == 1:
            add(f"[ ] Connect your {label} account in the {names[0]} node.", f"cred-{cred}")
        else:
            add(f"[ ] Connect your {label} account in the {join_names(names)} nodes.", f"cred-{cred}")

    for s in sources:
        if s.get("type") == "n8n-nodes-base.set":
            items = set_items(s)
            if items:
                add(f"[ ] In the {s['name']} node, set the {items} to your own content.", "set")
            else:
                add(f"[ ] Edit the fields in the {s['name']} node to set your own values.", "set")

    if publish_nodes:
        labels = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
        if len(publish_nodes) == 1:
            label = labels[0]
            add(f"[ ] Select your {label} account in the Publish to {label} node.", "account")
        else:
            add("[ ] Select your connected SocialRobot account in each Publish node.", "account")

        media_placeholder = False
        binary_instagram = False
        literal_caption = False
        schedule_mode = False
        for n in publish_nodes:
            params = n.get("parameters", {})
            platform = platform_of(n)
            if platform == "pinterest":
                add("[ ] Set your Pinterest board ID in the Publish to Pinterest node.", "pinterest")
            if params.get("publishMode") == "SCHEDULE":
                schedule_mode = True
            if params.get("mediaSource") == "binary":
                binary_instagram = True
            if params.get("caption") and not str(params.get("caption")).startswith("="):
                literal_caption = True
            u = params.get("mediaUrl")
            if isinstance(u, str) and ("placehold" in u or "example.com" in u):
                media_placeholder = True
            for m in as_list(params.get("medias")):
                u = (m or {}).get("mediaUrl", "")
                if isinstance(u, str) and ("placehold" in u or "example.com" in u):
                    media_placeholder = True
        if media_placeholder:
            add("[ ] Replace the sample media URL with your own public image or video URL.", "media")
        if binary_instagram:
            add("[ ] Make sure an upstream node provides the image as binary data for Instagram.", "igbin")
        if literal_caption and not any(s.get("type") == "n8n-nodes-base.set" for s in sources):
            if len(publish_nodes) == 1:
                label = labels[0]
                add(f"[ ] Replace the example caption in the Publish to {label} node with your own text.", "caption")
            else:
                add("[ ] Replace the example captions in the Publish nodes with your own text.", "caption")
        if schedule_mode:
            add("[ ] Confirm the schedule date in each Publish node, or map it from an upstream field.", "sched")

    # literal-URL file-download HTTP node -> point it at your own media
    for s in sources:
        if "httpRequest" in s.get("type", ""):
            params = s.get("parameters", {})
            url = str(params.get("url", ""))
            if params.get("responseFormat") == "file" and not url.startswith("="):
                add(f"[ ] Point the {s['name']} node at your own image URL.", f"dl-{s['name']}")

    if management_nodes:
        op = management_nodes[0].get("parameters", {}).get("operation")
        is_account = management_nodes[0].get("parameters", {}).get("resource") == "account"
        if op == "getAll" and not is_account:
            add("[ ] Optionally set the status, platform, and date filters.", "filters")
        elif op in ("get", "delete"):
            add("[ ] Provide the ID of the post you want to act on.", "postid")
        elif op == "reschedule":
            add("[ ] Provide the post ID and the new schedule date.", "postid")

    return steps


def build_customization(trigger, sources, actions):
    """One short customization sentence for the main sticky."""
    publish_nodes, management_nodes = _source_action_partition(actions)
    has_agent = any("langchain.agent" in s.get("type", "") for s in sources)
    set_nodes = [s for s in sources if s.get("type") == "n8n-nodes-base.set"]
    rss = any("rssFeedRead" in s.get("type", "") for s in sources)
    sheets = any("googleSheets" in s.get("type", "") for s in sources)
    manual = bool(trigger and trigger.get("type", "").endswith("manualTrigger"))

    if management_nodes:
        op = management_nodes[0].get("parameters", {}).get("operation")
        is_account = management_nodes[0].get("parameters", {}).get("resource") == "account"
        if op == "getAll" and is_account:
            return "The list covers every account connected to SocialRobot, ready to feed into other nodes."
        if op == "getAll":
            return "Adjust the filters to list exactly the posts you care about."
        return "Map the post ID from an upstream workflow to operate on the right post."

    if has_agent:
        agent = next((s for s in sources if "langchain.agent" in s.get("type", "")), None)
        name = agent["name"] if agent else "AI node"
        return (f"Edit the prompt in the {name} node, or change the OpenAI model, "
                f"to tune the tone of the copy.")

    if set_nodes:
        items = set_items(set_nodes[0])
        if items:
            return f"Change the {items} in the {set_nodes[0]['name']} node to publish different content."

    if rss:
        return "Point the RSS node at a different feed to reuse the workflow for another blog or channel."

    if sheets:
        return "Add rows to the spreadsheet to queue more posts, or edit columns to change the content."

    if publish_nodes:
        labels = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
        if manual and len(labels) > 1:
            return "Replace the example content, then run the workflow to post everywhere at once."
        if manual:
            return "Replace the example content, then run the workflow whenever you want to post."
    if trigger and trigger.get("type", "").endswith("scheduleTrigger"):
        return "Change the schedule interval to control how often the workflow runs."
    return "Edit any node after import to make the workflow your own."


def extra_customization_sentences(trigger, sources, actions):
    """Deterministic extras used only to lift short stickies toward the
    100-word minimum. Each sentence is accurate for the templates it applies to."""
    publish_nodes, _ = _source_action_partition(actions)
    has_agent = any("langchain.agent" in s.get("type", "") for s in sources)
    set_nodes = [s for s in sources if s.get("type") == "n8n-nodes-base.set"]
    rss = any("rssFeedRead" in s.get("type", "") for s in sources)
    sheets = any("googleSheets" in s.get("type", "") for s in sources)
    manual = bool(trigger and trigger.get("type", "").endswith("manualTrigger"))
    sched = bool(trigger and trigger.get("type", "").endswith("scheduleTrigger"))

    out = []
    if manual:
        out.append("Run it any time to post, or connect a Schedule Trigger to automate it.")
    if has_agent and set_nodes:
        out.append("Try different topics and tones in the Set node to see how the AI adapts the copy per platform.")
    if len(publish_nodes) > 1:
        out.append("Remove the Publish nodes you do not need to target fewer platforms.")
    has_media = any(
        (n.get("parameters") or {}).get("mediaSource") == "binary"
        or (n.get("parameters") or {}).get("mediaUrl")
        or (n.get("parameters") or {}).get("medias")
        for n in publish_nodes
    )
    if has_media:
        out.append("Swap the sample media for your own images or videos.")
    if sched:
        out.append("Adjust the trigger interval to control exactly how often the workflow runs.")
    if rss:
        out.append("The RSS node can point at any feed, so the workflow adapts to a new source in seconds.")
    if sheets:
        out.append("Every row of the spreadsheet becomes a candidate post, so the workflow scales with your plan.")
    # universal closers (only consumed when a sticky still sits under the floor)
    out.append("Everything runs inside your own n8n workspace, so you can change any step after import.")
    out.append("Run it once with a test post to confirm every node behaves as expected before you rely on it.")
    out.append("You can duplicate the workflow to try variations without touching the original.")
    out.append("Enable the workflow only after a successful test run, so nothing publishes by accident.")
    return out


def _who_is_it_for(sources, action):
    actions = as_list(action)
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

    actions = as_list(action)
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


def build_overview(wf, nodes, trigger, sources, action):
    """Content building blocks. The returned tuple is also used by
    generate_descriptions.py (who_for/requirements feed the private submission
    copy, not the sticky itself):
      (name, who_for, how_text, setup_steps, requirements, customization)
    """
    name = wf.get("name", "Untitled workflow")
    actions = as_list(action)
    who_for = _who_is_it_for(sources, actions)
    requirements = _requirements(sources, actions)

    how = build_how_items(trigger, sources, actions)
    how_text = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(how))

    steps = build_setup_steps(sources, actions)
    customization = build_customization(trigger, sources, actions)
    return name, who_for, how_text, steps, requirements, customization


def build_group_stickies(nodes, trigger, sources, actions):
    """Return one dict per logical section:
      {title, desc, anchor, members}
    `members` are the node names that move together when the section sticky
    needs extra room above the group (for the multi-platform publish fan-out
    this is the whole column of Publish nodes, not just the anchor)."""
    groups = []
    if sources:
        if any("langchain.agent" in s.get("type", "") for s in sources):
            anchor = next(s["name"] for s in sources if "langchain.agent" in s.get("type", ""))
            groups.append({"title": "Generate content",
                           "desc": "Uses OpenAI to write and structure the post copy.",
                           "anchor": anchor, "members": [anchor]})
        elif len(sources) == 1 and sources[0].get("type", "").endswith("rssFeedRead"):
            groups.append({"title": "Fetch content",
                           "desc": "Reads new items from the RSS feed to turn them into posts.",
                           "anchor": sources[0]["name"], "members": [sources[0]["name"]]})
        elif len(sources) == 1 and sources[0].get("type") == "n8n-nodes-base.googleSheets":
            groups.append({"title": "Read the calendar",
                           "desc": "Loads scheduled posts from your Google Sheets content calendar.",
                           "anchor": sources[0]["name"], "members": [sources[0]["name"]]})
        elif len(sources) == 1 and sources[0].get("type") == "n8n-nodes-base.set":
            items = set_items(sources[0])
            desc = f"Sets the {items} used to build the post." if items else \
                "Holds the topic, text, or image used to build the post."
            groups.append({"title": "Set input", "desc": desc,
                           "anchor": sources[0]["name"], "members": [sources[0]["name"]]})
        elif len(sources) == 1 and "httpRequest" in sources[0].get("type", ""):
            groups.append({"title": "Fetch media",
                           "desc": "Downloads the image from a URL into binary data for the post.",
                           "anchor": sources[0]["name"], "members": [sources[0]["name"]]})
        else:
            groups.append({"title": "Prepare content",
                           "desc": "Gathers and prepares the content to publish.",
                           "anchor": sources[0]["name"], "members": [sources[0]["name"]]})

    actions = as_list(actions)
    publish_nodes = [n for n in actions if is_publish(n)]
    management_nodes = [n for n in actions if is_management(n)]

    if publish_nodes:
        platforms = [PLATFORM_LABELS[platform_of(n)] for n in publish_nodes]
        if len(publish_nodes) > 4:
            all_names = [n["name"] for n in publish_nodes]
            params = publish_nodes[0].get("parameters", {})
            mode = params.get("publishMode", "NOW")
            if mode == "SCHEDULE":
                groups.append({"title": "Schedule posts",
                               "desc": f"Schedules the content to {join_names(platforms)} at each node's date.",
                               "anchor": publish_nodes[0]["name"], "members": all_names})
            elif mode == "DRAFT":
                groups.append({"title": "Create drafts",
                               "desc": f"Saves draft posts to {join_names(platforms)} in SocialRobot for review.",
                               "anchor": publish_nodes[0]["name"], "members": all_names})
            else:
                groups.append({"title": "Publish",
                               "desc": f"Publishes the content to {join_names(platforms)}.",
                               "anchor": publish_nodes[0]["name"], "members": all_names})
        else:
            for n in publish_nodes:
                label = PLATFORM_LABELS[platform_of(n)]
                mode = n.get("parameters", {}).get("publishMode", "NOW")
                if mode == "SCHEDULE":
                    groups.append({"title": f"Schedule {label}",
                                   "desc": f"Schedules the content to {label} at the given date.",
                                   "anchor": n["name"], "members": [n["name"]]})
                elif mode == "DRAFT":
                    groups.append({"title": f"Draft {label}",
                                   "desc": f"Saves a draft post to {label} in SocialRobot for review.",
                                   "anchor": n["name"], "members": [n["name"]]})
                else:
                    groups.append({"title": f"Publish to {label}",
                                   "desc": f"Publishes the content to {label}.",
                                   "anchor": n["name"], "members": [n["name"]]})

    if management_nodes:
        m = management_nodes[0]
        params = m.get("parameters", {})
        op = params.get("operation")
        resource = params.get("resource")
        if resource == "account":
            groups.append({"title": "List accounts",
                           "desc": "Lists your connected SocialRobot accounts.",
                           "anchor": m["name"], "members": [m["name"]]})
        elif op == "getAll":
            groups.append({"title": "List posts",
                           "desc": "Lists posts from SocialRobot with optional filters.",
                           "anchor": m["name"], "members": [m["name"]]})
        elif op == "get":
            groups.append({"title": "Get post",
                           "desc": "Fetches a single post by its ID.",
                           "anchor": m["name"], "members": [m["name"]]})
        elif op == "delete":
            groups.append({"title": "Delete post",
                           "desc": "Deletes the post with the given ID.",
                           "anchor": m["name"], "members": [m["name"]]})
        elif op == "reschedule":
            groups.append({"title": "Reschedule post",
                           "desc": "Moves the post to a new schedule date.",
                           "anchor": m["name"], "members": [m["name"]]})
        else:
            groups.append({"title": "Manage posts",
                           "desc": "Reads, deletes, or reschedules posts through the SocialRobot API.",
                           "anchor": m["name"], "members": [m["name"]]})
    return groups


# ---------------------------------------------------------------------------
# sticky sizing + placement
# ---------------------------------------------------------------------------

def word_count(content):
    """Prose word count: markdown markup (headings, checkbox dashes, link
    syntax, list numbers) does not count as words."""
    txt = re.sub(r"```.*?```", "", content, flags=re.S)
    txt = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", txt)  # link: keep visible text
    lines = []
    for ln in txt.splitlines():
        ln = ln.strip()
        if ln.startswith("###") or ln.startswith("##"):
            continue
        if ln.startswith("- [ ] "):
            ln = ln[6:]
        elif ln.startswith("- "):
            ln = ln[2:]
        ln = re.sub(r"^\d+\.\s*", "", ln)
        lines.append(ln)
    words = " ".join(lines).split()
    return len([w for w in words if re.search(r"[A-Za-z0-9]", w)])


def estimate_height(content, width):
    """Estimated rendered sticky height (px) at a given width. Deliberately a
    little generous so the stored height never clips the real rendering."""
    cpl = max(20, int((width - 48) / 6.9))
    h = 20.0  # top padding
    for line in content.split("\n"):
        if not line.strip():
            h += 8
        elif line.startswith("## "):
            h += 40 + 6
        elif line.startswith("### "):
            h += 32 + 4
        else:
            wrapped = max(1, -(-len(line) // cpl))
            h += wrapped * 20
            if wrapped > 1:
                h += 2
    return int(h) + 36  # bottom padding + slack


def _inflated(rect, gap):
    x, y, w, h = rect
    return (x - gap, y - gap, w + 2 * gap, h + 2 * gap)


def _overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def place_section_stickies(groups, objs):
    """Place each section sticky above its group's node bounding box.

    Groups are processed per column, top to bottom. Each group's sticky starts
    at y >= 40 and sits directly above the group's top node with padding; a
    group is shifted DOWN (all member nodes move by the same delta) whenever
    its sticky would collide with any node or previously placed sticky, or
    when the sticky would start above y=40. A per-column ladder additionally
    keeps the groups in their original vertical order, so fan-out columns read
    cleanly top to bottom and shifted nodes never land on other nodes.

    Columns are >420px apart while stickies are 360px wide, so columns never
    interact. Mutates node positions in place. Returns a list of sticky dicts."""
    placed = []  # (x, y, w, h) of already placed stickies
    result = []

    def member_clear(members, delta, pending):
        """Member nodes (shifted by delta) must not collide with any fixed node
        (nodes of already-placed groups, other columns, or ungrouped nodes).
        Nodes of groups in this column that are still to be placed move later,
        so they are not obstacles yet."""
        for name in members:
            mx, my = objs[name]["position"]
            for other, node in objs.items():
                if other in members or other in pending:
                    continue
                ox, oy = node.get("position", [620, 360])
                if _overlaps((mx, my + delta, NODE_W, NODE_H), (ox, oy, NODE_W, NODE_H)):
                    return False
        return True

    def sticky_clear(sx, sy, sw, sh, members, delta, pending):
        # keep GAP_OBSTACLE clearance from every fixed node (own members shift too)
        for name, node in objs.items():
            if name in pending:
                continue
            x, y = node.get("position", [620, 360])
            if name in members:
                y += delta
            if _overlaps((sx, sy, sw, sh), _inflated((x, y, NODE_W, NODE_H), GAP_OBSTACLE)):
                return False
        for (px, py, pw, ph) in placed:
            if _overlaps((sx, sy, sw, sh), _inflated((px, py, pw, ph), GAP_OBSTACLE)):
                return False
        return True

    by_column = {}
    for g in groups:
        x = objs[g["anchor"]]["position"][0]
        by_column.setdefault(x, []).append(g)

    for x in sorted(by_column):
        col_groups = sorted(by_column[x],
                            key=lambda g: min(objs[n]["position"][1] for n in g["members"]))
        pending = set()
        for g in col_groups:
            pending.update(g["members"])
        prev_sticky_bottom = None
        prev_node_bottom = None
        for g in col_groups:
            content = f"## {g['title']}"
            if g.get("desc"):
                content += f"\n\n{g['desc']}"
            w = SECTION_WIDTH
            h = estimate_height(content, SECTION_WIDTH)
            members = set(g["members"])
            btop = min(objs[n]["position"][1] for n in g["members"])

            # ladder lower bound: stay below the previous group in this column
            ladder = 0
            if prev_node_bottom is not None:
                ladder = max(ladder, prev_node_bottom + GAP_OBSTACLE - btop)
            if prev_sticky_bottom is not None:
                ladder = max(ladder,
                             prev_sticky_bottom + h + GAP_STICKY_NODE + GAP_OBSTACLE - btop)
            ladder = max(ladder, STICKY_TOP + h + GAP_STICKY_NODE - btop)

            delta = ladder
            while delta < 20000:
                top = btop + delta - h - GAP_STICKY_NODE
                if top < STICKY_TOP:
                    top = STICKY_TOP
                # sticky must sit above the group's top node with GAP_STICKY_NODE
                if top + h > btop + delta - GAP_STICKY_NODE + GAP_OBSTACLE:
                    delta += 20
                    continue
                if not sticky_clear(x, top, w, h, members, delta, pending):
                    delta += 20
                    continue
                if not member_clear(members, delta, pending):
                    delta += 20
                    continue
                break
            else:
                raise RuntimeError(f"could not place sticky for group '{g['title']}'")

            for name in g["members"]:
                nx, ny = objs[name]["position"]
                objs[name]["position"] = [nx, ny + delta]
            pending.difference_update(g["members"])

            sticky = make_sticky(content, w, h, x, top, f"Sticky Note{len(result) + 1}", color=7)
            result.append(sticky)
            placed.append((x, top, w, h))
            prev_sticky_bottom = top + h
            prev_node_bottom = btop + delta + NODE_H
    return result


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

    name, who_for, how_text, steps, requirements, customization = build_overview(
        wf, non_sticky, trigger, sources, actions
    )

    # --- main sticky content ---
    main_content = f"## {name}\n\n### How it works\n\n{how_text}\n\n### Setup steps\n\n"
    for step in steps:
        main_content += f"- {step}\n"

    # always close with a short Customization paragraph; add accurate extras
    # only when needed to reach the 100-word floor.
    extras = extra_customization_sentences(trigger, sources, actions)
    para = [customization] if customization else []
    while word_count(main_content + " " + " ".join(para)) < MAIN_WORDS_MIN and extras:
        para.append(extras.pop(0))
    if para:
        main_content += "\n### Customization\n\n" + " ".join(para)

    main_height = min(900, estimate_height(main_content, MAIN_WIDTH))
    stickies = [make_sticky(main_content, MAIN_WIDTH, main_height, 40, 40, "Sticky Note")]

    # --- section stickies (shift groups down as needed) ---
    objs = {n["name"]: n for n in non_sticky}
    groups = build_group_stickies(non_sticky, trigger, sources, actions)
    stickies += place_section_stickies(groups, objs)

    # stickies first (render behind nodes), then nodes
    wf["nodes"] = stickies + [n for n in nodes if n.get("type") != STICKY_TYPE]
    wf["meta"] = {"instanceId": rid(), "templateCredsSetupCompleted": False}
    return wf
