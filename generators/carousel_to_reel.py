#!/usr/bin/env python3
"""
Generator for the n8n template:
  Convert Instagram carousels to Reels and TikTok slideshow videos with ffmpeg and SocialRobot

Notes:
- Writes the workflow JSON to workflows/convert-instagram-carousels-to-reels-and-tiktok-slideshow-videos-with-ffmpeg-and-socialrobot.json
- Does not delete or modify any other files in this repository.
- Reconstructs the workflow programmatically; UUIDs are generated fresh each run (node ids, etc.).
"""
import json
import os
import uuid


def generate_uuid() -> str:
    return str(uuid.uuid4())


def make_node(name: str, node_type: str, type_version, position, parameters, **extra):
    node = {
        "parameters": parameters,
        "id": generate_uuid(),
        "name": name,
        "type": node_type,
        "typeVersion": type_version,
        "position": position,
    }
    node.update(extra)
    return node


def link(connections, source: str, target: str, output_index: int = 0, input_index: int = 0):
    main = connections.setdefault(source, {"main": []})["main"]
    while len(main) <= output_index:
        main.append([])
    main[output_index].append({"node": target, "type": "main", "index": input_index})


BOOL_CONDITION = {"rightValue": "", "operator": {"type": "boolean", "operation": "true", "singleValue": True}}


def boolean_if_parameters(left_expression: str):
    return {
        "conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [dict(id=generate_uuid(), leftValue=left_expression, **BOOL_CONDITION)],
            "combinator": "and",
        },
        "options": {},
    }


BUILD_FFMPEG_JS = """// Builds one ffmpeg command: zoompan per slide, xfade between slides, optional music.
const s = $('Set Video Render Settings').first().json;
const slides = $('Arrange Slides').all().map(i => i.json);
const music = String($('When Carousel Submitted').first().json['Music URL'] || '').trim();
const W = Number(s.width), H = Number(s.height), FPS = Number(s.fps);
const D = Number(s.seconds_per_slide), T = Number(s.crossfade_seconds);
const L = D + T; // each clip overlaps the next by T seconds
const F = Math.round(L * FPS);
const q = p => "'" + String(p).replace(/'/g, "'\\\\''") + "'";
const motions = String(s.motions).split(',').map(m => m.trim()).filter(Boolean);
const Z = Number(s.zoom_amount);
const zp = {
  zoomIn:   `z='1+${Z}*on/${F}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`,
  zoomOut:  `z='1+${Z}-${Z}*on/${F}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`,
  panLeft:  `z='1+${Z}':x='(iw-iw/zoom)*(1-on/${F})':y='ih/2-(ih/zoom/2)'`,
  panRight: `z='1+${Z}':x='(iw-iw/zoom)*on/${F}':y='ih/2-(ih/zoom/2)'`,
  panUp:    `z='1+${Z}':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/${F})'`,
};
const inputs = slides.map(sl => `-i ${q(sl.path)}`);
const filters = slides.map((sl, i) => {
  const m = zp[motions[i % motions.length]] || zp.zoomIn;
  // Blurred cover background + fitted slide, so square and 4:5 slides fill 9:16 without cropping text.
  return `[${i}:v]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},boxblur=30:5,setsar=1[bg${i}];` +
    `[${i}:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,setsar=1[fg${i}];` +
    `[bg${i}][fg${i}]overlay=(W-w)/2:(H-h)/2,scale=${W * 2}:${H * 2},` +
    `zoompan=${m}:d=${F}:s=${W}x${H}:fps=${FPS},format=yuv420p,setsar=1[v${i}]`;
});
let last = 'v0';
for (let i = 1; i < slides.length; i++) {
  const out = i === slides.length - 1 ? 'vout' : `x${i}`;
  const offset = Math.round(i * (L - T) * 1000) / 1000;
  filters.push(`[${last}][v${i}]xfade=transition=${s.transition}:duration=${T}:offset=${offset}[${out}]`);
  last = out;
}
if (slides.length === 1) filters.push('[v0]null[vout]');
const total = Math.round((slides.length * (L - T) + T) * 100) / 100;
let audioIn = '', audioMap = '';
if (/^https?:\\/\\/[^\\s'"]+$/.test(music)) {
  audioIn = `-stream_loop -1 -i ${q(music)}`;
  filters.push(`[${slides.length}:a]atrim=0:${total},afade=t=out:st=${Math.max(0, total - 1.5)}:d=1.5[aout]`);
  audioMap = '-map "[aout]" -c:a aac -b:a 160k';
}
const dir = s.temp_dir;
const outFile = `${dir}/reel.mp4`;
const cmd = [
  'ffmpeg -y -hide_banner -loglevel error',
  inputs.join(' '), audioIn,
  `-filter_complex ${q(filters.join(';'))}`,
  '-map "[vout]"', audioMap,
  `-t ${total} -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -r ${FPS} -movflags +faststart`,
  q(outFile),
].filter(Boolean).join(' ');
const command = `${cmd} 2> ${q(dir + '/ffmpeg.log')} && echo RENDER_OK || { echo RENDER_FAILED; tail -c 1500 ${q(dir + '/ffmpeg.log')}; }`;
return [{ json: { command, output_file: outFile, expected_seconds: total, slides: slides.length } }];
"""

