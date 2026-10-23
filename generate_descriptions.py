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
REALESTATE_WALKTHROUGH_MD = """## Who it's for

Listing agents and brokerages who already have a set of listing photos and want a vertical walkthrough video for TikTok, Instagram Reels, Facebook Reels, and LinkedIn, without filming a tour.

## What it does

1. A form takes 3 to 8 listing photos plus the address, price, beds, baths, size, features, agent and brokerage, and a listing link.
2. Photos are sorted by file name (numeric order, so `01-exterior.jpg` comes before `02-kitchen.jpg`), uploaded to fal storage, and center-cropped to 9:16. Kling 3.0 has no aspect-ratio field, so the start image sets the frame.
3. Consecutive photos are paired into room clips. An optional OpenAI step (`gpt-6-luna`, vision, low detail) writes one camera-move prompt per pair and a caption per network. If it fails, the workflow keeps going with a default camera prompt and a template caption.
4. Each pair is rendered as a 5 second Kling 3.0 Standard clip with no audio, through the fal queue, with polling, a 60 minute timeout, and a cancel path when a job fails or times out.
5. The clips are stitched by `fal-ai/ffmpeg-api/merge-videos` (a cloud call, so it runs on n8n Cloud with no ffmpeg binary), then checked for file size and duration by reading the MP4 `mvhd` atom.
6. The video is sent to TikTok as an **UPLOAD draft** through the SocialRobot community node. Instagram Reel, Facebook Reel, and LinkedIn video are in the workflow but **disabled**. LinkedIn goes through the SocialRobot HTTP API because the community node's LinkedIn target does not send the `videoMetadata` the API requires for video.

Every caption ends with a fixed AI-disclosure line. The prompt step is told to stay inside fair-housing rules: no claims about who lives nearby, no school quality, no "safe" or "family" language.

## Requirements

- n8n (self-hosted or Cloud). No Execute Command node and no ffmpeg on the machine.
- A fal API key, stored as an n8n Header Auth credential: header name `Authorization`, value `Key <FAL_KEY>`.
- The SocialRobot community node, with an `x-api-key` credential for `https://socialrobot.io/api/v1`.
- Optional: an OpenAI credential for the vision step. Turn it off with `use_openai = false` in **Set Walkthrough Configurations**.
- A TikTok account connected in SocialRobot. Publishing the draft is done by hand in TikTok, including the AI-generated label, which this workflow does not set for you.

## Cost

Kling 3.0 Standard, no audio, is $0.084 per second, so a 5 second clip is $0.42. With the default of no audio:

| Photos | Clips | Kling cost |
|---|---|---|
| 3 | 2 | $0.84 |
| 6 | 5 | $2.10 |
| 8 | 7 | $2.94 |

Audio raises it to $0.126 per second. Kling 3.0 Pro is $0.112 per second ($2.80 for 5 clips). fal lists the crop and merge utilities at $0 compute-seconds; treat that as unverified until you see a real invoice. OpenAI adds a few cents per run and was not priced here. fal's default concurrency is 1, so clips render one after another and a full run can take a while. Cancelling a job that is already `IN_PROGRESS` may still be billed.

## Customize

All of it lives in **Set Walkthrough Configurations**:

- `video_model` — `fal-ai/kling-video/v3/standard/image-to-video` by default. The sticky note **Switching to Kling 4.0 later** explains the swap: v4 takes `duration` as an integer and drops the v3-only fields, which the request builder already handles.
- `clip_seconds`, `generate_audio`, `cfg_scale`, `negative_prompt`, `default_camera_prompt`.
- `crop_to_vertical`, `sort_photos_by_file_name`, `min_photos`, `max_photos`.
- `use_openai`, `caption_tone`, `extra_hashtags`.
- `ai_label_line` and `brokerage_footer` — both are appended to every caption. Do not clear the AI line.
- `poll_every_seconds`, `timeout_minutes`, `max_file_mb`, `min_seconds`, `max_seconds`.
- `linkedin_account_id` — required only if you enable the LinkedIn node.

## Good practice

- The walkthrough is an illustration made from real photos, not a recording of the property. Keep the AI line, and say so wherever the video is posted.
- Fair housing: do not let captions describe the people, the neighborhood demographics, schools, crime, or "family-friendly". The prompt guardrails say this; a human should still read the draft before it goes out.
- TikTok's AI-generated label is not set by this workflow. Add it when you publish the draft.
- Check your MLS rules before posting a generated tour. Some MLSs restrict altered or synthesized media.
- No fake reviews, no testimonials, no real people's likenesses. Don't upload photos that show occupants.
- SocialRobot does not require an approval step before every post. The optional networks are disabled so a run only creates a TikTok draft unless you deliberately turn the others on.

## Why it's not a duplicate

Checked the n8n gallery on 19 Oct 2026, including templates published after 16 Oct (search index lagged, so IDs were scanned through 21225):

- **16854** is a real-estate content idea generator, not a photo-to-video pipeline.
- **20306** posts property cards from Airtable and Orshot to Instagram and TikTok. It does not render video from listing photos.
- **20261** and **17664** are social scheduling and repurposing templates, not listing walkthroughs.
- **21141** is unrelated to listing video.
- **21079** is SocialRobot's own story-series template, published 16 Oct, and does not use Kling or listing photos.

Nothing in the gallery turns a set of listing photos into a Kling walkthrough and posts it through SocialRobot.

## SEO keywords

real estate walkthrough, listing photos to video, AI home tour, Kling 3.0, Kling image to video, n8n real estate, SocialRobot, TikTok real estate draft, Instagram Reel listing, fair housing caption, fal.ai ffmpeg merge, vertical 9:16 listing video

## Community node

This workflow uses the SocialRobot community node. Community nodes are not maintained by n8n, and you install them at your own risk. The node is only needed for the TikTok draft and the optional Instagram and Facebook posts. LinkedIn uses a plain HTTP Request node against the SocialRobot API.
"""

