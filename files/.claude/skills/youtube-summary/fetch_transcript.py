# /// script
# requires-python = ">=3.12"
# dependencies = ["youtube-transcript-api==1.2.4"]
# ///
"""Fetch the English captions of one YouTube video as timestamped plain text.

Used by the youtube-summary skill. It reads captions only (never video or audio), needs no API
key, and stores nothing: the transcript text goes to standard output and nowhere else.

One-line install (Python 3.12):
    macOS or Linux:  python3 -m pip install youtube-transcript-api==1.2.4
    Windows:         py -m pip install youtube-transcript-api==1.2.4

Usage:
    python3 fetch_transcript.py "<youtube link>"            # chunk 1
    python3 fetch_transcript.py "<youtube link>" --chunk 2  # later chunks of a long video

Exit codes:
    0 ok, 2 not a video link or no such chunk, 3 no English captions, 4 removed or unplayable,
    5 age-restricted, 6 YouTube is blocking this network, 7 could not reach YouTube,
    8 unexpected YouTube response, 9 youtube-transcript-api is not installed.

When YouTube blocks a network, this tool stops and says so. It does not use proxies, cookies or
any other workaround.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Sequence

ENGLISH_CODES = ["en", "en-US", "en-GB", "en-CA", "en-AU"]
BLOCK_SECONDS = 30
MAX_CHUNK_CHARS = 20000

_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")  # always used with fullmatch
_TIME_RE = re.compile(r"^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?$")
_YOUTUBE_HOSTS = {"youtube.com", "m.youtube.com", "music.youtube.com", "youtube-nocookie.com"}
_PATH_PREFIXES = ("shorts", "embed", "live", "v", "e")

Block = tuple[float, str]


class LinkError(ValueError):
    """The text is not a YouTube video link."""


class NoEnglishCaptions(Exception):
    """The video has captions, but none in English."""

    def __init__(self, available: list[str]):
        super().__init__(", ".join(available))
        self.available = available


class EmptyCaptions(Exception):
    """The chosen transcript has no usable text (e.g. a music-only track)."""

    def __init__(self, language_code: str):
        super().__init__(language_code)
        self.language_code = language_code


def _parse_time(value: str) -> int | None:
    value = value.strip().lower()
    if not value:
        return None
    match = _TIME_RE.match(value)
    if not match or not any(match.groups()):
        return None
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


def parse_link(text: str) -> tuple[str, int | None]:
    """Return (video_id, start_seconds) for any common YouTube link form or a bare video id."""
    text = (text or "").strip()
    if _ID_RE.fullmatch(text):
        return text, None
    if not text:
        raise LinkError("empty link")
    if "://" not in text:
        text = "https://" + text
    parts = urllib.parse.urlsplit(text)
    host = (parts.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    query = urllib.parse.parse_qs(parts.query)
    segments = [segment for segment in parts.path.split("/") if segment]

    video_id = None
    if host == "youtu.be" and segments:
        video_id = segments[0]
    elif host in _YOUTUBE_HOSTS:
        if segments == ["watch"] and query.get("v"):
            video_id = query["v"][0]
        elif len(segments) >= 2 and segments[0] in _PATH_PREFIXES:
            video_id = segments[1]
    if not video_id or not _ID_RE.fullmatch(video_id):
        raise LinkError(text)

    start = None
    fragment = urllib.parse.parse_qs(parts.fragment)
    for source in (query, fragment):
        for key in ("t", "start"):
            if key in source and start is None:
                start = _parse_time(source[key][0])
    return video_id, start


def format_timestamp(seconds: float) -> str:
    """Format seconds as mm:ss, or h:mm:ss from one hour on."""
    total = int(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def timestamp_link(video_id: str, seconds: float) -> str:
    return f"https://www.youtube.com/watch?v={video_id}&t={int(seconds)}s"


def build_blocks(snippets: Iterable, every: int = BLOCK_SECONDS) -> list[Block]:
    """Join caption snippets into blocks that start a new [mm:ss] marker about every 30 seconds."""
    blocks: list[Block] = []
    block_start: float | None = None
    words: list[str] = []
    for snippet in snippets:
        text = " ".join(str(snippet.text).split())
        if not text:
            continue
        if block_start is None:
            block_start = snippet.start
        elif snippet.start >= block_start + every:
            blocks.append((block_start, " ".join(words)))
            block_start, words = snippet.start, []
        words.append(text)
    if block_start is not None and words:
        blocks.append((block_start, " ".join(words)))
    return blocks


def _block_line(block: Block) -> str:
    return f"[{format_timestamp(block[0])}] {block[1]}"


def chunk_blocks(blocks: Sequence[Block], max_chars: int = MAX_CHUNK_CHARS) -> list[list[Block]]:
    """Split blocks into chunks under max_chars, never splitting a block."""
    chunks: list[list[Block]] = []
    current: list[Block] = []
    size = 0
    for block in blocks:
        length = len(_block_line(block)) + 1
        if current and size + length > max_chars:
            chunks.append(current)
            current, size = [], 0
        current.append(block)
        size += length
    if current:
        chunks.append(current)
    return chunks


def english_codes(transcript_list) -> list[str]:
    """ENGLISH_CODES first, then any other English variant the video has (en-IN, en-NZ, ...)."""
    found = {transcript.language_code for transcript in transcript_list}
    others = sorted(
        code
        for code in found
        if code not in ENGLISH_CODES and (code.lower() == "en" or code.lower().startswith("en-"))
    )
    return ENGLISH_CODES + others


def choose_transcript(transcript_list):
    """Prefer manual English captions, then auto-generated English captions."""
    from youtube_transcript_api import NoTranscriptFound

    codes = english_codes(transcript_list)
    try:
        return transcript_list.find_manually_created_transcript(codes)
    except NoTranscriptFound:
        pass
    try:
        return transcript_list.find_generated_transcript(codes)
    except NoTranscriptFound:
        pass
    available = sorted({transcript.language_code for transcript in transcript_list})
    raise NoEnglishCaptions(available)


def https_open(url: str, timeout: float):
    """Open an HTTPS URL, trusting certifi's certificate list when it is installed.

    A python.org Python that skipped its "Install Certificates" step cannot verify HTTPS through
    urllib, so the title lookup failed on the 2026-10-03 clean-machine rerun. certifi comes with
    the caption library (through requests), so it is there whenever the fetcher can run.
    """
    context = None
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    return urllib.request.urlopen(url, timeout=timeout, context=context)


def fetch_title(video_id: str, opener: Callable = https_open) -> str | None:
    """Look up the video title through YouTube's public oEmbed endpoint. Any failure gives None."""
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    url = "https://www.youtube.com/oembed?" + urllib.parse.urlencode(
        {"url": video_url, "format": "json"}
    )
    try:
        with opener(url, timeout=10) as response:
            title = json.loads(response.read().decode("utf-8")).get("title")
    except Exception:
        return None
    return title.strip() if isinstance(title, str) and title.strip() else None