CHECK_SIZE_JS = """// Checks the file before it goes to SocialRobot. Duration comes from the MP4 header (mvhd box).
const s = $('Set Video Render Settings').first().json;
const item = $input.first();
const video = item.binary && item.binary.data;
const problems = [];
let sizeMb = 0;
let seconds = null;
if (!video) {
  problems.push('No video file was downloaded.');
} else {
  const buf = await this.helpers.getBinaryDataBuffer(0, 'data');
  sizeMb = buf.length / 1048576;
  const i = buf.indexOf('mvhd');
  if (i > 3) {
    const v1 = buf[i + 4] === 1;
    const scale = buf.readUInt32BE(i + (v1 ? 24 : 16));
    const units = v1 ? Number(buf.readBigUInt64BE(i + 28)) : buf.readUInt32BE(i + 20);
    if (scale) seconds = Math.round((units / scale) * 10) / 10;
  }
  if (sizeMb > Number(s.max_file_mb)) problems.push(`File is ${sizeMb.toFixed(1)} MB, above the ${s.max_file_mb} MB limit.`);
  if (seconds === null) problems.push('Could not read the video duration.');
  else if (seconds < Number(s.min_seconds) || seconds > Number(s.max_seconds)) problems.push(`Video is ${seconds} s; allowed is ${s.min_seconds}-${s.max_seconds} s.`);
}
return [{ json: { ok: problems.length === 0, problems, size_mb: Math.round(sizeMb * 100) / 100, duration_seconds: seconds }, binary: item.binary }];
"""

