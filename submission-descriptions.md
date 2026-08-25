# n8n.io submission descriptions

Paste each description into the n8n.io template submission form. Each is about
150 to 200 words and covers Who's it for, How it works, How to set up,
Requirements, and How to customize.

## Auto-post blog posts to X, LinkedIn, and Facebook

This workflow publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. It's for publishers and bloggers who want new content shared to social media automatically. It removes the manual work of copying new articles into social posts.

**How it works**
1. Runs automatically every day.
2. Fetches the latest items from the configured RSS feed.
3. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Set the RSS feed URL to your own feed.
3. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public RSS feed URL.

**How to customize**
Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (X (Twitter), LinkedIn, Facebook) and edit each node's caption and media fields to fit your brand voice.

---

## Auto-post RSS feed items to Bluesky and Mastodon

This workflow publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. It's for publishers and bloggers who want new content shared to social media automatically. It removes the manual work of copying new articles into social posts.

**How it works**
1. Runs automatically every hour.
2. Fetches the latest items from the configured RSS feed.
3. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Set the RSS feed URL to your own feed.
3. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public RSS feed URL.

**How to customize**
Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (Bluesky, Mastodon) and edit each node's caption and media fields to fit your brand voice.

---

## Auto-post RSS feed items to every social media platform

This workflow publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. It's for publishers and bloggers who want new content shared to social media automatically. It removes the manual work of copying new articles into social posts.

**How it works**
1. Runs automatically every 6 hours.
2. Fetches the latest items from the configured RSS feed.
3. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Set the RSS feed URL to your own feed.
3. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public RSS feed URL.

**How to customize**
Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (X (Twitter), Bluesky, Mastodon, Threads, LinkedIn, Facebook) and edit each node's caption and media fields to fit your brand voice.

---

## Auto-post RSS items to Bluesky, Mastodon, and Threads with AI summaries

This workflow publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. It's for publishers and bloggers who want new content shared to social media automatically. It removes the manual work of copying new articles into social posts.

**How it works**
1. Runs automatically every hour.
2. Fetches the latest items from the configured RSS feed.
3. Generates platform-optimized post text with the OpenAI model.
4. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Set the RSS feed URL to your own feed.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public RSS feed URL.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (Bluesky, Mastodon, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Create AI post drafts for review before publishing

This workflow saves a draft post to Instagram in SocialRobot for review. Saves a draft post to X (Twitter) in SocialRobot for review. Saves a draft post to LinkedIn in SocialRobot for review. Saves a draft post to TikTok in SocialRobot for review. Saves a draft post to Facebook in SocialRobot for review. Saves a draft post to Pinterest in SocialRobot for review. Saves a draft post to Bluesky in SocialRobot for review. Saves a draft post to Mastodon in SocialRobot for review. Saves a draft post to Threads in SocialRobot for review. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs automatically every day.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Saves a draft post to Instagram in SocialRobot for review. Saves a draft post to X (Twitter) in SocialRobot for review. Saves a draft post to LinkedIn in SocialRobot for review. Saves a draft post to TikTok in SocialRobot for review. Saves a draft post to Facebook in SocialRobot for review. Saves a draft post to Pinterest in SocialRobot for review. Saves a draft post to Bluesky in SocialRobot for review. Saves a draft post to Mastodon in SocialRobot for review. Saves a draft post to Threads in SocialRobot for review.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.
5. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.
- A Pinterest board ID.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (Instagram, X (Twitter), LinkedIn, TikTok, Facebook, Pinterest, Bluesky, Mastodon, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Cross-post a post to every social media platform

This workflow publishes a post to Instagram via the SocialRobot API. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to TikTok via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. It's for marketers and creators who post to multiple social platforms and want to write once, publish everywhere. It removes the manual work of posting the same update to every platform separately.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Instagram via the SocialRobot API. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to TikTok via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.
3. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Instagram.
- A public image or video URL for X (Twitter).
- A public image or video URL for LinkedIn.
- A public image or video URL for TikTok.
- A public image or video URL for Facebook.
- A Pinterest board ID.
- A public image or video URL for Pinterest.
- A public image or video URL for Mastodon.
- A public image or video URL for Threads.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram, X (Twitter), LinkedIn, TikTok, Facebook, Pinterest, Bluesky, Mastodon, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Cross-post an image to Instagram, Pinterest, Facebook, and Threads

This workflow publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. It's for marketers and creators who post to multiple social platforms and want to write once, publish everywhere. It removes the manual work of posting the same update to every platform separately.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Select your connected account in each Publish node.
4. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Instagram.
- A Pinterest board ID.
- A public image or video URL for Pinterest.
- A public image or video URL for Facebook.
- A public image or video URL for Threads.

**How to customize**
Edit the text or image URL in the Set node to change what gets posted. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram, Pinterest, Facebook, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Cross-post text to X, Bluesky, Mastodon, Threads, and LinkedIn

This workflow publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. It's for marketers and creators who post to multiple social platforms and want to write once, publish everywhere. It removes the manual work of posting the same update to every platform separately.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Edit the text or image URL in the Set node to change what gets posted. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (X (Twitter), Bluesky, Mastodon, Threads, LinkedIn) and edit each node's caption and media fields to fit your brand voice.

---

## Delete a social media post

This workflow deletes a post by ID. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Deletes a post by ID.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Provide the Post ID, mapped from an upstream node or typed directly.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Map the Post ID from an upstream node, or feed the SocialRobot node from a workflow that produces post IDs.

---

## Download an image and post it to Instagram

This workflow publishes a post to Instagram via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Instagram. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Downloads the media file from a URL into binary data.
3. Publishes a post to Instagram via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Set the media URL in the Download node.
3. Select your connected account in each Publish node.
4. Make sure an upstream node provides the image as binary data (for example an HTTP Request node).

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An upstream node that provides the image as binary data (for example an HTTP Request node).

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram) and edit each node's caption and media fields to fit your brand voice.

---

## Generate AI captions and post to Instagram and Pinterest

This workflow publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.
5. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.
- A public image or video URL for Instagram.
- A Pinterest board ID.
- A public image or video URL for Pinterest.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram, Pinterest) and edit each node's caption and media fields to fit your brand voice.

