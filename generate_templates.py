#!/usr/bin/env python3
"""
Generate submission-ready n8n workflow templates for the SocialRobot community node.

Each template wires built-in n8n trigger/source nodes into the per-platform
SocialRobot "Publish to ..." nodes (types "@socialrobot-io/n8n-nodes-socialrobot.socialRobot<Platform>",
credential "socialRobotApi"). Multi-platform templates fan the source out to one
publish node per platform. Management templates use the generic "SocialRobot" node.
Templates are annotated (sticky notes + descriptive node names) via annotate_templates.py.

AI templates use the real n8n LangChain nodes (verified against n8n's top-ranked
templates on n8n.io):
  - OpenAI chat model : "@n8n/n8n-nodes-langchain.lmChatOpenAi"   (gpt-4o-mini)
  - AI Agent          : "@n8n/n8n-nodes-langchain.agent"
  - Structured parser : "@n8n/n8n-nodes-langchain.outputParserStructured"
Wired exactly like n8n.io/workflows/3066 (433k views): model -> agent via
`ai_languageModel`, parser -> agent via `ai_outputParser`, input -> agent via `main`.

Run:  python3 generate_templates.py
"""
import json
import os
import uuid

from annotate_templates import annotate

NODE_TYPE = "@socialrobot-io/n8n-nodes-socialrobot.socialRobot"
CRED_TYPE = "socialRobotApi"

# 3.0.0: one SocialRobot node; each platform is a Resource. The platform is set
# on the `resource` parameter, so every publish node shares the same type.
PUBLISH_RESOURCES = (
    "instagram", "x", "linkedin", "tiktok", "facebook",
    "pinterest", "bluesky", "mastodon", "threads",
)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflows")

# Real, working sample media URLs. Importers replace these with their own assets.
SAMPLE_IMAGE = "https://placehold.co/1200x630/6e3edf/ffffff.png?text=Replace+with+your+image"
SAMPLE_VIDEO = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def rid():
    return str(uuid.uuid4())


def rloc(mode="list", value=""):
    return {"__rl": True, "mode": mode, "value": value}


def media_item(media_type, media_url, alt="", media_source="url"):
    """One entry of the `medias` collection on X/Threads/Facebook/TikTok/LinkedIn/Pinterest/Mastodon."""
    m = {"mediaSource": media_source, "mediaType": media_type}
    if media_source == "binary":
        m["binaryPropertyName"] = "data"
    else:
        m["mediaUrl"] = media_url
    if alt:
        m["altText"] = alt
    return m


# ----------------------------------------------------------------------------
# node builders
# ----------------------------------------------------------------------------

def _sr_node(parameters, name, node_type=NODE_TYPE):
    return {
        "parameters": parameters,
        "id": rid(),
        "name": name,
        "type": node_type,
        "typeVersion": 1,
        "position": [0, 0],
        "credentials": {CRED_TYPE: {"id": "", "name": "SocialRobot API"}},
    }


def publish_node(platform, name, caption="", medias=None, board_id="", publish_mode="NOW",
                 schedule_date="", media_source="url", media_type="IMAGE", media_url="",
                 binary_property="data", alt_text=""):
    """One SocialRobot node set to a platform Resource (Create operation).
    Field set matches publishFields.ts. The platform lives in the `resource`
    parameter so a single node type covers all nine platforms."""
    params = {"resource": platform, "operation": "create",
              "accountId": rloc(), "publishMode": publish_mode}
    if publish_mode == "SCHEDULE":
        params["scheduleDate"] = schedule_date
    params["caption"] = caption
    if platform == "pinterest":
        params["boardId"] = board_id or "your-board-id"
    if platform == "instagram":
        # Instagram uses flat single-media fields (no medias collection).
        # Only emit them when media is actually provided.
        if media_source == "binary":
            params["mediaSource"] = "binary"
            params["mediaType"] = media_type
            params["binaryPropertyName"] = binary_property
        elif media_url:
            params["mediaSource"] = "url"
            params["mediaType"] = media_type
            params["mediaUrl"] = media_url
    elif medias:
        params["medias"] = medias
    return _sr_node(params, name)


def sr_get_all(name="SocialRobot", return_all=True, filters=None):
    params = {"resource": "post", "operation": "getAll", "returnAll": return_all}
    if not return_all:
        params["limit"] = 50
    if filters:
        params["filters"] = filters
    return _sr_node(params, name)


def sr_get(name="SocialRobot"):
    return _sr_node({"resource": "post", "operation": "get", "postId": "={{ $json.postId }}"}, name)


def sr_delete(name="SocialRobot"):
    return _sr_node({"resource": "post", "operation": "delete", "postId": "={{ $json.id }}"}, name)


def sr_reschedule(name="SocialRobot"):
    return _sr_node(
        {"resource": "post", "operation": "reschedule", "postId": "={{ $json.id }}",
         "scheduleDate": "={{ $json.newDate }}"},
        name,
    )


def sr_accounts(name="SocialRobot"):
    return _sr_node({"resource": "account", "operation": "getAll"}, name)