def render(
    video_id: str,
    title: str | None,
    is_generated: bool,
    language_code: str,
    start: int | None,
    chunks: list[list[Block]],
    chunk_index: int,
) -> str:
    """Render one chunk with its header lines. chunk_index starts at 1."""
    total = len(chunks)
    lines = [
        f"VIDEO_ID: {video_id}",
        f"TITLE: {title or f'YouTube video {video_id}'}",
        f"URL: https://www.youtube.com/watch?v={video_id}",
        f"CAPTIONS: {'auto-generated' if is_generated else 'manual'} ({language_code})",
    ]
    if start is not None:
        lines.append(f"LINK_STARTS_AT: [{format_timestamp(start)}]")
    lines.append(f"CHUNK: {chunk_index} of {total}")
    lines.append("")
    lines.extend(_block_line(block) for block in chunks[chunk_index - 1])
    if chunk_index < total:
        lines.append("")
        lines.append(f"NEXT: run again with --chunk {chunk_index + 1}")
    return "\n".join(lines) + "\n"


class _Failure(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _explain(error: Exception) -> _Failure:
    """Map an expected failure to one plain-English message and an exit code."""
    import requests
    from youtube_transcript_api import (
        AgeRestricted,
        InvalidVideoId,
        IpBlocked,
        NoTranscriptFound,
        PoTokenRequired,
        RequestBlocked,
        TranscriptsDisabled,
        VideoUnavailable,
        VideoUnplayable,
        YouTubeRequestFailed,
        YouTubeTranscriptApiException,
    )

    if isinstance(error, (LinkError, InvalidVideoId)):
        return _Failure(
            2,
            "That is not a YouTube video link.\n"
            "What you can do: copy the full link from the browser's address bar and try again.",
        )
    if isinstance(error, NoEnglishCaptions):
        return _Failure(
            3,
            "This video has no English captions (captions found: "
            f"{', '.join(error.available) or 'none'}).\n"
            "What you can do: pick a video with English captions. This tool only reads captions.",
        )
    if isinstance(error, EmptyCaptions):
        return _Failure(
            3,
            f"This video's captions ({error.language_code}) contain no readable text, so there is "
            "nothing to summarize.\nWhat you can do: pick another video.",
        )
    if isinstance(error, (TranscriptsDisabled, NoTranscriptFound)):
        return _Failure(
            3,
            "This video has no captions, so there is nothing to summarize.\n"
            "What you can do: pick a video with captions. This tool only reads captions.",
        )
    if isinstance(error, VideoUnplayable):
        reason = f" YouTube says: {error.reason}." if getattr(error, "reason", None) else ""
        return _Failure(
            4,
            f"This video cannot be played (it is often private).{reason}\n"
            "What you can do: check that the video opens in a private browser window.",
        )
    if isinstance(error, VideoUnavailable):
        return _Failure(
            4,
            "This video was removed or does not exist.\n"
            "What you can do: check the link, or pick another video.",
        )
    if isinstance(error, AgeRestricted):
        return _Failure(
            5,
            "This video is age-restricted. The tool does not sign in, so it cannot read it.\n"
            "What you can do: pick another video, or use the copy-paste prompt in prompt.md.",
        )
    if isinstance(error, (IpBlocked, RequestBlocked)):
        return _Failure(
            6,
            "YouTube is blocking caption requests from this network. This is common on cloud "
            "servers and some work networks.\n"
            "What you can do: try again from a home internet connection, or use the copy-paste "
            "prompt in prompt.md. This tool does not use proxies or other workarounds.",
        )
    if isinstance(error, PoTokenRequired):
        return _Failure(
            8,
            "YouTube asked for an extra security check (a PO token) before it sends this video's "
            "captions, and this tool cannot pass it.\n"
            "What you can do: try again later, or use the copy-paste prompt in prompt.md.",
        )
    if isinstance(error, (requests.exceptions.RequestException, YouTubeRequestFailed)):
        return _Failure(
            7,
            "Could not reach YouTube.\n"
            "What you can do: check your internet connection and try again.",
        )
    if isinstance(error, YouTubeTranscriptApiException):
        return _Failure(
            8,
            f"YouTube sent an answer this tool did not expect ({type(error).__name__}).\n"
            "What you can do: try again later, or use the copy-paste prompt in prompt.md.",
        )
    raise error


def _fetch(link: str, chunk: int, api, title_fetcher: Callable) -> str:
    video_id, start = parse_link(link)
    if api is None:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
    transcript = choose_transcript(api.list(video_id))
    fetched = transcript.fetch()
    chunks = chunk_blocks(build_blocks(fetched.snippets))
    if not chunks:
        raise EmptyCaptions(transcript.language_code)
    if not 1 <= chunk <= len(chunks):
        raise _Failure(
            2,
            f"Chunk {chunk} does not exist. This video has {len(chunks)} chunk(s).\n"
            f"What you can do: use a number from 1 to {len(chunks)}.",
        )
    return render(
        video_id,
        title_fetcher(video_id),
        transcript.is_generated,
        transcript.language_code,
        start,
        chunks,
        chunk,
    )


def main(argv: Sequence[str] | None = None, api=None, title_fetcher: Callable = fetch_title) -> int:
    parser = argparse.ArgumentParser(
        description="Print the English captions of a YouTube video with [mm:ss] markers."
    )
    parser.add_argument("link", help="a YouTube link or video id")
    parser.add_argument("--chunk", type=int, default=1, help="which chunk to print (default 1)")
    args = parser.parse_args(argv)
    try:  # the library imports requests too, so this checks both
        import youtube_transcript_api  # noqa: F401
    except ImportError:
        print(
            "The youtube-transcript-api library is not installed, so the fetcher cannot run.\n"
            "What you can do: run the one-line install from the setup guide (Step 4), then try "
            "again.",
            file=sys.stderr,
        )
        return 9
    try:
        text = _fetch(args.link, args.chunk, api, title_fetcher)
    except _Failure as failure:
        print(failure.message, file=sys.stderr)
        return failure.code
    except Exception as error:  # expected failures are explained, anything else re-raises
        failure = _explain(error)
        print(failure.message, file=sys.stderr)
        return failure.code
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
