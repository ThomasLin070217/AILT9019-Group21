import pytest

from scripts.check_submission import validate_text, youtube_id


@pytest.mark.parametrize("url", ["https://youtu.be/abcdefghijk", "https://www.youtube.com/watch?v=abcdefghijk&t=2", "https://youtube.com/live/abcdefghijk"])
def test_extract_video_identity(url):
    assert youtube_id(url) == "abcdefghijk"


@pytest.mark.parametrize("url", ["PENDING", "https://youtube.com/watch", "https://youtube.com/@group21", "https://youtube.com/playlist?list=abcdefghijk", "https://youtu.be/short", "https://youtube.com.evil.example/watch?v=abcdefghijk", "https://user:password@youtube.com/watch?v=abcdefghijk"])
def test_reject_nonvideo_or_unsafe_links(url):
    with pytest.raises(ValueError):
        youtube_id(url)


def links(a, b):
    return f"Team ID: Group 21\nPublic project webpage: https://thomaslin070217.github.io/AILT9019-Group21/\nGitHub repository: https://github.com/ThomasLin070217/AILT9019-Group21\nPresentation YouTube link: {a}\nDemo YouTube link: {b}"


def test_aliases_for_one_video_do_not_satisfy_two_video_requirement():
    body = links("https://youtu.be/abcdefghijk", "https://www.youtube.com/watch?v=abcdefghijk")
    assert any("different videos" in e for e in validate_text(body, body, 5))


def test_two_urls_must_appear_in_report_and_body_must_fit():
    body = links("https://youtu.be/abcdefghijk", "https://youtu.be/lmnopqrstuv")
    assert validate_text(body, body, 5) == []
    assert len(validate_text(body, "No links", 6)) == 3
