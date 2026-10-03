"""Offline tests for the fetcher's error messages and exit codes: a fake caption API, no network."""

import sys

import pytest
import requests
import youtube_transcript_api as yta

from conftest import snippets_from
from fetch_transcript import main

VID = "dQw4w9WgXcQ"
LINK = f"https://youtu.be/{VID}"


class FakeFetched:
    def __init__(self, snippets):
        self.snippets = snippets


class FakeTranscript:
    def __init__(self, language_code, is_generated, snippets):
        self.video_id = VID
        self.language = language_code
        self.language_code = language_code
        self.is_generated = is_generated
        self._snippets = snippets

    def fetch(self):
        return FakeFetched(self._snippets)


class FakeTranscriptList:
    def __init__(self, transcripts):
        self.transcripts = transcripts

    def __iter__(self):
        manual = [t for t in self.transcripts if not t.is_generated]
        generated = [t for t in self.transcripts if t.is_generated]
        return iter(manual + generated)

    def _find(self, codes, generated):
        for code in codes:
            for transcript in self.transcripts:
                if transcript.language_code == code and transcript.is_generated == generated:
                    return transcript
        raise yta.NoTranscriptFound(VID, codes, self)

    def find_manually_created_transcript(self, codes):
        return self._find(codes, False)

    def find_generated_transcript(self, codes):
        return self._find(codes, True)


class FakeApi:
    """Stands in for YouTubeTranscriptApi: returns a caption list or raises an error."""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def list(self, video_id):
        self.calls.append(video_id)
        if self.error is not None:
            raise self.error
        return self.result


def no_title(video_id):
    return None


CASES = [
    (yta.TranscriptsDisabled(VID), 3, "no captions"),
    (yta.VideoUnavailable(VID), 4, "removed or does not exist"),
    (yta.AgeRestricted(VID), 5, "age-restricted"),
    (yta.IpBlocked(VID), 6, "blocking caption requests"),
    (yta.RequestBlocked(VID), 6, "blocking caption requests"),
    (requests.exceptions.ConnectionError("down"), 7, "reach YouTube"),
    (yta.PoTokenRequired(VID), 8, "PO token"),
]


@pytest.mark.parametrize(("error", "code", "phrase"), CASES)
def test_each_failure_has_a_plain_message(error, code, phrase, capsys):
    assert main([LINK], api=FakeApi(error=error), title_fetcher=no_title) == code
    out = capsys.readouterr()
    assert out.out == ""
    assert phrase in out.err
    assert "What you can do:" in out.err
    assert "Traceback" not in out.err


def test_blocked_message_says_no_workaround(capsys):
    main([LINK], api=FakeApi(error=yta.IpBlocked(VID)), title_fetcher=no_title)
    err = capsys.readouterr().err
    assert "YouTube is blocking caption requests from this network." in err
    assert "does not use proxies" in err


def test_po_token_is_not_reported_as_a_network_block(capsys):
    main([LINK], api=FakeApi(error=yta.PoTokenRequired(VID)), title_fetcher=no_title)
    err = capsys.readouterr().err
    assert "YouTube asked for an extra security check (a PO token)" in err
    assert "blocking caption requests" not in err


def test_bad_link_exits_2_without_calling_youtube(capsys):
    api = FakeApi(error=AssertionError("must not be called"))
    assert main(["https://vimeo.com/123"], api=api, title_fetcher=no_title) == 2
    assert api.calls == []
    assert "not a YouTube video link" in capsys.readouterr().err


def test_missing_library_exits_9_with_a_plain_message(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "youtube_transcript_api", None)
    assert main([LINK], title_fetcher=no_title) == 9
    out = capsys.readouterr()
    assert out.out == ""
    assert "The youtube-transcript-api library is not installed" in out.err
    assert "Traceback" not in out.err


def test_captions_print_and_exit_0(manual_rows, capsys):
    transcripts = FakeTranscriptList([FakeTranscript("en", False, snippets_from(manual_rows))])
    assert main([LINK], api=FakeApi(result=transcripts), title_fetcher=no_title) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"VIDEO_ID: {VID}\n")
    assert "CAPTIONS: manual (en)" in out