def manual_node(name="When clicking 'Execute workflow'"):
    return {"parameters": {}, "id": rid(), "name": name, "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1, "position": [0, 0]}


_INTERVAL_KEY = {
    "seconds": "secondsInterval", "minutes": "minutesInterval", "hours": "hoursInterval",
    "days": "daysInterval", "weeks": "weeksInterval", "months": "monthsInterval",
}


def schedule_node(name="Schedule Trigger", field="days", interval=1, cron=None):
    if cron:
        rule = {"interval": [{"field": "cronExpression", "expression": cron}]}
    else:
        rule = {"interval": [{"field": field, _INTERVAL_KEY[field]: interval}]}
    return {"parameters": {"rule": rule}, "id": rid(), "name": name, "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2, "position": [0, 0]}


def rss_node(url, name="RSS Read"):
    return {"parameters": {"url": url}, "id": rid(), "name": name, "type": "n8n-nodes-base.rssFeedRead",
            "typeVersion": 1, "position": [0, 0]}


def http_request_download_node(url, name="Download Image"):
    """GET a URL and save the response as binary data under the 'data' property."""
    return {
        "parameters": {"method": "GET", "url": url, "responseFormat": "file", "options": {}},
        "id": rid(), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [0, 0],
    }


def google_sheets_read(name="Google Sheets"):
    return {
        "parameters": {
            "resource": "sheet",
            "operation": "read",
            "documentId": {"__rl": True, "mode": "list", "value": ""},
            "sheetName": {"__rl": True, "mode": "list", "value": ""},
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7,
        "position": [0, 0],
        "credentials": {"googleSheetsOAuth2Api": {"id": "", "name": "Google Sheets account"}},
    }


def sheets_update_node(name="Update status", key="date"):
    """Google Sheets 'update': writes item json fields back to the row whose
    `key` column matches, e.g. set ready=done after scheduling."""
    return {
        "parameters": {
            "resource": "sheet",
            "operation": "update",
            "documentId": {"__rl": True, "mode": "list", "value": ""},
            "sheetName": {"__rl": True, "mode": "list", "value": ""},
            "key": key,
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.7,
        "position": [0, 0],
        "credentials": {"googleSheetsOAuth2Api": {"id": "", "name": "Google Sheets account"}},
    }


def code_node(name, js, mode="runOnceForAllItems"):
    return {
        "parameters": {"mode": mode, "language": "javaScript", "jsCode": js},
        "id": rid(), "name": name, "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [0, 0],
    }


def set_node(name, assignments):
    """assignments: list of {name, value, type?}. Editable fields the user sets."""
    assign_list = [
        {"id": rid(), "name": a["name"], "type": a.get("type", "string"), "value": a["value"]}
        for a in assignments
    ]
    return {
        "parameters": {"options": {}, "assignments": {"assignments": assign_list}},
        "id": rid(), "name": name, "type": "n8n-nodes-base.set", "typeVersion": 3.4,
        "position": [0, 0],
    }


def openai_model_node(name, model="gpt-4o-mini"):
    return {
        "parameters": {
            "model": {"__rl": True, "mode": "list", "value": model, "cachedResultName": model},
            "options": {"responseFormat": "text"},
        },
        "id": rid(), "name": name, "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi", "typeVersion": 1.2,
        "position": [0, 0],
        "credentials": {"openAiApi": {"id": "", "name": "OpenAI account"}},
    }


def parser_node(name, schema_dict):
    return {
        "parameters": {"schemaType": "manual", "inputSchema": json.dumps(schema_dict, indent=2)},
        "id": rid(), "name": name, "type": "@n8n/n8n-nodes-langchain.outputParserStructured", "typeVersion": 1.2,
        "position": [0, 0],
    }


def agent_node(name, prompt_text, system_message="You always follow the output schema exactly.",
               has_output_parser=True):
    params = {
        "text": "=" + prompt_text,
        "options": {"systemMessage": "=" + system_message},
        "promptType": "define",
    }
    if has_output_parser:
        params["hasOutputParser"] = True
    return {
        "parameters": params,
        "id": rid(), "name": name, "type": "@n8n/n8n-nodes-langchain.agent", "typeVersion": 1.7,
        "position": [0, 0],
        "retryOnFail": True,
    }


# ----------------------------------------------------------------------------
# workflow / connection / layout helpers
# ----------------------------------------------------------------------------

def workflow(name, nodes, connections, active=False):
    return {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
        "active": active,
        "versionId": rid(),
        "meta": {"instanceId": rid(), "templateCredsSetupCompleted": False},
        "pinData": {},
    }


def link(source, target):
    return {source: {"main": [[{"node": target, "type": "main", "index": 0}]]}}


def chain(names):
    """names: ordered node names; returns a merged connection dict."""
    conns = {}
    for i in range(len(names) - 1):
        conns.update(link(names[i], names[i + 1]))
    return conns


def fan_out(source, targets):
    """One source output fanning out to multiple targets (each gets the same item)."""
    return {source: {"main": [[{"node": t, "type": "main", "index": 0} for t in targets]]}}


def ai_block_connections(trigger, input_node, agent, model, parser, action_targets):
    """Wire trigger -> input -> agent -> (fan-out to action_targets), with the OpenAI
    model and structured parser attached to the agent via ai_* edges."""
    conns = {}
    if input_node:
        conns.update(link(trigger, input_node))
        conns.update(link(input_node, agent))
    else:
        conns.update(link(trigger, agent))
    conns[model] = {"ai_languageModel": [[{"node": agent, "type": "ai_languageModel", "index": 0}]]}
    conns[parser] = {"ai_outputParser": [[{"node": agent, "type": "ai_outputParser", "index": 0}]]}
    if action_targets:
        conns.update(fan_out(agent, action_targets))
    return conns


def tidy(wf):
    """Auto-arrange nodes: trigger leftmost, main flow left-to-right, AI sub-nodes
    (model/parser/tools) tucked under their agent. Mirrors n8n's Tidy Up."""
    nodes = [n for n in wf.get("nodes", []) if n.get("type") != "n8n-nodes-base.stickyNote"]
    by_name = {n["name"]: n for n in nodes}
    conns = wf.get("connections", {})

    def is_trigger_type(n):
        t = (n.get("type") or "").lower()
        return "trigger" in t or "webhook" in t

    # --- repair orphaned triggers -------------------------------------------
    # A real trigger (Manual/Schedule/Webhook) with NO outgoing connection means
    # the template's flow starts at a later node instead. Connect it to the
    # single node that has no incoming main edge (the intended entry point).
    incoming_main_pre = set()
    for src, conn_def in conns.items():
        for ctype, outputs in conn_def.items():
            for arr in outputs:
                for c in arr:
                    if isinstance(c, dict) and c.get("node") and ctype == "main":
                        incoming_main_pre.add(c["node"])
    for t in nodes:
        if not is_trigger_type(t):
            continue
        outgoing = conns.get(t["name"], {})
        has_main_out = any(ct == "main" for ct in outgoing)
        if has_main_out:
            continue
        candidates = [
            n["name"] for n in nodes
            if not is_trigger_type(n)
            and n["name"] not in incoming_main_pre
        ]
        if len(candidates) == 1:
            conns.setdefault(t["name"], {})["main"] = [
                [{"node": candidates[0], "type": "main", "index": 0}]
            ]

    incoming_main = set()
    attached = {}            # agent name -> [source names feeding it via ai_*]
    attached_sources = set()

    for src, conn_def in conns.items():
        for ctype, outputs in conn_def.items():
            for arr in outputs:
                for c in arr:
                    if not isinstance(c, dict) or not c.get("node"):
                        continue
                    if ctype == "main":
                        incoming_main.add(c["node"])
                    else:
                        attached.setdefault(c["node"], []).append(src)
                        attached_sources.add(src)

    triggers = [n["name"] for n in nodes if n["name"] not in incoming_main and n["name"] not in attached_sources]

    # BFS over main edges to assign columns
    col = {}
    queue = [(t, 0) for t in triggers]
    visited = set()
    while queue:
        name, depth = queue.pop(0)
        if name in visited:
            continue
        visited.add(name)
        col[name] = max(col.get(name, depth), depth)
        for ctype, outputs in (conns.get(name) or {}).items():
            if ctype != "main":
                continue
            for arr in outputs:
                for c in arr:
                    if isinstance(c, dict) and c.get("node") and c["node"] not in visited:
                        queue.append((c["node"], depth + 1))

    BASE_X, COL_W, BASE_Y, ROW_H = 620, 420, 360, 140
    cols = {}
    for name, depth in col.items():
        cols.setdefault(depth, []).append(name)

    for depth, names in cols.items():
        total_h = len(names) * ROW_H
        start_y = BASE_Y - (total_h - ROW_H) / 2
        for i, name in enumerate(sorted(names)):
            if name in by_name:
                by_name[name]["position"] = [BASE_X + depth * COL_W, int(start_y + i * ROW_H)]

    # AI sub-nodes stacked under their agent
    for target, sources in attached.items():
        if target not in by_name:
            continue
        tx, ty = by_name[target]["position"]
        for i, src in enumerate(sources):
            if src in by_name:
                by_name[src]["position"] = [tx, ty + 220 * (i + 1)]

    return wf


def post_layout(wf):
    """Per-template layout refinements that generic tidy() can't express.
    For the Sheets calendar workflow, move the mark-done branch (Set done flag
    -> Update status) onto its own lane below the publish column instead of
    mixing it in with the five platform publishes."""
    if wf.get("name") != "Schedule social media posts from a Google Sheets calendar":
        return wf
    by_name = {n["name"]: n for n in wf["nodes"]}
    pubs = sorted((n for n in wf["nodes"] if n.get("type") == NODE_TYPE), key=lambda n: n["name"])
    pub_x = 620 + 3 * 420
    pub_y = 360 - (len(pubs) * 140 - 140) / 2
    for i, n in enumerate(pubs):
        n["position"] = [pub_x, int(pub_y + i * 140)]
    lane_y = int(pub_y + len(pubs) * 140) + 200
    if "Set done flag" in by_name:
        by_name["Set done flag"]["position"] = [620 + 2 * 420, lane_y]
    if "Update status" in by_name:
        by_name["Update status"]["position"] = [pub_x, lane_y]
    return wf


def save(wf, filename):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(wf, f, indent=2)
    return path


# ----------------------------------------------------------------------------
# AI prompt + schema helpers
# ----------------------------------------------------------------------------

TEXT_PLATFORM_GUIDE = """- X (Twitter): under 280 characters, punchy, 2-3 hashtags.
- LinkedIn: professional, 3-4 short lines, end with a question or CTA.
- Facebook: friendly and conversational, 2-3 sentences.
- Bluesky: under 300 characters, warm and authentic.
- Mastodon: thoughtful, can be longer, include 2-3 hashtags.
- Threads: casual, 1-2 sentences."""

ALL_PLATFORM_GUIDE = """- Instagram: catchy caption with 3-5 hashtags.
- X (Twitter): under 280 characters, punchy, 2-3 hashtags.
- LinkedIn: professional, 3-4 short lines, end with a question or CTA.
- TikTok: short and energetic with 3-5 hashtags.
- Facebook: friendly and conversational, 2-3 sentences.
- Pinterest title: under 100 characters, keyword-rich.
- Pinterest description: 2-3 sentences with keywords.
- Bluesky: under 300 characters, warm and authentic.
- Mastodon: thoughtful, can be longer, include 2-3 hashtags.
- Threads: casual, 1-2 sentences."""


def text_schema(keys):
    return {"type": "object", "properties": {k: {"type": "string"} for k in keys}}


def caption_schema(keys):
    return {"type": "object", "properties": {k: {"type": "string"} for k in keys}}


# ----------------------------------------------------------------------------
# AI media generation nodes (Replicate: Seedance video, OpenAI gpt-image-2).
# Submit prediction -> poll status -> download binary, the standard pattern
# used by the top-ranked n8n templates in this niche.
# ----------------------------------------------------------------------------

def replicate_video_submit_node(name="Generate Video (Seedance)"):
    """Create a Seedance text-to-video prediction on Replicate.
    Body: { input: { prompt, duration, resolution, aspect_ratio } }."""
    return {
        "parameters": {
            "method": "POST",
            "url": "https://api.replicate.com/v1/models/bytedance/seedance-2.0/predictions",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ input: { prompt: $("AI Video Prompt Writer").item.json.output || $("Set video topic").item.json.topic, duration: 5, resolution: "720p", aspect_ratio: "16:9" } }) }}',
            "options": {},
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [0, 0],
        "credentials": {"replicateApi": {"id": "", "name": "Replicate account"}},
    }


def replicate_poll_node(name="Check Status"):
    """GET a Replicate prediction by id. Response: { status, output, ... }
    where status is starting|processing|succeeded|failed and output is the
    video URL once succeeded."""
    return {
        "parameters": {
            "method": "GET",
            "url": "=https://api.replicate.com/v1/predictions/{{ $json.id }}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "options": {},
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [0, 0],
        "credentials": {"replicateApi": {"id": "", "name": "Replicate account"}},
    }


def wait_node(name="Wait 30 Seconds", amount=30):
    return {
        "parameters": {"amount": amount},
        "id": rid(), "name": name, "type": "n8n-nodes-base.wait", "typeVersion": 1.1,
        "position": [0, 0], "webhookId": rid(),
    }


def if_node(name, condition_left, condition_right="COMPLETED", operation="equals"):
    """Boolean IF on two string values (v2 syntax)."""
    return {
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [
                    {
                        "id": rid(),
                        "leftValue": condition_left,
                        "rightValue": condition_right,
                        "operator": {"type": "string", "operation": operation},
                    }
                ],
                "combinator": "and",
            },
            "options": {},
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.if", "typeVersion": 2,
        "position": [0, 0],
    }


def openai_image_node(name="Generate Image (gpt-image-2)", size="1536x1024", quality="high"):
    """OpenAI images endpoint via HTTP Request (the built-in OpenAI node has no
    images action in most n8n versions, and HTTP keeps the template version-proof).
    Returns b64_json image data saved to binary property 'data'."""
    return {
        "parameters": {
            "method": "POST",
            "url": "https://api.openai.com/v1/images/generations",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": json.dumps({
                "model": "gpt-image-2",
                "prompt": "{{ $json.imagePrompt }}",
                "size": size,
                "quality": quality,
                "n": 1,
            }),
            "options": {"response": {"response": {"responseFormat": "autodetect"}}},
        },
        "id": rid(), "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
        "position": [0, 0],
        "credentials": {"openAiApi": {"id": "", "name": "OpenAI account"}},
    }


