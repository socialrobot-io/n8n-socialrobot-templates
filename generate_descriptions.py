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

CAROUSEL_TO_REEL_MD = """## Who it's for
Cafés, salons, makers, online shops and solo founders who already design Instagram carousels and want the reach of Reels and TikTok videos without an editing app or render fees.

## What it does
1. Form: upload 2-10 slides in order, add a caption, seconds per slide (1.5-6, default 2.5) and an optional music URL. You can also choose whether to send a TikTok photo slideshow.
2. Check ffmpeg Installed: stops with a clear message if ffmpeg is missing.
3. Slides are written to a temp folder (temp_dir/<execution id>) with Read/Write Files from Disk.
4. ffmpeg (Execute Command) builds a 1080×1920, 30 fps H.264 MP4:
   - Each slide sits on a blurred 9:16 background, so square and 4:5 slides keep their text.
   - Each slide gets a zoom in, zoom out or pan (zoompan).
   - 0.5 s crossfades (xfade) between slides.
   - Optional music is looped or trimmed to the video length and fades out at the end.
5. The MP4 is read back, and file size and the real duration from the MP4 header are checked.
6. SocialRobot:
   - TikTok inbox draft (Post Mode Send to Inbox (Draft), no title on video).
   - Optional Instagram Reel (isReel: true), Facebook Reel and Threads video, connected but disabled.
   - Optional TikTok photo slideshow draft with the original slides (1-35, optional title up to 90 characters). The images are sent as binary; SocialRobot uploads them to its own storage, so no public URLs are needed.
7. Cleanup: the temp folder is deleted after success, and after any error before the run stops with a readable message.

## Requirements
- Self-hosted n8n with ffmpeg installed. This template doesn't run on n8n Cloud (no Execute Command node, no ffmpeg).
  - Docker: FROM docker.n8n.io/n8nio/n8n:latest + USER root + RUN apk add --no-cache ffmpeg + USER node.
  - Debian/Ubuntu: apt install ffmpeg.
- n8n 2.x: enable Execute Command with NODES_EXCLUDE=[], and keep temp_dir inside N8N_RESTRICT_FILE_ACCESS_TO (default ~/.n8n-files). The default is /home/node/.n8n-files/carousel-to-reel/<execution id>.
- The community node @socialrobot-io/n8n-nodes-socialrobot 3.1.1+ (verified). On self-hosted n8n, install it under Settings → Community Nodes.
- A SocialRobot account with TikTok connected (and Instagram/Facebook/Threads if you enable those nodes).

## Cost
$0 per run. Rendering happens on your server, with no render API and no AI model.

## Customize
- Set Render Settings: temp_dir, seconds per slide, crossfade length, transition (any ffmpeg xfade name, such as fade, slideleft or circleopen), motion list, zoom amount, size, fps and limits.
- Build ffmpeg Command: add a logo overlay or text with drawtext.
- Use a Google Drive trigger instead of the form, as long as it outputs one binary per slide.

## Good practice
- Pan-and-zoom isn't generative AI, so the Instagram AI label is off by default. If your slides were made with AI, turn on AI-Generated Content in the Instagram node and the AI-generated content label in TikTok. The node doesn't send TikTok's AI label for inbox drafts.
- Only use music you have the rights to. You can also add sound in the TikTok app.
- The music URL is passed to ffmpeg only if it's a plain http(s) link, and all paths are shell-quoted.
- SocialRobot doesn't publish to YouTube.

## Why it's not a duplicate
- The existing carousel templates (4028, 3524, 8989, 12413) generate or upload image carousels.
- The slideshow templates (20592, 17181) turn blog posts into image slideshows.
- No gallery template converts an existing carousel into a pan-and-zoom video (search "carousel to reel", 16 Oct 2026).

## SEO
- Primary keywords: convert carousel to reel, instagram carousel to reel, carousel to video, ffmpeg slideshow, tiktok slideshow.
"""

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
    # Custom curated description for the ffmpeg-based carousel-to-reel template
    if wf.get("name") == "Convert Instagram carousels to Reels and TikTok slideshow videos with ffmpeg and SocialRobot":
        return CAROUSEL_TO_REEL_MD.strip()
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
    # Special notes for the Seedance 2.5 TikTok Shop template
    if wf.get("name") == "Create TikTok Shop product videos with Seedance 2.5 and save them as TikTok drafts via SocialRobot":
        parts.append("6. Photos are optional: upload zero to four product photos. With none, the video is generated from the text brief only.")
        parts.append("7. The workflow polls Replicate every 20 seconds for up to 30 minutes until the job succeeds, fails, or times out.")
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