---

## Generate AI captions and publish to every social media platform

This workflow publishes a post to Instagram via the SocialRobot API. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to TikTok via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Publishes a post to Instagram via the SocialRobot API. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to TikTok via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.
5. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.
- A public image or video URL for Instagram.
- A public image or video URL for X (Twitter).
- A public image or video URL for LinkedIn.
- A public image or video URL for TikTok.
- A public image or video URL for Facebook.
- A Pinterest board ID.
- A public image or video URL for Pinterest.
- A public image or video URL for Mastodon.
- A public image or video URL for Threads.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram, X (Twitter), LinkedIn, TikTok, Facebook, Pinterest, Bluesky, Mastodon, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Generate AI images with gpt-image-2 and post them to Instagram and Pinterest

This workflow publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Downloads the media file from a URL into binary data.
4. Generates platform-optimized post text with the OpenAI model.
5. Publishes a post to Instagram via the SocialRobot API. Publishes a post to Pinterest via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Set the media URL in the Download node.
4. Connect your OpenAI account in the OpenAI Chat Model node.
5. Select your connected account in each Publish node.
6. Make sure an upstream node provides the image as binary data (for example an HTTP Request node).
7. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.
- An upstream node that provides the image as binary data (for example an HTTP Request node).
- A Pinterest board ID.
- A public image or video URL for Pinterest.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram, Pinterest) and edit each node's caption and media fields to fit your brand voice.

---

## Generate AI videos with Seedance and post them to TikTok

This workflow publishes a post to TikTok via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Downloads the media file from a URL into binary data.
5. Downloads the media file from a URL into binary data.
6. Downloads the media file from a URL into binary data.
7. Publishes a post to TikTok via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Set the media URL in the Download node.
5. Set the media URL in the Download node.
6. Set the media URL in the Download node.
7. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.
- A public image or video URL for TikTok.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (TikTok) and edit each node's caption and media fields to fit your brand voice.

---

## Generate daily AI posts for Bluesky and Mastodon

This workflow publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs automatically every day.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (Bluesky, Mastodon) and edit each node's caption and media fields to fit your brand voice.

---

## Get a social media post by ID

This workflow fetches a single post by ID. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Fetches a single post by ID.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Provide the Post ID, mapped from an upstream node or typed directly.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Map the Post ID from an upstream node, or feed the SocialRobot node from a workflow that produces post IDs.

---

## List connected social media accounts

This workflow lists your connected SocialRobot accounts. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Lists your connected SocialRobot accounts.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Optionally set the status, platform, and date filters.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Adjust the status, platform, and date filters to list exactly the posts you need.

---