def code_extract_b64_node(name="Extract Image Binary", source_field="data[0].b64_json"):
    """Convert an OpenAI b64_json response into n8n binary data for upload."""
    js = (
        "const items = [];\n"
        "for (const item of $input.all()) {\n"
        "  const b64 = item.json." + source_field.replace("[0].", "[0]?.") + ";\n"
        "  if (!b64) throw new Error('No image data in response');\n"
        "  items.push({\n"
        "    json: { ...item.json },\n"
        "    binary: {\n"
        "      data: await this.helpers.prepareBinaryData(\n"
        "        Buffer.from(b64, 'base64'), 'generated.png', 'image/png'),\n"
        "    },\n"
        "  });\n"
        "}\n"
        "return items;"
    )
    return {
        "parameters": {"mode": "runOnceForAllItems", "language": "javaScript", "jsCode": js},
        "id": rid(), "name": name, "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [0, 0],
    }


# ----------------------------------------------------------------------------
# templates
# ----------------------------------------------------------------------------

templates = []

# --- A. single-platform posts ---
templates.append(workflow(
    "Post an image to Instagram",
    [manual_node(), publish_node("instagram", "Post to Instagram",
                                 caption="Here's what we shipped this week. Full breakdown in the comments.",
                                 media_url=SAMPLE_IMAGE)],
    link("When clicking 'Execute workflow'", "Post to Instagram"),
))

