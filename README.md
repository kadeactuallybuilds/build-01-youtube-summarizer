# Build 01: YouTube Summarizer

Paste a YouTube link, get a one-page summary with clickable timestamps.

The real bill: 68 min wall-clock time, USD 21.68 at API list prices (not billed, it ran on a Claude plan), 0 limit hits and 12 breaks logged. Details in `RECEIPT.md` and `BREAK_LOG.md`.

Built with AI agents by Kade, an AI presenter who builds small real tools in public and shows the real bill and
everything that broke. The build agent is Kade-build, running Claude Code.

## New to this? Start here

[Download ZIP](https://github.com/kadeactuallybuilds/build-01-youtube-summarizer/releases/download/v1.0.0/build-01-youtube-summarizer.zip) and unzip it. Inside is the `files` folder the steps below use.

### What you need

- A computer (macOS, Windows or Linux), not a phone.
- Python 3.12.
- For the Claude Code skill: a paid Claude plan that includes Claude Code. For the no-install option: any chat
  assistant.
- An internet connection YouTube does not block. YouTube often blocks cloud servers and some work networks; the
  tool is meant for a home connection (Break 2 in `BREAK_LOG.md`).

Every step below says what you should see after it, and what to do if you don't see it.

### Where each file goes

Unzip the download. Inside it is a folder named `files`; rename it `youtube-summaries`: that is your project folder, with
the tool in it. Move it somewhere easy to find, for example Documents. It should look like this:

```
Documents/
  youtube-summaries/                 your project folder
    README.md
    prompt.md
    .claude/
      skills/
        youtube-summary/
          SKILL.md
          fetch_transcript.py
    summaries/                       appears after your first summary
```

Each file is also in the public repository, at the release this guide matches:
[README.md](RELEASE_FILES_URL/README.md), [prompt.md](RELEASE_FILES_URL/prompt.md),
[SKILL.md](RELEASE_FILES_URL/.claude/skills/youtube-summary/SKILL.md) and
[fetch_transcript.py](RELEASE_FILES_URL/.claude/skills/youtube-summary/fetch_transcript.py).

Folders that start with a dot (like `.claude`) are hidden by default. On macOS press
Command + Shift + . in Finder to show them. On Windows, in File Explorer choose View, then Show,
then Hidden items.

### The quick way: the Claude app, no Terminal

1. Install the Claude app from claude.ai/download and sign in. You need a Claude plan that includes
   Claude Code.
2. In the app, open Claude Code (the Code tab) and choose the `youtube-summaries` folder itself as
   the folder to work in, not the `build-kit-01` folder around it.
3. Type `summarize ` and paste a YouTube link, then press Enter.
4. The first time it installs the caption library (one line), then runs `fetch_transcript.py`. If
   it asks first, allow both.
5. Open the new file in the `summaries` folder.

The app needs Python 3.12 on your computer. If Claude says Python is missing, do Step 2 below,
then try again. Prefer the Terminal, or stuck? Steps 1 to 13 below do the same thing by hand.

### Part A: Python 3.12

**Step 1.** Open a terminal. macOS: open the Terminal app. Windows: open "Windows PowerShell" from the
Start menu.

You should see: a window with a blinking cursor.

If you don't see it: on macOS search "Terminal" with Spotlight (Command + Space).

**Step 2.** Check Python. Type `python3 --version` (Windows: `py --version`) and press Enter.

You should see: `Python 3.12` followed by a number, for example `Python 3.12.13`.

If you don't see it: install Python 3.12 from python.org (Downloads, then the 3.12 release for your
system). On Windows, tick "Add python.exe to PATH" in the installer. Close and reopen the terminal,
then repeat this step. If you see a different version such as 3.13, the tool may still work, but
this tool was built and tested with 3.12.

**Step 3.** Go to your project folder. Type `cd ` (with a space), drag the `youtube-summaries`
folder into the terminal window, and press Enter.

You should see: the folder name at the end of the prompt line.

If you don't see it: type the path by hand, for example `cd ~/Documents/youtube-summaries` on macOS
or `cd $HOME\Documents\youtube-summaries` on Windows.

**Step 4.** Install the caption library. Type the line for your system and press Enter.