## List failed social media posts

This workflow lists posts from SocialRobot. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Lists posts from SocialRobot.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Optionally set the status, platform, and date filters.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Adjust the status, platform, and date filters to list exactly the posts you need.

---

## List scheduled social media posts

This workflow lists posts from SocialRobot. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Lists posts from SocialRobot.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Optionally set the status, platform, and date filters.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Adjust the status, platform, and date filters to list exactly the posts you need.

---

## Pin an image to Pinterest

This workflow publishes a post to Pinterest via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Pinterest. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Pinterest via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.
3. Set the Pinterest board ID in the Pinterest Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A Pinterest board ID.
- A public image or video URL for Pinterest.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Pinterest) and edit each node's caption and media fields to fit your brand voice.

---

## Post a video to Instagram

This workflow publishes a post to Instagram via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Instagram. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Instagram via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Instagram.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram) and edit each node's caption and media fields to fit your brand voice.

---

## Post a video to TikTok

This workflow publishes a post to TikTok via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to TikTok. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to TikTok via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for TikTok.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (TikTok) and edit each node's caption and media fields to fit your brand voice.

---

## Post an image to Instagram

This workflow publishes a post to Instagram via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Instagram. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Instagram via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Instagram.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Instagram) and edit each node's caption and media fields to fit your brand voice.

---

## Post text and an image to X (Twitter)

This workflow publishes a post to X (Twitter) via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to X (Twitter). It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to X (Twitter) via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for X (Twitter).

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (X (Twitter)) and edit each node's caption and media fields to fit your brand voice.

---

## Post text to Bluesky

This workflow publishes a post to Bluesky via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Bluesky. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Bluesky via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Bluesky) and edit each node's caption and media fields to fit your brand voice.

---

## Post text to X (Twitter)

This workflow publishes a post to X (Twitter) via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to X (Twitter). It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to X (Twitter) via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (X (Twitter)) and edit each node's caption and media fields to fit your brand voice.

---

## Post to a Facebook Page

This workflow publishes a post to Facebook via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Facebook. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Facebook via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Facebook.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Facebook) and edit each node's caption and media fields to fit your brand voice.

---

## Post to LinkedIn

This workflow publishes a post to LinkedIn via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to LinkedIn. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to LinkedIn via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (LinkedIn) and edit each node's caption and media fields to fit your brand voice.

---

## Post to Mastodon

This workflow publishes a post to Mastodon via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Mastodon. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Mastodon via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Mastodon.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Mastodon) and edit each node's caption and media fields to fit your brand voice.

---

## Post to Threads

This workflow publishes a post to Threads via the SocialRobot API. It's for anyone who wants a simple, repeatable way to post to Threads. It removes the manual work of logging in and posting by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A public image or video URL for Threads.

**How to customize**
Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Repurpose one piece of content into posts for every platform

This workflow publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API. It's for creators and marketers who want AI written posts published automatically. It removes the manual work of writing captions for every platform by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Sets the topic, text, or other inputs used to build the post.
3. Generates platform-optimized post text with the OpenAI model.
4. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to LinkedIn via the SocialRobot API. Publishes a post to Facebook via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. Publishes a post to Threads via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Edit the fields in the Set node to set your topic or text.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Switch the publish mode to Schedule to queue the post for a future date, or to Draft to review it first. Add or remove Publish nodes (X (Twitter), LinkedIn, Facebook, Bluesky, Mastodon, Threads) and edit each node's caption and media fields to fit your brand voice.

---

## Reschedule a social media post

This workflow reschedules a post to a new date. It's for teams that manage SocialRobot posts programmatically.

**How it works**
1. Runs when you click Execute Workflow.
2. Reschedules a post to a new date.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Provide the Post ID, mapped from an upstream node or typed directly.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Map the Post ID from an upstream node, or feed the SocialRobot node from a workflow that produces post IDs.

---

## Schedule a daily post to X, Bluesky, and Mastodon

This workflow publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API. It's for marketers and creators who post to multiple social platforms and want to write once, publish everywhere. It removes the manual work of posting the same update to every platform separately.

**How it works**
1. Runs automatically every day.
2. Publishes a post to X (Twitter) via the SocialRobot API. Publishes a post to Bluesky via the SocialRobot API. Publishes a post to Mastodon via the SocialRobot API.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Change the Schedule Trigger interval or switch to a cron expression to match your posting cadence. Add or remove Publish nodes (X (Twitter), Bluesky, Mastodon) and edit each node's caption and media fields to fit your brand voice.