templates.append(workflow(
    "Post a video to Instagram",
    [manual_node(), publish_node("instagram", "Post to Instagram",
                                 caption="60 seconds on how to automate your posting.",
                                 media_url=SAMPLE_VIDEO, media_type="VIDEO")],
    link("When clicking 'Execute workflow'", "Post to Instagram"),
))

templates.append(workflow(
    "Download an image and post it to Instagram",
    [manual_node(), http_request_download_node(SAMPLE_IMAGE, name="Download image"),
     publish_node("instagram", "Post to Instagram",
                  caption="Posted straight from binary data, no upload URL step needed.",
                  media_source="binary", binary_property="data")],
    chain(["When clicking 'Execute workflow'", "Download image", "Post to Instagram"]),
))

templates.append(workflow(
    "Post text to X (Twitter)",
    [manual_node(), publish_node("x", "Post to X",
                                 caption="Automation is not about doing less. It is about doing the boring parts automatically so you can focus on the work that matters.")],
    link("When clicking 'Execute workflow'", "Post to X"),
))

templates.append(workflow(
    "Post text and an image to X (Twitter)",
    [manual_node(), publish_node("x", "Post to X",
                                 caption="Shipping a new workflow today. Here is a look at it.",
                                 medias=[media_item("IMAGE", SAMPLE_IMAGE)])],
    link("When clicking 'Execute workflow'", "Post to X"),
))

templates.append(workflow(
    "Post to LinkedIn",
    [manual_node(), publish_node("linkedin", "Post to LinkedIn",
                                 caption="We just automated our social media publishing end to end. "
                                         "What used to take an hour a day now takes one workflow. "
                                         "How much time do you spend scheduling posts?")],
    link("When clicking 'Execute workflow'", "Post to LinkedIn"),
))

templates.append(workflow(
    "Post a video to TikTok",
    [manual_node(), publish_node("tiktok", "Post to TikTok",
                                 caption="POV: your social media posts publish themselves #automation",
                                 medias=[media_item("VIDEO", SAMPLE_VIDEO)])],
    link("When clicking 'Execute workflow'", "Post to TikTok"),
))

templates.append(workflow(
    "Post to a Facebook Page",
    [manual_node(), publish_node("facebook", "Post to Facebook",
                                 caption="New post from our automation pipeline. Have a great week everyone!",
                                 medias=[media_item("IMAGE", SAMPLE_IMAGE)])],
    link("When clicking 'Execute workflow'", "Post to Facebook"),
))

templates.append(workflow(
    "Pin an image to Pinterest",
    [manual_node(), publish_node("pinterest", "Post to Pinterest",
                                 caption="A quick pin about social media automation.",
                                 board_id="your-board-id",
                                 medias=[media_item("IMAGE", SAMPLE_IMAGE)])],
    link("When clicking 'Execute workflow'", "Post to Pinterest"),
))

templates.append(workflow(
    "Post text to Bluesky",
    [manual_node(), publish_node("bluesky", "Post to Bluesky",
                                 caption="Small automation win today: my posts now publish themselves across the fediverse.")],
    link("When clicking 'Execute workflow'", "Post to Bluesky"),
))

templates.append(workflow(
    "Post to Mastodon",
    [manual_node(), publish_node("mastodon", "Post to Mastodon",
                                 caption="Took the manual work out of posting today. One workflow, every platform. #automation #indieweb",
                                 medias=[media_item("IMAGE", SAMPLE_IMAGE)])],
    link("When clicking 'Execute workflow'", "Post to Mastodon"),
))

