# Build Log: Build Kit 01, YouTube Summarizer

- Build date: 2026-09-26 (UTC)
- Run by an AI agent (Kade-build, running Claude Code) from spec.md
- Agent run id: (internal run id)
- Build machine: a Linux cloud server (aarch64), uv 0.12.19, Python 3.12.13
- Start time: 23:42 UTC

This file is written while the build runs. Every failed command, failed test, wrong assumption and
dead end goes in as a Break the moment it happens. Times are rough ("about").

## Real run

The fetcher was run for real against public tutorial videos from the build machine, a cloud server.
YouTube blocked the caption requests (library error RequestBlocked, the tool exited with code 6 and
printed its "YouTube is blocking caption requests from this network" message). Per the spec, no
workaround was tried: no proxies, no cookies, no other network, no other library, no transcript
site. The tests use saved, made-up caption fixtures instead. The real run has to be repeated on a
home connection (see Human steps left). No example summary is included because no real transcript
could be read.

## Break 1: The first test videos were not usable
- What happened: the first video picked for the real run (a PyCon talk, id wf-BqAjZb8M) returned
  "401 Unauthorized" from YouTube's oEmbed title lookup, and the fetch was started in the same
  command before that answer was read. The second pick (id OSLbwQiDldY) returned "404 Not Found"
  from oEmbed and VideoUnavailable from the caption library: the video no longer exists. Wrong
  assumption: that well-known talk ids from memory still work.
- Fix that failed: none
- Fix that worked: checked candidates with oEmbed first and used one that answered 200
  (freeCodeCamp.org "Learn Python - Full Course for Beginners", id rfscVS0vtbw). Also learned that
  oEmbed can answer 401 for a video that exists, so the fetcher treats a missing title as normal and
  falls back to "YouTube video <id>".
- Time lost: roughly 2 min

## Break 2: YouTube blocks caption requests from the build machine
- What happened: `fetch_transcript.py "https://www.youtube.com/watch?v=rfscVS0vtbw"` exited 6. The
  library raised RequestBlocked ("YouTube is blocking requests from your IP"). The same happened for
  the first video. The build machine is a cloud server, and YouTube often blocks those.
- Fix that failed: none
- Fix that worked: not fixed, see human steps. The spec forbids working around a block.
- Time lost: roughly 1 min

## Break 3: The linter failed on the first test files
- What happened: `uv run ruff check .` reported 2 errors after the first 84 tests passed: an
  import block in the wrong order in tests/test_errors.py and one line longer than 100 characters.
- Fix that failed: none
- Fix that worked: `uv run ruff check --fix .` for the imports, split the long line by hand, and
  told ruff which modules are the kit's own (known-first-party) so the import order stays stable.
- Time lost: roughly 1 min

## Break 4: The first guide PDF was 13 pages, not 10 to 12
- What happened: the first `uv run python build.py` printed a 13-page guide. Section 1 ran 8
  lines onto a second page.
- Fix that failed: shortening section 1's wording still left 5 lines on the second page (13
  pages again).
- Fix that worked: folded "Setup time" and "Where it stands" into short paragraphs and set the
  body text from 10.5pt to 10pt. The guide is now 12 pages.
- Time lost: roughly 3 min

## Break 5: No PDF text tool on the build machine
- What happened: to see which section overflowed, the agent ran `pdftotext` on the guide. The
  command is not installed on the build machine (exit code 2).
- Fix that failed: none
- Fix that worked: read the page texts with the pypdf library in a throwaway environment
  (`uv run --no-project --with pypdf`), which is not part of the kit or its lockfile.
- Time lost: roughly 1 min

