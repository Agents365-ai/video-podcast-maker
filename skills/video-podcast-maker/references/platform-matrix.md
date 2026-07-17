# Video Podcast Maker — Platform Matrix

> **When to load:** When generating platform-specific outputs (publish info, thumbnails, outro, shorts). Reference during Steps 7, 9, 10, 13, and 15.

## Overview

| Property | Bilibili | YouTube | Xiaohongshu | Douyin | WeChat Channels |
| ---------- | ---------- | --------- | ------------- | -------- | ----------------- |
| **Video format** | Horizontal 16:9 | Horizontal 16:9 | Primarily vertical 9:16 | Vertical 9:16 only | Vertical 9:16 only |
| **Long-form horizontal** | Yes | Yes | Optional | No | No |
| **Thumbnail (16:9)** | Required | Required | — | — | — |
| **Thumbnail (4:3)** | Required | Required | — | — | — |
| **Thumbnail (3:4)** | — | — | Required | — | — |
| **Thumbnail (9:16)** | — | — | With vertical render | With vertical render | With vertical render |
| **Chapters** | Yes (MM:SS) | Yes (0:00 first) | No | No | No |
| **Outro animation** | Pre-made MP4 | Pre-made MP4 / text | Text CTA | Text only | Text only |
| **Shorts pipeline** | `generate_shorts.py` | `generate_shorts.py` | `generate_shorts.py` | `generate_shorts.py` | `generate_shorts.py` |

## Thumbnail Aspect Ratios

| Platform | Required Ratios | Command |
| ---------- | ---------------- | --------- |
| Bilibili | 16:9 + 4:3 | `remotion still ... Thumbnail16x9` + `Thumbnail4x3` |
| YouTube | 16:9 + 4:3 | `remotion still ... Thumbnail16x9` + `Thumbnail4x3` |
| Xiaohongshu | 3:4 (replaces 4:3) | `remotion still ... Thumbnail3x4` |
| Douyin | 9:16 (with vertical render) | `remotion still ... Thumbnail9x16` |
| WeChat Channels | 9:16 (with vertical render) | `remotion still ... Thumbnail9x16` |

## Outro Animation by Platform

| Platform | Mode | Action |
| ---------- | ------ | -------- |
| Bilibili | Pre-made MP4 | `cp assets/bilibili-triple-{white,black}.mp4 videos/{name}/media/` (theme: light→white, dark→black) |
| YouTube | Text CTA or pre-made MP4 | Interactive mode: ask user preference |
| Xiaohongshu | Text CTA | Animated text overlay (no pre-made MP4) |
| Douyin | Text only | Simple end text (no animation) |
| WeChat Channels | Text only | Simple end text (no animation) |

## Publish Info Format

| Platform | Title Limit | Description Style | Hashtag Format | Chapters |
| ---------- | ------------- | ------------------- | ---------------- | ---------- |
| Bilibili | Title formula (number + topic + hook) | 100-200 chars | Tags (comma-separated) | `MM:SS Chapter Title` (≥5s gaps) |
| YouTube | <70 chars, SEO-optimized | Keyword-rich with timestamps | `#tag1 #tag2` (space-separated) | `0:00 Chapter Title` (first line) |
| Xiaohongshu | ≤20 chars, punchy + emoji | 200-500 chars, 种草 style + emoji | `#话题#` (double hash, 5-10) | N/A |
| Douyin | 100-200 chars, casual + emoji | Conversational tone | `#话题` (single hash, 3-8) | N/A |
| WeChat Channels | 100-300 chars, knowledge-sharing | Suitable for forwarding | `#话题` (single hash, 3-8) | N/A |

## Outro Text by Platform + Language

| Platform | zh-CN | en-US |
| ---------- | ------- | ------- |
| Bilibili | "一键三连！评论区留言，下期再见！" | "Like, coin, and favorite! Leave a comment, see you next time!" |
| YouTube | "点赞订阅转发！评论区留言，下期再见！" | "Like, subscribe, and share! Leave a comment, see you next time!" |
| Xiaohongshu | "点赞收藏加关注，评论区见！" | "Like, save & follow! See you in comments!" |
| Douyin | "点赞关注，评论区见！" | "Like & follow! See you in comments!" |
| WeChat Channels | "点赞关注，转发给朋友！" | "Like, follow & share with friends!" |

## Vertical Shorts Behavior

| Platform | Shorts generated | Notes |
| ---------- | ----------------- | ------- |
| Bilibili | Optional (Step 15) | Long-form is primary |
| YouTube | Optional (Step 15) | Long-form is primary; Shorts are separate content |
| Xiaohongshu | Recommended | Vertical shorts are primary format |
| Douyin | Required | Douyin is shorts-only — no horizontal long-form video |
| WeChat Channels | Required | Channels is shorts-only — no horizontal long-form video |