templates.append(workflow(
    "Post to Threads",
    [manual_node(), publish_node("threads", "Post to Threads",
                                 caption="Automation hot take: the best workflow is the one you actually run.",
                                 medias=[media_item("IMAGE", SAMPLE_IMAGE)])],
    link("When clicking 'Execute workflow'", "Post to Threads"),
))

# --- B. cross-posting (one node per platform, fanned out) ---
all9 = ["instagram", "x", "linkedin", "tiktok", "facebook", "pinterest", "bluesky", "mastodon", "threads"]
microblog5 = ["x", "bluesky", "mastodon", "threads", "linkedin"]
visual4 = ["instagram", "pinterest", "facebook", "threads"]


def _publish_all(platforms, caption, image_url=None, video_url=None, publish_mode="NOW", schedule_date=""):
    """Build one publish node per platform, all fed the same caption (and image when visual)."""
    nodes = []
    for p in platforms:
        kw = {"caption": caption, "publish_mode": publish_mode, "schedule_date": schedule_date}
        if p == "instagram":
            if image_url:
                kw["media_url"] = image_url
        elif p == "pinterest":
            kw["board_id"] = "your-board-id"
            if image_url:
                kw["medias"] = [media_item("IMAGE", image_url)]
        else:
            # bluesky is text-only in the node schema
            if image_url and p != "bluesky":
                kw["medias"] = [media_item("IMAGE", image_url)]
            elif video_url and p != "bluesky":
                kw["medias"] = [media_item("VIDEO", video_url)]
        nodes.append(publish_node(p, f"Post to {p}", **kw))
    return nodes


templates.append(workflow(
    "Cross-post a post to every social media platform",
    [manual_node()] + _publish_all(all9, "Post everywhere caption", image_url=SAMPLE_IMAGE, video_url=SAMPLE_VIDEO),
    fan_out("When clicking 'Execute workflow'", [n["name"] for n in _publish_all(all9, "Post everywhere caption", image_url=SAMPLE_IMAGE, video_url=SAMPLE_VIDEO)]),
))

templates.append(workflow(
    "Cross-post text to X, Bluesky, Mastodon, Threads, and LinkedIn",
    [manual_node(), set_node("Set post text", [{"name": "caption", "value": "One post, every network. Type your text here."}])]
    + _publish_all(microblog5, "={{ $json.caption }}"),
    fan_out("Set post text", [n["name"] for n in _publish_all(microblog5, "={{ $json.caption }}")]),
))

templates.append(workflow(
    "Cross-post an image to Instagram, Pinterest, Facebook, and Threads",
    [manual_node(), set_node("Set post image", [
        {"name": "caption", "value": "A caption that works across visual platforms."},
        {"name": "imageUrl", "value": SAMPLE_IMAGE},
    ])]
    + _publish_all(visual4, "={{ $json.caption }}", image_url="={{ $json.imageUrl }}"),
    fan_out("Set post image", [n["name"] for n in _publish_all(visual4, "={{ $json.caption }}", image_url="={{ $json.imageUrl }}")]),
))

# --- C. scheduling ---
templates.append(workflow(
    "Schedule a social media post for a future date",
    [manual_node()]
    + _publish_all(["x", "linkedin"], "Scheduled ahead of time: this post went out without touching a button.",
                   publish_mode="SCHEDULE", schedule_date="2026-08-20T09:00:00-03:00"),
    fan_out("When clicking 'Execute workflow'",
            [n["name"] for n in _publish_all(["x", "linkedin"], "Scheduled ahead of time: this post went out without touching a button.",
                                             publish_mode="SCHEDULE", schedule_date="2026-08-20T09:00:00-03:00")]),
))

templates.append(workflow(
    "Schedule a daily post to X, Bluesky, and Mastodon",
    [schedule_node(field="days", interval=1)]
    + _publish_all(["x", "bluesky", "mastodon"], "Your daily post"),
    fan_out("Schedule Trigger", [n["name"] for n in _publish_all(["x", "bluesky", "mastodon"], "Your daily post")]),
))

# --- D. content sources ---
templates.append(workflow(
    "Auto-post RSS feed items to every social media platform",
    [schedule_node(field="hours", interval=6), rss_node("https://example.com/feed.xml", name="RSS Read")]
    + _publish_all(microblog5 + ["facebook"], "={{ $json.title }} {{ $json.link }}"),
    fan_out("RSS Read", [n["name"] for n in _publish_all(microblog5 + ["facebook"], "={{ $json.title }} {{ $json.link }}")]),
))

templates.append(workflow(
    "Auto-post RSS feed items to Bluesky and Mastodon",
    [schedule_node(field="hours", interval=1), rss_node("https://example.com/feed.xml", name="RSS Read")]
    + _publish_all(["bluesky", "mastodon"], "={{ $json.title }} {{ $json.link }}"),
    fan_out("RSS Read", [n["name"] for n in _publish_all(["bluesky", "mastodon"], "={{ $json.title }} {{ $json.link }}")]),
))

templates.append(workflow(
    "Auto-post blog posts to X, LinkedIn, and Facebook",
    [schedule_node(field="days", interval=1), rss_node("https://example.com/blog/feed.xml", name="Blog RSS")]
    + _publish_all(["x", "linkedin", "facebook"], "New on the blog: {{ $json.title }} {{ $json.link }}"),
    fan_out("Blog RSS", [n["name"] for n in _publish_all(["x", "linkedin", "facebook"], "New on the blog: {{ $json.title }} {{ $json.link }}")]),
))

# --- E. AI generation (real OpenAI nodes) ---

flagship_prompt = """You are a social media writer. Write one post for each platform below about the topic, matching each platform's tone and length.

Topic: {{ $json.topic }}
Tone: {{ $json.tone }}

Guidelines:
""" + ALL_PLATFORM_GUIDE + """

Return plain text with no markdown formatting."""

