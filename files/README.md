# Build Kit 01 files: YouTube Summarizer

This folder is the tool. Put it anywhere on your computer (for example in your Documents folder),
open it in Claude Code, and paste a YouTube link with "summarize".

Build date: 2026-09-26

## What is in the folder

```
youtube-summaries/
  README.md                          this file
  prompt.md                          the copy-paste prompt for any chat assistant
  .claude/
    skills/
      youtube-summary/
        SKILL.md                     tells Claude Code how to make the summary
        fetch_transcript.py          reads the video's captions
  summaries/                         created on first use; your summaries go here
```

The `.claude` folder starts with a dot, so your computer may hide it. It is still there.

## Versions

| Item | Version |
|---|---|
| Python | 3.12 |
| youtube-transcript-api | 1.2.4 |
| Claude Code | the Code tab of the Claude desktop app 2.19675.0 (rerun of 2026-10-03) |

## One-line install

The fetcher needs one library. Install it once:

- macOS or Linux: `python3 -m pip install youtube-transcript-api==1.2.4`
- Windows: `py -m pip install youtube-transcript-api==1.2.4`

If you see "externally-managed-environment", follow Step 4b in the README at the top of this repository (`../README.md`).

## Use it

1. Open this folder in Claude Code (`claude` in a terminal inside the folder).
2. Type: `summarize https://www.youtube.com/watch?v=...`
3. Open the file it names, in the `summaries` folder.

No account key is needed. The tool reads public captions only and writes only to `summaries/`.

## Remove it

Delete the folder `.claude/skills/youtube-summary`. To remove everything, delete this whole folder.

## More

The Receipt and the Break Log are in this repository. The step-by-step guide with the access check
is in Build Kit 01: https://noelyss.com/kadeactuallybuilds?utm_source=github&utm_medium=repo&utm_campaign=kade&utm_content=build-01
