# YouTube summary prompt (for any chat assistant)

Use this if you do not use Claude Code. It gives the same one-page summary, but you copy the
transcript yourself. YouTube's menus change from time to time, so the labels below say "look for".

## Get the transcript

1. Open the video on a computer (the transcript panel is hard to copy on a phone).
2. Under the video title, click "...more" to open the description.
3. Scroll down in the description and look for the "Show transcript" button. Click it.
4. A transcript panel opens next to the video. Leave the timestamps turned on.
5. Click inside the panel, select all of its text and copy it.

If you don't see "Show transcript": the video may have no captions. This prompt only works with
captions, so pick another video.

Timestamps in the panel look like `3:07` or `1:02:05`. That is fine.

## Ask the assistant

6. Open any chat assistant.
7. Paste the prompt below.
8. Under it, paste the video link, then the transcript you copied, and send.

Long videos can be too long for one chat message. If the assistant says the message is too long,
paste the transcript in parts and start each part with "part 1 of 3", "part 2 of 3" and so on. Ask
for the summary after the last part.

```
Summarize this YouTube video from its transcript. Use only what is in the transcript: add no
outside facts, opinions or links.

Write it in exactly this layout:

# <video title, or "YouTube video" if you cannot tell>

**Gist:** <one line>

## Key points

- [mm:ss](<video link>&t=<seconds>s) <point>
(5 to 10 points in video order; mm:ss comes from the transcript's timestamps; <seconds> is that
time in whole seconds, for example 3:07 is 187; if the video link has no "?" in it, use "?t="
instead of "&t=")

**Worth watching for:** <one short line>

Source: <video link>

Video link:
Transcript:
```

## Use it fairly

This reads captions only. Keep summaries for your own use and do not republish full transcripts.