flagship_model, flagship_parser, flagship_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", text_schema(
        ["instagram", "twitter", "linkedin", "tiktok", "facebook", "pinterest_title",
         "pinterest_description", "bluesky", "mastodon", "threads"])),
    agent_node("AI Content Generator", flagship_prompt),
)
# per-platform caption expressions (the agent emits one key per platform)
FLAGSHIP_CAPTIONS = {
    "instagram": "={{ $json.output.instagram }}",
    "x": "={{ $json.output.twitter }}",
    "linkedin": "={{ $json.output.linkedin }}",
    "tiktok": "={{ $json.output.tiktok }}",
    "facebook": "={{ $json.output.facebook }}",
    "pinterest": "={{ $json.output.pinterest_description }}",
    "bluesky": "={{ $json.output.bluesky }}",
    "mastodon": "={{ $json.output.mastodon }}",
    "threads": "={{ $json.output.threads }}",
}


def _publish_ai(platforms, captions, image_url=None, publish_mode="NOW", schedule_date=""):
    nodes = []
    for p in platforms:
        kw = {"caption": captions[p], "publish_mode": publish_mode, "schedule_date": schedule_date}
        if p == "instagram":
            if image_url:
                kw["media_url"] = image_url
        elif p == "pinterest":
            kw["board_id"] = "your-board-id"
            if image_url:
                kw["medias"] = [media_item("IMAGE", image_url)]
        elif image_url and p != "bluesky":
            kw["medias"] = [media_item("IMAGE", image_url)]
        nodes.append(publish_node(p, f"Post to {p}", **kw))
    return nodes


templates.append(workflow(
    "Generate AI captions and publish to every social media platform",
    [manual_node(),
     set_node("Set post topic", [
         {"name": "topic", "value": "How small teams can automate their social media posting"},
         {"name": "tone", "value": "friendly and expert"},
     ]),
     flagship_agent, flagship_model, flagship_parser]
    + _publish_ai(all9, FLAGSHIP_CAPTIONS, image_url=SAMPLE_IMAGE),
    ai_block_connections("When clicking 'Execute workflow'", "Set post topic", "AI Content Generator",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(all9, FLAGSHIP_CAPTIONS, image_url=SAMPLE_IMAGE)]),
))

ig_pinterest_prompt = """You are a social media writer. Write a caption and a Pinterest title and description for the topic below.

Topic: {{ $json.topic }}
Image description (for context): a promotional graphic for the topic

Guidelines:
- Instagram: a catchy caption with emojis and 3-5 hashtags.
- Pinterest title: under 100 characters, keyword-rich.
- Pinterest description: 2-3 sentences with keywords.

Return plain text with no markdown."""

igp_model, igp_parser, igp_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", caption_schema(["instagram", "pinterest_title", "pinterest_description"])),
    agent_node("AI Caption Generator", ig_pinterest_prompt),
)
templates.append(workflow(
    "Generate AI captions and post to Instagram and Pinterest",
    [manual_node(),
     set_node("Set post topic", [{"name": "topic", "value": "Automate your social media with one workflow"}]),
     igp_agent, igp_model, igp_parser]
    + _publish_ai(["instagram", "pinterest"],
                  {"instagram": "={{ $json.output.instagram }}",
                   "pinterest": "={{ $json.output.pinterest_description }}"},
                  image_url=SAMPLE_IMAGE),
    ai_block_connections("When clicking 'Execute workflow'", "Set post topic", "AI Caption Generator",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(["instagram", "pinterest"],
                                                          {"instagram": "={{ $json.output.instagram }}",
                                                           "pinterest": "={{ $json.output.pinterest_description }}"},
                                                          image_url=SAMPLE_IMAGE)]),
))

daily_bsky_masto_prompt = """You are a social media writer. Write a fresh, original post for Bluesky and Mastodon about the theme below. Vary the angle and wording each run so posts never repeat.

Theme: {{ $json.theme }}

Guidelines:
- Bluesky: under 300 characters, warm and authentic, 1-2 hashtags.
- Mastodon: thoughtful, can be longer, 2-3 hashtags.

Return plain text with no markdown."""

dbm_model, dbm_parser, dbm_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", text_schema(["bluesky", "mastodon"])),
    agent_node("AI Daily Post Generator", daily_bsky_masto_prompt),
)
templates.append(workflow(
    "Generate daily AI posts for Bluesky and Mastodon",
    [schedule_node(field="days", interval=1),
     set_node("Set post theme", [{"name": "theme", "value": "indie hacking and automation"}]),
     dbm_agent, dbm_model, dbm_parser]
    + _publish_ai(["bluesky", "mastodon"],
                  {"bluesky": "={{ $json.output.bluesky }}", "mastodon": "={{ $json.output.mastodon }}"}),
    ai_block_connections("Schedule Trigger", "Set post theme", "AI Daily Post Generator",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(["bluesky", "mastodon"],
                                                          {"bluesky": "={{ $json.output.bluesky }}",
                                                           "mastodon": "={{ $json.output.mastodon }}"})]),
))

rss_summary_prompt = """You are a social media writer. Summarize the article below into a short, engaging post with hashtags.

Article title: {{ $json.title }}
Article snippet: {{ $json.contentSnippet }}
Article link: {{ $json.link }}

Return plain text. Keep the summary under 250 characters, then append the link and 2-3 hashtags."""

rssa_model, rssa_parser, rssa_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", caption_schema(["summary", "hashtags"])),
    agent_node("AI Summary Generator", rss_summary_prompt),
)
templates.append(workflow(
    "Auto-post RSS items to Bluesky, Mastodon, and Threads with AI summaries",
    [schedule_node(field="hours", interval=1), rss_node("https://example.com/feed.xml", name="RSS Read"),
     rssa_agent, rssa_model, rssa_parser]
    + _publish_ai(["bluesky", "mastodon", "threads"],
                  {"bluesky": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}",
                   "mastodon": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}",
                   "threads": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}"}),
    ai_block_connections("Schedule Trigger", "RSS Read", "AI Summary Generator",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(["bluesky", "mastodon", "threads"],
                                                          {"bluesky": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}",
                                                           "mastodon": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}",
                                                           "threads": "={{ $json.output.summary }} {{ $json.link }} {{ $json.output.hashtags }}"})]),
))

