# The prompts

This build was run by an AI agent (Kade-build, running Claude Code) from a written spec (the build issue; it
is internal and not part of this kit). The prompts below are the ones a person types into Claude Code to rebuild the same tool, in
order. A prompt marked "Changed during the build" is one the build showed needed changing; the note
names the Break Log entry. These prompts are rerun on a clean machine before release.

Start Claude Code in an empty folder, then type each prompt and wait for it to finish before the
next one.

## Prompt 1: the folder

```
Create this folder layout in the current folder: .claude/skills/youtube-summary/ and summaries/.
Add a README.md that says what the folder is for: a Claude Code skill that turns a YouTube link
into a one-page summary with clickable timestamps.
```

## Prompt 2: the caption fetcher

```
Write .claude/skills/youtube-summary/fetch_transcript.py for Python 3.12 using only the standard
library and youtube-transcript-api==1.2.4. It takes a YouTube link and an optional --chunk K.
- Accept watch, youtu.be, shorts, embed and live links, with or without https, extra parameters
  and a t= or start= time (90, 90s, 1m30s, 1h2m3s). Reject anything else.
- Prefer manual English captions, then auto-generated English captions. Never download video or
  audio. Never use proxies or cookies.
- Print header lines VIDEO_ID, TITLE (from YouTube's oEmbed address, or "YouTube video <id>"),
  URL, CAPTIONS (manual or auto-generated), LINK_STARTS_AT when the link had a time, and
  CHUNK: k of N. Then print the text with a [mm:ss] marker about every 30 seconds.
- Split long videos into chunks under 20,000 characters on marker boundaries, and print
  "NEXT: run again with --chunk k+1" until the last chunk.
- For no captions, private, age-restricted or removed videos, a network block, or no internet,
  print one plain-English message with a "What you can do" line and exit with its own code.
  No tracebacks. Write no files.
```

## Prompt 3: tests without internet

```
Add pytest tests that never touch the network: link forms, timestamp formatting, chunking,
manual versus auto captions from saved made-up captions, and every error message. Run them and
the ruff linter, and fix anything that fails.
```

## Prompt 4: the skill

```
Write .claude/skills/youtube-summary/SKILL.md with YAML frontmatter (name: youtube-summary and
a description saying to use it when the user pastes a YouTube link and asks for a summary). The
steps: run the fetcher on the link; if it fails, show the message and stop; read every chunk
with --chunk; write summaries/<VIDEO_ID>.md with the title, a one-line gist, 5 to 10 key points
each starting with a [mm:ss](https://www.youtube.com/watch?v=<id>&t=<seconds>s) link, a "Worth
watching for" line, a note when captions were auto-generated, and the source link. Use only what
is in the transcript.
```

## Prompt 5: one real run

```
Pick one public, non-controversial talk or tutorial with English captions. First check that it
exists with YouTube's oEmbed address and only use it if that answers with its title. Then run the
fetcher on it, and if it works, follow SKILL.md to write the summary. If YouTube blocks this
network, stop, write down the exact message, and do not try any workaround.
```

Changed during the build: the first version said only "run the fetcher on one public talk". The
first video ids picked from memory no longer worked (Break 1), so the prompt now says to check the
video with oEmbed first. The "if YouTube blocks this network" sentence was added after the real
run was blocked (Break 2).

## Prompt 6: the copy-paste prompt

```
Write prompt.md for people without Claude Code: numbered steps to open YouTube's "Show
transcript" panel on a computer and copy it, then a prompt for any chat assistant that asks for
the same summary layout as SKILL.md, using only the pasted transcript. Say what to do when a long
transcript does not fit in one message.
```
