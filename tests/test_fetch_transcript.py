"""Offline tests for the caption fetcher: no network, made-up captions."""

import pytest

from conftest import snippets_from
from fetch_transcript import (
    LinkError,
    build_blocks,
    chunk_blocks,
    format_timestamp,
    parse_link,
    render,
    timestamp_link,
)

VID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    ("link", "start"),
    [
        (f"https://www.youtube.com/watch?v={VID}", None),
        (f"http://m.youtube.com/watch?v={VID}", None),
        (f"youtube.com/watch?v={VID}", None),
        (f"https://www.youtube.com/watch?feature=share&v={VID}", None),
        (f"https://youtu.be/{VID}", None),
        (f"https://youtu.be/{VID}?si=abcDEF123", None),
        (f"https://www.youtube.com/shorts/{VID}", None),
        (f"https://www.youtube.com/embed/{VID}", None),
        (f"https://www.youtube.com/live/{VID}", None),
        (VID, None),
        (f"  https://youtu.be/{VID}  ", None),
        (f"https://www.youtube.com/watch?v={VID}&t=90", 90),
        (f"https://youtu.be/{VID}?t=1m30s", 90),
        (f"https://youtu.be/{VID}?t=1h2m3s", 3723),
        (f"https://www.youtube.com/embed/{VID}?start=45", 45),
        (f"https://www.youtube.com/watch?v={VID}#t=2m5s", 125),
        (f"https://www.youtube.com/watch?v={VID}&t=abc", None),
    ],
)
def test_parse_link_accepts_common_forms(link, start):
    assert parse_link(link) == (VID, start)


@pytest.mark.parametrize(
    "link",
    [
        "",
        "   ",
        "not a link",
        "https://vimeo.com/123456789",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/playlist?list=PL123",
        f"https://example.com/watch?v={VID}",
        f"https://www.youtube.com/watch?v={VID}%0A",
    ],
)
def test_parse_link_rejects_what_is_not_a_video_link(link):
    with pytest.raises(LinkError):
        parse_link(link)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "00:00"),
        (5, "00:05"),
        (59.9, "00:59"),
        (61, "01:01"),
        (187, "03:07"),
        (3599, "59:59"),
        (3600, "1:00:00"),
        (3725, "1:02:05"),
        (36000, "10:00:00"),
    ],
)
def test_format_timestamp(seconds, expected):
    assert format_timestamp(seconds) == expected


def test_timestamp_link_uses_whole_seconds():
    assert timestamp_link(VID, 187.8) == f"https://www.youtube.com/watch?v={VID}&t=187s"
    assert timestamp_link(VID, 0) == f"https://www.youtube.com/watch?v={VID}&t=0s"


def test_build_blocks_start_about_every_30_seconds(manual_rows):
    blocks = build_blocks(snippets_from(manual_rows))
    starts = [start for start, _ in blocks]
    assert starts[0] == 0.0
    for earlier, later in zip(starts, starts[1:], strict=False):
        assert 30 <= later - earlier < 40
    assert " ".join(text for _, text in blocks) == " ".join(row["text"] for row in manual_rows)


def test_build_blocks_collapse_whitespace_and_drop_empty_text():
    rows = [
        {"text": "a\n  b", "start": 0.0},
        {"text": "", "start": 2.0},
        {"text": "c", "start": 4.0},
    ]
    assert build_blocks(snippets_from(rows)) == [(0.0, "a b c")]
    assert build_blocks([]) == []


def test_chunk_blocks_keeps_a_short_video_in_one_chunk(manual_rows):
    blocks = build_blocks(snippets_from(manual_rows))
    assert chunk_blocks(blocks) == [blocks]


def test_chunk_blocks_splits_on_block_boundaries(manual_rows):
    blocks = build_blocks(snippets_from(manual_rows))
    chunks = chunk_blocks(blocks, max_chars=200)
    assert len(chunks) > 1
    assert [block for chunk in chunks for block in chunk] == blocks


def test_chunk_blocks_puts_an_oversize_block_alone():
    blocks = [(0.0, "a" * 50), (30.0, "b" * 500), (60.0, "c" * 50)]
    assert chunk_blocks(blocks, max_chars=200) == [[blocks[0]], [blocks[1]], [blocks[2]]]


def test_render_first_and_last_chunk(manual_rows):
    chunks = chunk_blocks(build_blocks(snippets_from(manual_rows)), max_chars=200)
    total = len(chunks)
    first = render(VID, None, False, "en", None, chunks, 1)
    lines = first.splitlines()
    assert lines[:5] == [
        f"VIDEO_ID: {VID}",
        f"TITLE: YouTube video {VID}",
        f"URL: https://www.youtube.com/watch?v={VID}",
        "CAPTIONS: manual (en)",
        f"CHUNK: 1 of {total}",
    ]
    assert lines[6].startswith("[00:00] Welcome to ")
    assert lines[-1] == "NEXT: run again with --chunk 2"
    assert first.endswith("\n")
    last = render(VID, "A title", True, "en", 90, chunks, total)
    assert "TITLE: A title" in last
    assert "CAPTIONS: auto-generated (en)" in last
    assert "LINK_STARTS_AT: [01:30]" in last
    assert "NEXT:" not in last