pick_ready_js = (
    "const out = [];\n"
    "for (const item of $input.all()) {\n"
    "  const ready = String(item.json.ready || '').toLowerCase();\n"
    "  const due = item.json.date && new Date(item.json.date).getTime() > Date.now();\n"
    "  if ((ready === 'yes' || ready === 'true' || ready === 'ready') && due) out.push(item);\n"
    "}\n"
    "return out;"
)
sheets_publish = _publish_all(microblog5, "={{ $json.caption }}",
                              publish_mode="SCHEDULE", schedule_date="={{ $json.date }}")
sheets_pub_names = [n["name"] for n in sheets_publish]
templates.append(workflow(
    "Schedule social media posts from a Google Sheets calendar",
    [schedule_node(field="hours", interval=1),
     google_sheets_read(name="Content calendar"),
     code_node("Pick ready rows", pick_ready_js),
     set_node("Set done flag", [{"name": "date", "value": "={{ $json.date }}"},
                                {"name": "ready", "value": "done"}]),
     sheets_update_node("Update status", "date")]
    + sheets_publish,
    fan_out("Schedule Trigger", ["Content calendar"]),
))
_t = templates[-1]
_t["connections"].update(link("Content calendar", "Pick ready rows"))
_t["connections"]["Pick ready rows"] = {"main": [[{"node": nm, "type": "main", "index": 0} for nm in sheets_pub_names + ["Set done flag"]]]}
_t["connections"].update(link("Set done flag", "Update status"))

repurpose_prompt = """You are a content repurposing expert. Turn the long-form content below into a platform-native post for each platform.

Source content:
{{ $json.content }}

Guidelines:
""" + TEXT_PLATFORM_GUIDE + """

Return plain text with no markdown."""

rep_model, rep_parser, rep_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", text_schema(["twitter", "linkedin", "facebook", "bluesky", "mastodon", "threads"])),
    agent_node("AI Repurposing Engine", repurpose_prompt),
)
republish_platforms = ["x", "linkedin", "facebook", "bluesky", "mastodon", "threads"]
templates.append(workflow(
    "Repurpose one piece of content into posts for every platform",
    [manual_node(),
     set_node("Set source content", [{"name": "content", "value": "Paste your long-form article or script here. The AI rewrites it for each platform."}]),
     rep_agent, rep_model, rep_parser]
    + _publish_ai(republish_platforms,
                  {"x": "={{ $json.output.twitter }}", "linkedin": "={{ $json.output.linkedin }}",
                   "facebook": "={{ $json.output.facebook }}", "bluesky": "={{ $json.output.bluesky }}",
                   "mastodon": "={{ $json.output.mastodon }}", "threads": "={{ $json.output.threads }}"}),
    ai_block_connections("When clicking 'Execute workflow'", "Set source content", "AI Repurposing Engine",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(republish_platforms,
                                                          {"x": "={{ $json.output.twitter }}", "linkedin": "={{ $json.output.linkedin }}",
                                                           "facebook": "={{ $json.output.facebook }}", "bluesky": "={{ $json.output.bluesky }}",
                                                           "mastodon": "={{ $json.output.mastodon }}", "threads": "={{ $json.output.threads }}"})]),
))

# Draft-for-review: the AI writes for all 9 platforms, everything saves as DRAFT
# in SocialRobot where the user reviews and publishes manually.
draft_prompt = """You are a social media writer. Write one post for each platform below about the theme. Vary the angle and wording each run so drafts never repeat.

Theme: {{ $json.theme }}

Guidelines:
""" + ALL_PLATFORM_GUIDE + """

Return plain text with no markdown formatting."""

draft_model, draft_parser, draft_agent = (
    openai_model_node("OpenAI Chat Model"),
    parser_node("Content Schema", text_schema(
        ["instagram", "twitter", "linkedin", "tiktok", "facebook", "pinterest_title",
         "pinterest_description", "bluesky", "mastodon", "threads"])),
    agent_node("AI Draft Generator", draft_prompt),
)
draft_captions = dict(FLAGSHIP_CAPTIONS)
draft_captions["pinterest"] = "={{ $json.output.pinterest_description }}"
templates.append(workflow(
    "Create AI post drafts for review before publishing",
    [schedule_node(field="days", interval=1),
     set_node("Set post theme", [{"name": "theme", "value": "indie hacking and automation"}]),
     draft_agent, draft_model, draft_parser]
    + _publish_ai(all9, draft_captions, publish_mode="DRAFT"),
    ai_block_connections("Schedule Trigger", "Set post theme", "AI Draft Generator",
                         "OpenAI Chat Model", "Content Schema",
                         [n["name"] for n in _publish_ai(all9, draft_captions, publish_mode="DRAFT")]),
))

# --- E2. AI media generation (the highest-view pattern in the gallery) ---

# 1) Seedance text-to-video -> TikTok
video_prompt_agent = agent_node(
    "AI Video Prompt Writer",
    """You are a short-form video director. Turn the topic below into one vivid,
concrete video generation prompt for an AI text-to-video model. Describe the
scene, camera movement, lighting, and mood in one flowing paragraph of at most
120 words. No camera jargon a model would not understand. Return only the prompt.

Topic: {{ $json.topic }}""",
    has_output_parser=False,
)
vpm_model = openai_model_node("OpenAI Chat Model")
seedance_submit = replicate_video_submit_node()
seedance_poll = replicate_poll_node()
seedance_wait = wait_node()
seedance_if = if_node("Video Ready?", "={{ $json.status }}", "succeeded")
video_download = http_request_download_node(
    "={{ $json.output }}",
    name="Download Video",
)
tiktok_publish = publish_node("tiktok", "Post to TikTok",
                              caption="={{ $('Set video topic').item.json.topic }} #ai #automation",
                              medias=[media_item("VIDEO", "", media_source="binary")])
templates.append(workflow(
    "Generate AI videos with Seedance and post them to TikTok",
    [manual_node(),
     set_node("Set video topic", [{"name": "topic",
        "value": "A cozy desk setup at golden hour while code compiles"}]),
     video_prompt_agent, vpm_model,
     seedance_submit, seedance_poll, seedance_if,
     seedance_wait, video_download, tiktok_publish],
    {},
    ))