FOOD_ASMR_VIDEO_MD = """## Who it's for

Cafés, bakeries, coffee bars and small restaurants that already take phone photos of their food and want short, vertical food ASMR videos for Instagram Reels, Facebook Reels, TikTok and Threads, without filming or editing.

## What it does

1. A form takes one real photo of a dish, pastry or drink, plus the dish name and, optionally, ingredients, price, availability, business name and a location or link.
2. The photo is uploaded to fal storage and center-cropped to 9:16. Kling 3.0 has no aspect-ratio field, so the photo sets the frame.
3. An optional OpenAI step (`gpt-6-luna`, vision, low detail) looks at the photo and writes 1 to 3 close-up shot prompts (macro push-in, slow texture pan, rack focus, slow orbit) with matching ASMR sound, plus a caption for each network. Captions may only use the facts typed into the form. If OpenAI is off or fails, template shots and captions are used instead.
4. One Kling 3.0 Standard image-to-video job renders every shot in a single 10-second clip with native audio (crackle, crunch, sizzle, quiet café ambience), so no stitching step is needed. It runs through the fal queue with polling, a 30-minute timeout, and a cancel request if the job times out.
5. The file is downloaded and checked for size and real duration by reading the MP4 `mvhd` atom.
6. The video is sent to TikTok as an **UPLOAD draft** through the SocialRobot community node. Instagram Reel (with Instagram's AI label on), Facebook Reel and Threads video are already in the workflow but **disabled**.

Every caption ends with a fixed line, "AI-generated video made from our real photo." Every problem ends in one readable error message.

## Requirements

- n8n, self-hosted or Cloud. The workflow does not use an Execute Command node or ffmpeg.
- A fal API key, stored as an n8n Header Auth credential: header name `Authorization`, value `Key <FAL_KEY>`.
- The SocialRobot community node `@socialrobot-io/n8n-nodes-socialrobot` (3.1.1 or later), with your SocialRobot API key.
- A TikTok account connected in SocialRobot. To post to Instagram, Facebook or Threads, connect those accounts and enable their nodes.
- Optional: an OpenAI credential for the vision and caption step. To skip it, set `use_openai = false` in **Configure Video Settings**.

## Cost

These are fal list prices, checked on 21 Oct 2026. Kling 3.0 Standard costs $0.126 per second with audio on (the default) and $0.084 per second with audio off.

| Video length | With audio (default) | Audio off |
|---|---|---|
| 5 s | $0.63 | $0.42 |
| **10 s (default, 3 shots)** | **$1.26** | $0.84 |
| 15 s | $1.89 | $1.26 |

You pay for the total seconds, however many shots they are split into. fal lists the crop utility at $0 per compute second. The OpenAI step adds a few cents. If you cancel a job that is already rendering, fal may still bill it.

## Customize

Every setting is in **Configure Video Settings**:

- `video_model`. The default is `fal-ai/kling-video/v3/standard/image-to-video`. To use Kling 3.0 Pro, set it to `fal-ai/kling-video/v3/pro/image-to-video` and update the prices. The sticky note **Switching to Kling 4.0 later** covers the v4 endpoint.
- `video_seconds` (3 to 15) and `shot_count` (1 to 3). The seconds are split across the shots.
- `generate_audio`, `price_per_second_usd` and `price_per_second_no_audio_usd`.
- `shot_1_prompt`, `shot_2_prompt` and `shot_3_prompt`. These are template shots, and `{dish}` is replaced by the dish name.
- `prompt_guardrails`, which is added to every shot, plus `negative_prompt` and `cfg_scale`.
- `use_openai`, `caption_language`, `caption_tone` and `extra_hashtags`.
- `ai_label_line` and `business_footer`, which are added to every caption. Keep the AI line.
- `crop_to_vertical`, `poll_every_seconds`, `timeout_minutes`, `max_file_mb` and `duration_tolerance_seconds`.

## Good practice

- The video is an AI illustration made from your real photo, not footage. Keep the AI line in the caption, leave Instagram's AI label on, and turn on TikTok's "AI-generated content" label before you publish the draft. The node cannot set that label on inbox drafts.
- The prompts tell Kling to keep the dish exactly as photographed, with no extra toppings, bigger portions or new ingredients. Watch the clip next to the real dish anyway. If it looks better than what you actually serve, don't post it.
- Captions only use the facts you type into the form. There are no invented ingredients, allergens, diet claims or prices, and no reviews, ratings or testimonials.
- No people appear. The prompts and the negative prompt exclude people, hands and faces. Upload photos of food, not of staff or guests.
- The optional networks are disabled, so a default run only creates a TikTok draft. Once you enable them, they publish directly when the run finishes.

## Community node

This workflow uses the SocialRobot community node (`@socialrobot-io/n8n-nodes-socialrobot`). Community nodes are not maintained by n8n, and you install them at your own risk. The node is used for the TikTok draft and the optional Instagram, Facebook and Threads posts.
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
    # Curated gallery descriptions for the Kling 3.0 templates (approved in the n8n gallery 2026-10-23)
    if wf.get("name") == "Turn listing photos into AI real estate walkthrough Reels and TikToks with Kling 3.0 and SocialRobot":
        return REALESTATE_WALKTHROUGH_MD.strip()
    if wf.get("name") == "Turn café and bakery dish photos into ASMR AI food videos with Kling 3.0 and SocialRobot":
        return FOOD_ASMR_VIDEO_MD.strip()
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