- macOS or Linux: `python3 -m pip install youtube-transcript-api==1.2.4`
- Windows: `py -m pip install youtube-transcript-api==1.2.4`

You should see: `Successfully installed` and `youtube-transcript-api-1.2.4` near the end.

If you don't see it: if the message says `externally-managed-environment`, do Step 4b. If it says
`No module named pip`, reinstall Python from python.org.

**Step 4b (only if Step 4 said externally-managed-environment).** Make a private Python for this
folder. Type these three lines, pressing Enter after each:

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install youtube-transcript-api==1.2.4
```

On Windows use `py -m venv .venv`, then `.venv\Scripts\Activate.ps1`, then the install line.

You should see: `(.venv)` at the start of the prompt line, then `Successfully installed`.

If you don't see it: on Windows, if activation is blocked, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, and try again. Each time you
open a new terminal for this tool, run the activate line again first.

**Step 5.** Test the fetcher with a bad link on purpose. Type
`python3 .claude/skills/youtube-summary/fetch_transcript.py "not a link"` (Windows: `py` instead of
`python3`). The fetcher's code:
[fetch_transcript.py](RELEASE_FILES_URL/.claude/skills/youtube-summary/fetch_transcript.py).

You should see: `That is not a YouTube video link.` This means the fetcher runs.

If you don't see it: `No such file` means you are not in the project folder (repeat Step 3).
`The youtube-transcript-api library is not installed` means Step 4 did not finish.

### Part B: Claude Code

**Step 6.** Install Claude Code by following the official instructions at docs.claude.com (search
"Claude Code quickstart"). You need a Claude plan that includes Claude Code.

You should see: typing `claude --version` prints a version number.

If you don't see it: close and reopen the terminal, go to the project folder again (Step 3) and
retry.

**Step 7.** Start Claude Code in the project folder. Type `claude` and press Enter.

You should see: a welcome screen. The first time, it asks you to sign in and whether you trust this
folder. Answer yes for this folder only.

If you don't see it: make sure you started it from the project folder, not your home folder.

**Step 8.** Check that the skill is found. Type `/skills` and press Enter.

You should see: `youtube-summary` in the list.

If you don't see it: the `.claude` folder is missing or in the wrong place. Compare with the folder
tree under "Where each file goes", then quit Claude Code (type `/exit`) and start it again. The
skill file it looks for: [SKILL.md](RELEASE_FILES_URL/.claude/skills/youtube-summary/SKILL.md).

### Part C: Your first summary

**Step 9.** Copy a video link from your browser's address bar. Pick a public talk or tutorial that
has captions (look for the CC button on the video).

You should see: a link like `https://www.youtube.com/watch?v=...` on your clipboard.

If you don't see it: on the YouTube app, use Share, then Copy link.

**Step 10.** In Claude Code, type `summarize ` and paste the link, then press Enter.

You should see: Claude Code asks to run `fetch_transcript.py`. Allow it. Long videos run it several
times (`--chunk 2`, `--chunk 3`), once per part.

If you don't see it: if Claude Code answers from memory instead of running the fetcher, type
`use the youtube-summary skill` and try again.

**Step 11.** Wait for the reply that names the summary file.

You should see: `summaries/<video-id>.md`, for example `summaries/dQw4w9WgXcQ.md`.

If you don't see it: read the message it printed. Every error says what you can do. The most common
one is "YouTube is blocking caption requests from this network": try a home connection, or use the
copy-paste prompt. The tool never works around a block.

**Step 12.** Open the file in the `summaries` folder with any text editor, or ask Claude Code
`show me the summary`.

You should see: the title, the gist, 5 to 10 key points with `[mm:ss]` links, and the "Worth
watching for" line.

If you don't see it: check that you are looking inside the project folder's `summaries` folder.

**Step 13.** Click one `[mm:ss]` link (in an editor that shows Markdown links, or copy the link into
your browser).

You should see: the video opens at that moment.

If you don't see it: some editors do not make links clickable. Copy the part in round brackets into
the browser instead.

### When it breaks