_t = templates[-1]
for a, b in [("When clicking 'Execute workflow'", "Set video topic"),
             ("Set video topic", "AI Video Prompt Writer"),
             ("AI Video Prompt Writer", "Generate Video (Seedance)"),
             ("Generate Video (Seedance)", "Check Status"),
             ("Check Status", "Video Ready?")]:
    _t["connections"].update(link(a, b))
# IF true -> download -> publish;  IF false -> wait -> poll again (loop)
_t["connections"]["Video Ready?"] = {"main": [
    [{"node": "Download Video", "type": "main", "index": 0}],
    [{"node": "Wait 30 Seconds", "type": "main", "index": 0}],
]}
_t["connections"].update(link("Wait 30 Seconds", "Check Status"))
_t["connections"].update(link("Download Video", "Post to TikTok"))
_t["connections"]["OpenAI Chat Model"] = {
    "ai_languageModel": [[{"node": "AI Video Prompt Writer", "type": "ai_languageModel", "index": 0}]]}

# 2) gpt-image-2 -> Instagram + Pinterest
extract_js = (
    "const items = [];\n"
    "for (const item of $input.all()) {\n"
    "  const b64 = item.json.data?.[0]?.b64_json;\n"
    "  if (!b64) throw new Error('No image data in response');\n"
    "  const prompt = $('Set image idea').first().json.imagePrompt || 'AI-generated artwork';\n"
    "  const caption = `${prompt}.\n\nWhat do you think? #aiart #designinspo #smallbusiness`;\n"
    "  const ptitle = prompt.length > 95 ? prompt.slice(0, 95).trimEnd() : prompt;\n"
    "  const pdesc = `${prompt}. Created with gpt-image-2 and published with SocialRobot. Follow for more visual ideas.`;\n"
    "  items.push({\n"
    "    json: { instagram: caption, pinterest_title: ptitle, pinterest_description: pdesc },\n"
    "    binary: { data: await this.helpers.prepareBinaryData(\n"
    "      Buffer.from(b64, 'base64'), 'generated.png', 'image/png') },\n"
    "  });\n"
    "}\n"
    "return items;"
)
image_extract = code_extract_b64_node(name="Extract Image Binary")
image_extract["parameters"]["jsCode"] = extract_js
ig_pin_publish = _publish_ai(
    ["instagram", "pinterest"],
    {"instagram": "={{ $json.instagram }}",
     "pinterest": "={{ $json.pinterest_description }}"},
    image_url=SAMPLE_IMAGE)
# both publish nodes take the GENERATED image from binary property 'data'
# (Instagram: flat fields; Pinterest: medias collection)
for n in ig_pin_publish:
    p = n["parameters"]
    if p.get("resource") == "instagram":
        p.pop("mediaUrl", None)
        p["mediaSource"] = "binary"
        p["mediaType"] = "IMAGE"
        p["binaryPropertyName"] = "data"
    else:
        p.pop("medias", None)
        p["medias"] = [{"mediaSource": "binary", "mediaType": "IMAGE", "binaryPropertyName": "data"}]
templates.append(workflow(
    "Generate AI images with gpt-image-2 and post them to Instagram and Pinterest",
    [manual_node(),
     set_node("Set image idea", [{"name": "imagePrompt",
        "value": "A minimalist flat-lay of a laptop, coffee, and notebook in soft violet morning light"}]),
     openai_image_node(name="Generate Image (gpt-image-2)"),
     image_extract]
    + ig_pin_publish,
    {},
    ))
_t = templates[-1]
for a, b in [("When clicking 'Execute workflow'", "Set image idea"),
             ("Set image idea", "Generate Image (gpt-image-2)"),
             ("Generate Image (gpt-image-2)", "Extract Image Binary")]:
    _t["connections"].update(link(a, b))
_pub_names = [n["name"] for n in ig_pin_publish]
_t["connections"]["Extract Image Binary"] = {"main": [[{"node": nm, "type": "main", "index": 0} for nm in _pub_names]]}

# --- F. management ---
templates.append(workflow(
    "List scheduled social media posts",
    [manual_node(), sr_get_all("List scheduled posts", filters={"status": "SCHEDULED"})],
    link("When clicking 'Execute workflow'", "List scheduled posts"),
))
templates.append(workflow(
    "List failed social media posts",
    [manual_node(), sr_get_all("List failed posts", filters={"status": "FAILED"})],
    link("When clicking 'Execute workflow'", "List failed posts"),
))
templates.append(workflow(
    "Get a social media post by ID",
    [manual_node(), sr_get("Get post")],
    link("When clicking 'Execute workflow'", "Get post"),
))
templates.append(workflow(
    "Delete a social media post",
    [manual_node(), sr_delete("Delete post")],
    link("When clicking 'Execute workflow'", "Delete post"),
))
templates.append(workflow(
    "Reschedule a social media post",
    [manual_node(), sr_reschedule("Reschedule post")],
    link("When clicking 'Execute workflow'", "Reschedule post"),
))
templates.append(workflow(
    "List connected social media accounts",
    [manual_node(), sr_accounts("List accounts")],
    link("When clicking 'Execute workflow'", "List accounts"),
))


def slug(name):
    return name.lower().replace(" ", "-").replace("/", "-")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    written = []
    for wf in templates:
        wf = tidy(wf)                 # auto-arrange nodes
        wf = post_layout(wf)          # per-template layout refinements
        wf = annotate(wf)             # sticky notes + descriptive node names
        fn = slug(wf["name"]) + ".json"
        path = save(wf, fn)
        written.append((fn, wf["name"]))
        with open(path) as f:
            json.load(f)

    # remove stale template files that are no longer generated
    generated = {fn for fn, _ in written}
    for existing in os.listdir(OUT_DIR):
        if existing.endswith(".json") and existing not in generated:
            os.remove(os.path.join(OUT_DIR, existing))

    print(f"Generated {len(written)} annotated templates in {OUT_DIR} (removed stale files):")
    for fn, name in sorted(written):
        print(f"  {fn}  <-  {name}")


if __name__ == "__main__":
    main()