---

## Schedule a social media post for a future date

This workflow schedules a post to X (Twitter) at the given date and time. Schedules a post to LinkedIn at the given date and time. It's for marketers and creators who post to multiple social platforms and want to write once, publish everywhere. It removes the manual work of posting the same update to every platform separately.

**How it works**
1. Runs when you click Execute Workflow.
2. Schedules a post to X (Twitter) at the given date and time. Schedules a post to LinkedIn at the given date and time.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Select your connected account in each Publish node.
3. Confirm the schedule date, or map it from an upstream field.
4. Confirm the schedule date, or map it from an upstream field.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.

**How to customize**
Change the schedule date, or map it from an upstream field like a spreadsheet column. Add or remove Publish nodes (X (Twitter), LinkedIn) and edit each node's caption and media fields to fit your brand voice.

---

## Schedule AI captions to social media from a Google Sheets calendar

This workflow schedules a post to X (Twitter) at the given date and time. Schedules a post to Bluesky at the given date and time. Schedules a post to Mastodon at the given date and time. Schedules a post to Threads at the given date and time. Schedules a post to LinkedIn at the given date and time. It's for social media teams that plan content in a spreadsheet and want it published on schedule. It removes the manual work of posting every spreadsheet row by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Reads the rows of your content calendar spreadsheet.
3. Generates platform-optimized post text with the OpenAI model.
4. Schedules a post to X (Twitter) at the given date and time. Schedules a post to Bluesky at the given date and time. Schedules a post to Mastodon at the given date and time. Schedules a post to Threads at the given date and time. Schedules a post to LinkedIn at the given date and time.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Connect Google Sheets and pick your spreadsheet and sheet.
3. Connect your OpenAI account in the OpenAI Chat Model node.
4. Select your connected account in each Publish node.
5. Confirm the schedule date, or map it from an upstream field.
6. Confirm the schedule date, or map it from an upstream field.
7. Confirm the schedule date, or map it from an upstream field.
8. Confirm the schedule date, or map it from an upstream field.
9. Confirm the schedule date, or map it from an upstream field.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A Google account and a Google Sheet with date and caption columns.
- An [OpenAI API key](https://platform.openai.com/api-keys), connected in the OpenAI Chat Model node.

**How to customize**
Edit the topic or source content in the Set node to change what the AI writes, or swap the OpenAI model for a different one in the chat model node. Change the schedule date, or map it from an upstream field like a spreadsheet column. Add or remove Publish nodes (X (Twitter), Bluesky, Mastodon, Threads, LinkedIn) and edit each node's caption and media fields to fit your brand voice.

---

## Schedule social media posts from a Google Sheets calendar

This workflow schedules a post to X (Twitter) at the given date and time. Schedules a post to Bluesky at the given date and time. Schedules a post to Mastodon at the given date and time. Schedules a post to Threads at the given date and time. Schedules a post to LinkedIn at the given date and time. It's for social media teams that plan content in a spreadsheet and want it published on schedule. It removes the manual work of posting every spreadsheet row by hand.

**How it works**
1. Runs when you click Execute Workflow.
2. Reads the rows of your content calendar spreadsheet.
3. Schedules a post to X (Twitter) at the given date and time. Schedules a post to Bluesky at the given date and time. Schedules a post to Mastodon at the given date and time. Schedules a post to Threads at the given date and time. Schedules a post to LinkedIn at the given date and time.

**How to set up**
1. Install the SocialRobot community node, then create an API key at [socialrobot.io](https://socialrobot.io) (Scheduler -> API Keys) and connect your SocialRobot API credential.
2. Connect Google Sheets and pick your spreadsheet and sheet.
3. Select your connected account in each Publish node.
4. Confirm the schedule date, or map it from an upstream field.
5. Confirm the schedule date, or map it from an upstream field.
6. Confirm the schedule date, or map it from an upstream field.
7. Confirm the schedule date, or map it from an upstream field.
8. Confirm the schedule date, or map it from an upstream field.

**Requirements**
- A [SocialRobot](https://socialrobot.io) account with connected social channels and an API key.
- A Google account and a Google Sheet with date and caption columns.

**How to customize**
Change the schedule date, or map it from an upstream field like a spreadsheet column. Add or remove Publish nodes (X (Twitter), Bluesky, Mastodon, Threads, LinkedIn) and edit each node's caption and media fields to fit your brand voice.

---