DESCRIBE_FAILURE_JS = """// One readable reason for whatever went wrong. Add an error workflow in the settings to get alerts.
const j = $json;
const s = $('Set Video Render Settings').first().json;
const out = String(j.stdout || '');
let message;
if (out.includes('FFMPEG_MISSING')) {
  message = 'ffmpeg is not installed on this n8n server. Install it (see the yellow \"Install ffmpeg\" note) and run again.';
} else if (out.includes('RENDER_FAILED')) {
  message = `ffmpeg could not render the Reel: ${out.replace('RENDER_FAILED', '').trim().slice(-800) || 'no log'}`;
} else if (Array.isArray(j.problems) && j.problems.length) {
  message = `The video did not pass the checks: ${j.problems.join(' ')}`;
} else if (j.error) {
  const e = typeof j.error === 'string' ? j.error : (j.error.message || JSON.stringify(j.error));
  message = $('Draft TikTok Video').isExecuted
    ? `SocialRobot could not save the TikTok draft: ${e}`
    : `File or command step failed (check temp_dir "${s.temp_dir}" and file access settings): ${e}`;
} else if (!$('Initialize Temp Folder').isExecuted) {
  message = `Upload ${s.min_slides}-${s.max_slides} slide images (JPG, PNG or WebP). The form had a different number.`;
} else {
  message = `Unexpected failure: ${JSON.stringify(j).slice(0, 500)}`;
}
return [{ json: { message } }];
"""


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "workflows")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(
        out_dir,
        "convert-instagram-carousels-to-reels-and-tiktok-slideshow-videos-with-ffmpeg-and-socialrobot.json",
    )

    nodes = []
    connections = {}

    # Sticky notes (match n8n-submitted names and content)
    nodes.append(make_node("Sticky Note", "n8n-nodes-base.stickyNote", 1, [-48, 224], {
        "content": "## Convert Instagram carousels to Reels and TikTok slideshow videos with ffmpeg and SocialRobot\n\nUpload 2-10 carousel slides and get a 1080x1920 Reel with pan-and-zoom on each slide, crossfades and optional music. It renders on your own n8n server with ffmpeg, so there are no render fees. SocialRobot sends the video to your TikTok inbox as a draft and can also post it as an Instagram Reel, a Facebook Reel or a Threads video.\n\n### How it works\n1. **When Carousel Submitted** takes 2-10 slides (in carousel order), a caption, the seconds per slide and an optional music URL.\n2. The workflow checks that ffmpeg is installed and the slide count is right, then writes the slides to a temporary folder.\n3. ffmpeg places each slide on a blurred 9:16 background (so square and 4:5 slides keep their text), adds a zoom or pan, crossfades between slides and mixes in the music.\n4. The MP4 is read back, size and duration are checked, then SocialRobot sends it to your TikTok inbox as a draft.\n5. Optional: the original slides also go to TikTok as a photo slideshow draft.\n6. Temp files are deleted at the end, and on errors too.\n\n### Setup steps\n- [ ] **Self-hosted n8n with ffmpeg installed** and the Execute Command node enabled (see the yellow note)\n- [ ] SocialRobot community node 3.1.1+ (npm latest 3.1.2) and your SocialRobot API key\n- [ ] Connect TikTok in SocialRobot and pick the account in **Draft TikTok Video** (and **Draft TikTok Slideshow** if you use it)\n- [ ] Check `temp_dir` in **Set Video Render Settings**: it must be a folder n8n is allowed to write to and delete from\n\n### Customization\n- Change slide length, crossfade, transition, motions, zoom, size and video limits in **Set Video Render Settings**.\n- Enable **Draft Instagram Reel**, **Draft Facebook Reel** or **Draft Threads Video** (disabled by default) and pick accounts.\n- SocialRobot does not publish to YouTube.\n\nCost per run: $0. ffmpeg runs on your own server and no AI model is used.",
        "width": 480, "height": 1000
    }))
    nodes.append(make_node("Sticky Note1", "n8n-nodes-base.stickyNote", 1, [512, 240], {
        "content": "## Collect render request\n\nStarts from the upload form. **Set Video Render Settings** holds every value you'd want to tweak: pacing, crossfade, motions, zoom, size and limits.",
        "width": 384, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note2", "n8n-nodes-base.stickyNote", 1, [928, 240], {
        "content": "## Preflight validation checks\n\n**Verify ffmpeg Installation** stops the run with a clear message if ffmpeg is missing. **Check Slide Count** makes sure there are 2-10 images before any files are created.",
        "width": 576, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note3", "n8n-nodes-base.stickyNote", 1, [1536, 240], {
        "content": "## Stage carousel slides\n\nCreates a temp folder named after the execution ID and writes each slide to disk in carousel order.",
        "width": 576, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note4", "n8n-nodes-base.stickyNote", 1, [2144, 272], {
        "content": "## Render reel video\n\n**Compose ffmpeg Command** builds one zoompan + xfade filter graph on a blurred 9:16 background. The music link is used only if it's a plain http(s) URL. ffmpeg's error log is kept for the error message.",
        "width": 576, "height": 304, "color": 7
    }))
    nodes.append(make_node("Sticky Note5", "n8n-nodes-base.stickyNote", 1, [2752, 240], {
        "content": "## Validate rendered output\n\nReads `reel.mp4` back and checks file size and real duration (from the MP4 header) before anything goes to SocialRobot.",
        "width": 576, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note6", "n8n-nodes-base.stickyNote", 1, [3392, 240], {
        "content": "## Save TikTok draft\n\n**Draft TikTok Video** uses Post Mode *Send to Inbox (Draft)*: nothing goes public until you post it in the TikTok app.",
        "width": 432, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note7", "n8n-nodes-base.stickyNote", 1, [3856, 224], {
        "content": "## Clean successful render\n\nRemoves temporary files after the main TikTok draft path has completed successfully.",
        "width": 240, "height": 336, "color": 7
    }))
    nodes.append(make_node("Sticky Note8", "n8n-nodes-base.stickyNote", 1, [3632, 592], {
        "content": "## Create photo slideshow\n\nIf you answer Yes on the form, the original slides also go to TikTok as a photo slideshow draft (1-35 images). SocialRobot hosts the files itself, so no public image URLs are needed.",
        "width": 640, "height": 320, "color": 7
    }))
    nodes.append(make_node("Sticky Note9", "n8n-nodes-base.stickyNote", 1, [3360, 592], {
        "content": "## Optional social drafts\n\nConnected and **disabled by default**. Enable the ones you want and pick an account in each.",
        "width": 240, "height": 752, "color": 7
    }))
    nodes.append(make_node("Sticky Note10", "n8n-nodes-base.stickyNote", 1, [1792, 832], {
        "content": "## Handle render failures\n\nMissing ffmpeg, a wrong slide count, ffmpeg errors, files that fail the checks and SocialRobot errors end here. The temp folder is deleted, then the run stops with one readable message. Add an error workflow in the settings to get alerts.",
        "width": 672, "height": 304, "color": 7
    }))
    nodes.append(make_node("Sticky Note11", "n8n-nodes-base.stickyNote", 1, [-48, 1248], {
        "content": "## Install ffmpeg (self-hosted only)\nn8n Cloud can't run this template: it has no Execute Command node and no ffmpeg.\n\n**Docker:** build a small image on top of n8n:\n```\nFROM docker.n8n.io/n8nio/n8n:latest\nUSER root\nRUN apk add --no-cache ffmpeg\nUSER node\n```\nThen `docker build -t n8n-ffmpeg .` and run `n8n-ffmpeg` instead of the stock image. On Debian/Ubuntu installs use `sudo apt install ffmpeg`.\n\n**n8n 2.x:** Execute Command is turned off by default. Enable it with `NODES_EXCLUDE=[]`. Read/Write Files only works inside `N8N_RESTRICT_FILE_ACCESS_TO` (default `~/.n8n-files`), so keep `temp_dir` in there.",
        "width": 480, "height": 560, "color": 6
    }))
    nodes.append(make_node("Sticky Note12", "n8n-nodes-base.stickyNote", 1, [4304, 224], {
        "content": "## AI label\nPan-and-zoom isn't generative AI, so the label is off. If your slides were made with AI, turn on **AI-Generated Content** in **Draft Instagram Reel** and the 'AI-generated content' label in TikTok before posting. The node doesn't send TikTok's AI label for inbox drafts.",
        "width": 320, "height": 330, "color": 3
    }))

    # Form trigger
    form_trigger = make_node(
        "When Carousel Submitted",
        "n8n-nodes-base.formTrigger",
        2.3,
        [560, 400],
        {
            "formTitle": "Convert a carousel to a Reel",
            "formDescription": "Upload 2-10 carousel slides in order. You get a vertical pan-and-zoom video in your TikTok inbox as a draft.",
            "formFields": {
                "values": [
                    {"fieldLabel": "Carousel Slides", "fieldType": "file", "multipleFiles": True, "acceptFileTypes": ".jpg, .jpeg, .png, .webp", "requiredField": True},
                    {"fieldLabel": "Caption", "fieldType": "textarea", "placeholder": "Caption with #hashtags", "requiredField": True},
                    {"fieldLabel": "Seconds per Slide", "fieldType": "number", "placeholder": "2.5 (1.5 to 6)"},
                    {"fieldLabel": "Music URL", "placeholder": "Optional public MP3 link you have the rights to use"},
                    {
                        "fieldLabel": "Also Send TikTok Photo Slideshow",
                        "fieldType": "dropdown",
                        "fieldOptions": {"values": [{"option": "No"}, {"option": "Yes"}]},
                        "requiredField": True,
                    },
                    {"fieldLabel": "Slideshow Title", "placeholder": "Optional, up to 90 characters (photo slideshow only)"},
                ]
            },
            "responseMode": "onReceived",
            "options": {"respondWithOptions": {"values": {"respondWith": "text", "formSubmittedText": "Thanks! Your Reel is rendering. It shows up in your TikTok inbox in a minute or two."}}},
        },
        webhookId=generate_uuid(),
    )
    nodes.append(form_trigger)

    # Render settings
    def assignment(name, typ, value):
        return {"id": generate_uuid(), "name": name, "type": typ, "value": value}

    set_settings = make_node(
        "Set Video Render Settings",
        "n8n-nodes-base.set",
        3.4,
        [752, 400],
        {
            "assignments": {
                "assignments": [
                    assignment("temp_dir", "string", "=/home/node/.n8n-files/carousel-to-reel/{{ $execution.id }}"),
                    assignment("seconds_per_slide", "number", "={{ Math.min(6, Math.max(1.5, Number($('When Carousel Submitted').first().json['Seconds per Slide']) || 2.5)) }}"),
                    assignment("crossfade_seconds", "number", 0.5),
                    assignment("transition", "string", "fade"),
                    assignment("motions", "string", "zoomIn,panLeft,zoomOut,panRight,panUp"),
                    assignment("zoom_amount", "number", 0.12),
                    assignment("width", "number", 1080),
                    assignment("height", "number", 1920),
                    assignment("fps", "number", 30),
                    assignment("min_slides", "number", 2),
                    assignment("max_slides", "number", 10),
                    assignment("max_file_mb", "number", 250),
                    assignment("min_seconds", "number", 3),
                    assignment("max_seconds", "number", 90),
                ]
            },
            "options": {},
        },
    )
    nodes.append(set_settings)
    link(connections, form_trigger["name"], set_settings["name"])

    # ffmpeg check
    check_ffmpeg = make_node(
        "Verify ffmpeg Installation",
        "n8n-nodes-base.executeCommand",
        1,
        [976, 400],
        {"executeOnce": True, "command": "command -v ffmpeg >/dev/null 2>&1 && ffmpeg -hide_banner -version | head -n 1 || echo FFMPEG_MISSING"},
    )
    nodes.append(check_ffmpeg)
    link(connections, set_settings["name"], check_ffmpeg["name"])

    ffmpeg_found = make_node("If ffmpeg Available", "n8n-nodes-base.if", 2.2, [1168, 400], boolean_if_parameters("={{ String($json.stdout || '').startsWith('ffmpeg version') }}"))
    nodes.append(ffmpeg_found)
    link(connections, check_ffmpeg["name"], ffmpeg_found["name"])

    has_slides = make_node(
        "Check Slide Count",
        "n8n-nodes-base.if",
        2.2,
        [1360, 400],
        boolean_if_parameters(
            "= {{ (n => n >= $('Set Video Render Settings').first().json.min_slides && n <= $('Set Video Render Settings').first().json.max_slides)(Object.values($('When Carousel Submitted').first().binary || {}).filter(b => String(b.mimeType || '').startsWith('image/')).length) }}"
        ),
    )
    # Note: keep original expression string formatting (no spaces before '=')
    has_slides["parameters"]["conditions"]["conditions"][0]["leftValue"] = "={{ (n => n >= $('Set Video Render Settings').first().json.min_slides && n <= $('Set Video Render Settings').first().json.max_slides)(Object.values($('When Carousel Submitted').first().binary || {}).filter(b => String(b.mimeType || '').startsWith('image/')).length) }}"
    nodes.append(has_slides)
    link(connections, ffmpeg_found["name"], has_slides["name"], 0)

    describe_failure = make_node("Explain Process Error", "n8n-nodes-base.code", 2, [1840, 960], {"jsCode": DESCRIBE_FAILURE_JS})
    nodes.append(describe_failure)
    link(connections, ffmpeg_found["name"], describe_failure["name"], 1)

    create_temp = make_node(
        "Initialize Temp Folder",
        "n8n-nodes-base.executeCommand",
        1,
        [1584, 400],
        {"executeOnce": True, "command": "=mkdir -p '{{ $('Set Video Render Settings').first().json.temp_dir }}' && echo OK"},
        onError="continueErrorOutput",
    )
    nodes.append(create_temp)
    link(connections, has_slides["name"], create_temp["name"], 0)
    link(connections, has_slides["name"], describe_failure["name"], 1)

    prepare_slides = make_node(
        "Arrange Slides",
        "n8n-nodes-base.code",
        2,
        [1776, 400],
        {
            "jsCode": "// One item per slide, in upload order, with the path it gets in the temp folder.\nconst s = $('Set Video Render Settings').first().json;\nconst form = $('When Carousel Submitted').first();\nconst slides = Object.values(form.binary || {}).filter(b => String(b.mimeType || '').startsWith('image/'));\nconst ext = b => ({ 'image/png': 'png', 'image/webp': 'webp' }[b.mimeType] || 'jpg');\nreturn slides.map((image, i) => {\n  const name = `slide_${String(i + 1).padStart(2, '0')}.${ext(image)}`;\n  return { json: { slide: i + 1, path: `${s.temp_dir}/${name}` }, binary: { image } };\n});"
        },
    )
    nodes.append(prepare_slides)
    link(connections, create_temp["name"], prepare_slides["name"], 0)
    link(connections, create_temp["name"], describe_failure["name"], 1)

    write_slide = make_node(
        "Save Slide to Disk",
        "n8n-nodes-base.readWriteFile",
        1,
        [1968, 400],
        {"operation": "write", "fileName": "={{ $json.path }}", "dataPropertyName": "image", "options": {}},
        onError="continueErrorOutput",
    )
    nodes.append(write_slide)
    link(connections, prepare_slides["name"], write_slide["name"])

    build_ffmpeg = make_node("Compose ffmpeg Command", "n8n-nodes-base.code", 2, [2192, 400], {"jsCode": BUILD_FFMPEG_JS})
    nodes.append(build_ffmpeg)
    link(connections, write_slide["name"], build_ffmpeg["name"], 0)
    link(connections, write_slide["name"], describe_failure["name"], 1)

    render_cmd = make_node(
        "Execute ffmpeg Render",
        "n8n-nodes-base.executeCommand",
        1,
        [2384, 400],
        {"executeOnce": True, "command": "={{ $json.command }}"},
        onError="continueErrorOutput",
    )
    nodes.append(render_cmd)
    link(connections, build_ffmpeg["name"], render_cmd["name"])

    render_ok = make_node("If Render Successful", "n8n-nodes-base.if", 2.2, [2576, 400], boolean_if_parameters("={{ String($json.stdout || '').includes('RENDER_OK') }}"))
    nodes.append(render_ok)
    link(connections, render_cmd["name"], render_ok["name"], 0)
    link(connections, render_cmd["name"], describe_failure["name"], 1)

    read_video = make_node(
        "Load Reel from Disk",
        "n8n-nodes-base.readWriteFile",
        1,
        [2800, 400],
        {"operation": "read", "fileSelector": "={{ $('Compose ffmpeg Command').first().json.output_file }}", "options": {"dataPropertyName": "data"}},
        onError="continueErrorOutput",
    )
    nodes.append(read_video)
    link(connections, render_ok["name"], read_video["name"], 0)
    link(connections, render_ok["name"], describe_failure["name"], 1)

    check_size = make_node("Validate Size and Duration", "n8n-nodes-base.code", 2, [2992, 400], {"jsCode": CHECK_SIZE_JS})
    nodes.append(check_size)
    link(connections, read_video["name"], check_size["name"], 0)
    link(connections, read_video["name"], describe_failure["name"], 1)

    passes = make_node("If Video Verified", "n8n-nodes-base.if", 2.2, [3184, 400], boolean_if_parameters("={{ $json.ok }}"))
    nodes.append(passes)
    link(connections, check_size["name"], passes["name"])

    # Publish actions
    account_resolver = {"__rl": True, "mode": "list", "value": ""}
    caption_expr = "={{ $('Carousel Form').first().json.Caption }}"
    video_binary = [{"mediaSource": "binary", "binaryPropertyName": "data", "mediaType": "VIDEO"}]

    publish_tiktok_video = make_node(
        "Draft TikTok Video",
        "@socialrobot-io/n8n-nodes-socialrobot.socialRobot",
        1,
        [3440, 400],
        {
            "resource": "tiktok",
            "operation": "create",
            "accountId": account_resolver,
            "caption": caption_expr,
            "medias": video_binary,
            "postMode": "UPLOAD",
            "publishMode": "NOW",
        },
        onError="continueErrorOutput",
    )
    nodes.append(publish_tiktok_video)
    link(connections, passes["name"], publish_tiktok_video["name"], 0)
    link(connections, passes["name"], describe_failure["name"], 1)

    summarize = make_node(
        "Summarize Video Results",
        "n8n-nodes-base.set",
        3.4,
        [3680, 400],
        {
            "assignments": {
                "assignments": [
                    {"id": generate_uuid(), "name": "tiktok_post_id", "type": "string", "value": "={{ $json.id }}"},
                    {"id": generate_uuid(), "name": "status", "type": "string", "value": "={{ $json.status }}"},
                    {"id": generate_uuid(), "name": "slides", "type": "number", "value": "={{ $('Compose ffmpeg Command').first().json.slides }}"},
                    {"id": generate_uuid(), "name": "duration_seconds", "type": "number", "value": "={{ $('Validate Size and Duration').first().json.duration_seconds }}"},
                    {"id": generate_uuid(), "name": "size_mb", "type": "number", "value": "={{ $('Validate Size and Duration').first().json.size_mb }}"},
                    {
                        "id": generate_uuid(),
                        "name": "next_step",
                        "type": "string",
                        "value": "Open the TikTok inbox notification, add sound if you like, then post.",
                    },
                ]
            },
            "options": {},
        },
    )
    nodes.append(summarize)
    link(connections, publish_tiktok_video["name"], summarize["name"], 0)
    link(connections, publish_tiktok_video["name"], describe_failure["name"], 1)

    clean_success = make_node(
        "Remove Temp Files",
        "n8n-nodes-base.executeCommand",
        1,
        [3900, 400],
        {"executeOnce": True, "command": "=rm -rf -- '{{ $('Set Video Render Settings').first().json.temp_dir }}' && echo CLEANED"},
        onError="continueRegularOutput",
    )
    nodes.append(clean_success)
    link(connections, summarize["name"], clean_success["name"])

    wants_slideshow = make_node(
        "If Slideshow Required",
        "n8n-nodes-base.if",
        2.2,
        [3680, 752],
        boolean_if_parameters("={{ $('When Carousel Submitted').first().json['Also Send TikTok Photo Slideshow'] === 'Yes' }}"),
    )
    nodes.append(wants_slideshow)
    link(connections, summarize["name"], wants_slideshow["name"])

    gather_slides = make_node(
        "Collect Slides for Slideshow",
        "n8n-nodes-base.code",
        2,
        [3904, 752],
        {
            "jsCode": "// One item with every slide as its own binary field (slide_1, slide_2, ...).\n// The SocialRobot node uploads binary media to SocialRobot storage itself, so no public URLs are needed.\nconst slides = $('Arrange Slides').all().slice(0, 35);\nconst binary = {};\nslides.forEach((item, i) => { binary[`slide_${i + 1}`] = item.binary.image; });\nreturn [{ json: { slide_fields: slides.map((_, i) => `slide_${i + 1}`) }, binary }];"
        },
    )
    nodes.append(gather_slides)
    link(connections, wants_slideshow["name"], gather_slides["name"], 0)

    publish_tiktok_slideshow = make_node(
        "Draft TikTok Slideshow",
        "@socialrobot-io/n8n-nodes-socialrobot.socialRobot",
        1,
        [4128, 752],
        {
            "resource": "tiktok",
            "operation": "create",
            "accountId": account_resolver,
            "caption": caption_expr,
            "medias": "={{ $json.slide_fields.map(name => ({ mediaSource: 'binary', binaryPropertyName: name, mediaType: 'IMAGE' })) }}",
            "postMode": "UPLOAD",
            "title": "={{ String($('When Carousel Submitted').first().json['Slideshow Title'] || '').slice(0, 90) }}",
            "publishMode": "NOW",
        },
        onError="continueRegularOutput",
    )
    nodes.append(publish_tiktok_slideshow)
    link(connections, gather_slides["name"], publish_tiktok_slideshow["name"])

    optional_ig = make_node(
        "Draft Instagram Reel",
        "@socialrobot-io/n8n-nodes-socialrobot.socialRobot",
        1,
        [3408, 816],
        {
            "resource": "instagram",
            "operation": "create",
            "accountId": account_resolver,
            "caption": caption_expr,
            "mediaSource": "binary",
            "mediaType": "VIDEO",
            "binaryPropertyName": "data",
            "isAiGenerated": False,
            "isReel": True,
            "publishMode": "NOW",
        },
        disabled=True,
        onError="continueRegularOutput",
    )
    nodes.append(optional_ig)
    link(connections, passes["name"], optional_ig["name"], 0)

    optional_fb = make_node(
        "Draft Facebook Reel",
        "@socialrobot-io/n8n-nodes-socialrobot.socialRobot",
        1,
        [3408, 992],
        {
            "resource": "facebook",
            "operation": "create",
            "accountId": account_resolver,
            "caption": caption_expr,
            "medias": video_binary,
            "isReel": True,
            "publishMode": "NOW",
        },
        disabled=True,
        onError="continueRegularOutput",
    )
    nodes.append(optional_fb)
    link(connections, passes["name"], optional_fb["name"], 0)

    optional_threads = make_node(
        "Draft Threads Video",
        "@socialrobot-io/n8n-nodes-socialrobot.socialRobot",
        1,
        [3408, 1184],
        {
            "resource": "threads",
            "operation": "create",
            "accountId": account_resolver,
            "caption": caption_expr,
            "medias": video_binary,
            "publishMode": "NOW",
        },
        disabled=True,
        onError="continueRegularOutput",
    )
    nodes.append(optional_threads)
    link(connections, passes["name"], optional_threads["name"], 0)

    # Error cleanup path
    clean_error = make_node(
        "Handle Error Cleanup",
        "n8n-nodes-base.executeCommand",
        1,
        [2080, 960],
        {"executeOnce": True, "command": "=rm -rf -- '{{ $('Set Video Render Settings').first().json.temp_dir }}' && echo CLEANED"},
        onError="continueRegularOutput",
    )
    nodes.append(clean_error)
    link(connections, describe_failure["name"], clean_error["name"])

    stop_with_error = make_node(
        "Terminate on Error",
        "n8n-nodes-base.stopAndError",
        1,
        [2320, 960],
        {"errorMessage": "={{ $('Explain Process Error').first().json.message }}"},
    )
    nodes.append(stop_with_error)
    link(connections, clean_error["name"], stop_with_error["name"])

    # Build final workflow dict
    workflow = {
        "name": "Convert Instagram carousels to Reels and TikTok slideshow videos with ffmpeg and SocialRobot",
        "nodes": nodes,
        "connections": connections,
        "pinData": {},
        "settings": {"executionOrder": "v1"},
        "meta": {"templateCredsSetupCompleted": False},
        "tags": [{"name": n} for n in ["SocialRobot", "Instagram Reels", "Carousel", "TikTok", "Slideshow", "ffmpeg", "Video", "Facebook Reels"]],
    }

    with open(out_path, "w") as f:
        json.dump(workflow, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