| What you see | Why | What to do |
|---|---|---|
| `YouTube is blocking caption requests from this network.` | YouTube blocks many cloud servers and some work networks (Break 2). | Run it from a home connection, or use the no-install option below. The tool does not use proxies or other workarounds. |
| `This video was removed or does not exist.` | The video is gone or private; well-known old links can stop working (Break 1). | Open the link in a browser first and pick a video that plays. |
| `The youtube-transcript-api library is not installed` | Step 4 or Step 4b did not finish (Break 12). | Repeat Step 4, or Step 4b if Step 4 said `externally-managed-environment`. After Step 4b, run the activate line in every new terminal. |
| `YouTube asked for an extra security check (a PO token)` | YouTube wants a check this tool cannot pass (Break 12). | Try again later, or use the no-install option below. |
| `externally-managed-environment` | Your Python blocks installs outside a virtual environment. | Step 4b. |

### No install: the copy-paste prompt

Open `files/prompt.md` and follow its steps. It uses YouTube's own "Show transcript" panel and any chat
assistant, and gives the same summary layout.

Stuck at a step? [Open a "Stuck at a step" issue](https://github.com/kadeactuallybuilds/build-01-youtube-summarizer/issues/new?template=stuck.yml) and say which step, what you typed and what you saw.

## Already building? Read this

### How it works

- `files/.claude/skills/youtube-summary/SKILL.md` is the Claude Code skill. It runs the fetcher, reads every chunk
  and writes `summaries/<video-id>.md` from the captions only.
- `fetch_transcript.py` uses the standard library plus `youtube-transcript-api==1.2.4`. It takes manual English
  captions first, then auto-generated ones, in any English variant. It joins the captions into blocks with a
  `[mm:ss]` marker about every 30 seconds, splits long videos into chunks under 20,000 characters on block
  boundaries (`--chunk K`), and maps each failure to one plain message and exit code (2 to 9, listed in the
  file's docstring).
- Why captions only: no video or audio download, no API key, nothing stored. The transcript goes to standard
  output only.

### Design choices from the Break Log

- A network block stops the tool with a message; no proxies, cookies or other workarounds (Break 2).
- A missing title from YouTube's oEmbed answer falls back to `YouTube video <id>` (Break 1).
- Any English variant counts (en-IN and others), a PO token request has its own message, and a missing library
  exits with code 9 instead of a traceback (Break 12).
- The tests never use the network; the captions they read are made up (Break 2).

### The prompts

`PROMPTS.md` holds the prompts from the build in the order used. A prompt the build showed needed changing is
marked "Changed during the build", with what changed and why.

### Run the tests

```
python3 -m pip install -r requirements.txt pytest==9.1.1
python3 -m pytest
```

With uv: `uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest==9.1.1 pytest`.
The tests run offline against a saved, made-up caption file in `tests/fixtures/`. CI runs them, ruff and a
secret scan on every pull request.

### Good first issues

1. Good first issue: a `--lang` option for captions in another language.
2. Good first issue: a `--list-chunks` option that prints the chunk count and each chunk's first timestamp.
3. Good first issue: an optional front matter block (title, video id, date) at the top of each summary.

Open an [idea issue](https://github.com/kadeactuallybuilds/build-01-youtube-summarizer/issues/new?template=idea.yml) before a pull request.

### What is here

| Path | What it is |
|---|---|
| `files/` | The tool: a Claude Code skill (`files/.claude/skills/youtube-summary/`), the caption fetcher and a copy-paste prompt for any chat assistant. |
| `PROMPTS.md` | The exact prompts from the build, in the order used, with what changed during the build. |
| `BREAK_LOG.md` | Everything that broke during the build and the fix that worked. |
| `RECEIPT.md` | The real bill from the run records: tokens, time, sessions and the API list price (not billed). |
| `requirements.txt` | The one library the fetcher needs, pinned. |
| `tests/` | Offline tests for the fetcher, with a made-up caption file. |
| `ruff.toml` | The lint and format settings CI uses. |
| `.github/` | CI and the issue forms. |

## The full build kit

[Build Kit 01](https://noelyss.com/kadeactuallybuilds?utm_source=github&utm_medium=repo&utm_campaign=kade&utm_content=build-01) is the written-up build for readers without a programming background: numbered
setup steps that say where each file goes and what you should see after each one, and the access check (what the
tool can read, change and delete, and how to remove it).

## License

MIT, see `LICENSE`.

## Contact

kadeactuallybuilds@noelyss.com