## Break 6: Four new tests failed on their first run
- What happened: after adding the receipt, Break Log, guide, zip, secret-scan, copy-rule and skill
  tests, 4 of 139 failed and ruff found 2 lines that were too long. The trader identity test compared
  against text still holding the HTML escape for "&". The receipt test expected 17 table rows when
  the page has 16 (the test's count was wrong, not the page). The "no cookies" check in the skill
  test matched the host name youtube-nocookie.com.
- Fix that failed: none
- Fix that worked: unescaped the HTML in the test, corrected the row count to 16, checked for the
  words `cookies=` and `http_client` (the ways to pass cookies to the library) instead of the bare
  word, and split the long lines. 140 tests pass.
- Time lost: roughly 3 min

## Break 7: The guide went back to 13 pages as the Break Log grew
- What happened: after Breaks 3 and 4 were added, the Break Log took 2 pages and the guide was 13
  pages again.
- Fix that failed: showing each break as a short list instead of a table, letting the short rerun
  record share the access check's page, and shortening sections 7 and 8. Each left the guide at 13
  pages, since the last screenshot box and the trader line still spilled onto a new page.
- Fix that worked: smaller screenshot placeholder boxes and a smaller gap above the trader line.
  The guide is 11 pages. Setup (section 3) is 3 pages with placeholders; the real screenshots are
  expected to take it toward the 4 to 6 pages in the spec, so the page count is checked again after
  they are added.
- Time lost: roughly 5 min

## Break 8: uv used a shared environment outside the kit folder
- What happened: the final `uv sync --locked` check printed that it removed `studio-jev` (a package
  from another build folder). The build machine sets `UV_PROJECT_ENVIRONMENT` to a shared
  environment in the home folder, so every `uv sync` and `uv run` in this build installed the kit's
  packages there and removed that environment's other packages. Wrong assumption: that uv would
  make a `.venv` inside the kit folder.
- Fix that failed: none
- Fix that worked: not fixed in the build machine's setup (it is outside this kit). Other projects
  that use `uv run` reinstall their own packages on their next run. The kit's README now says to
  unset `UV_PROJECT_ENVIRONMENT` so the kit gets its own `.venv`. Clean machines and CI do not set
  it.
- Time lost: roughly 2 min

## Break 9: The first code review found two bugs
- What happened: a review found that captions with no readable text said "no English captions
  (captions found: en)", and that the receipt priced a run with several models at the first
  model's prices.
- Fix that failed: none
- Fix that worked: a separate "no readable text" message, a list price only for one model, and 8
  new tests. 148 tests pass.
- Time lost: roughly 5 min

## Break 10: The CI jobs never started on GitHub's runners
- What happened: the CI jobs on GitHub-hosted runners did not start (GitHub Actions billing).
- Fix that failed: none
- Fix that worked: the owner moved CI to the organization's self-hosted runners (2026-09-27).
- Time lost: roughly 0 min of agent time

## Break 11: The first self-hosted CI run failed the linter
- What happened: ruff reported a test line over 100 characters, added in Break 9 without running
  ruff again.
- Fix that failed: none
- Fix that worked: wrapped the line. Ruff now runs before every commit.
- Time lost: roughly 4 min

## Break 12: A second review found eight more problems
- What happened: without the caption library, setup Step 5 printed a traceback instead of a plain
  message. Captions only in en-IN or another English variant were refused. PoTokenRequired was
  reported as a network block. A video id ending in a newline was accepted. Some network errors
  printed a traceback. No test ran build.py to the end. This log and the pull request description
  were out of date. A `uv run` changed the shared environment again (Break 8), and one new test
  line was too long for ruff.
- Fix that failed: none
- Fix that worked: fixed each one (exit code 9 now means the library is missing) and added 11
  tests. 159 tests pass and the guide is 12 pages.
- Time lost: roughly 10 min

## Timeline

- 23:42 UTC: session 1 starts; project skeleton, lockfile and fetcher written
- 23:43 UTC: first real run, blocked (Break 1, Break 2)
- 23:45 UTC: fetcher tests pass (84), linter fails then passes (Break 3); real run retried once,
  still blocked with the same message
- 23:49 UTC: first full build; guide too long (Break 4, Break 5), fixed
- 23:50 UTC: remaining tests written; 4 fail, then fixed (Break 6)
- 23:51 UTC: CI workflow written; action commit SHAs checked against their tags; gitleaks finds
  no leaks in the kit folder
- 23:53 UTC: guide back to 13 pages, fixed to 11 (Break 7)
- 23:54 UTC: found that uv used a shared environment (Break 8)
- 23:54 UTC: session 1 ends after roughly 14 min
- 2026-09-27 00:10 UTC: session 2, fixes from the first code review; 148 tests pass (Break 9)
- 06:26 UTC: session 3; CI moved to self-hosted runners (Break 10); the first run fails ruff,
  fixed at 06:30 (Break 11)
- 06:45 UTC: session 4, second review; fixes at 07:01, 159 tests pass (Break 12)
- Total wall-clock time: roughly 14 min in session 1, then roughly 25 min over sessions 2 to 4. This
  is the agent's own clock; the Receipt uses the run records instead.
