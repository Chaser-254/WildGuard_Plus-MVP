import time
import os
from app.services.stream_service import get_stream_manager


def test_add_and_remove_stream():
    manager = get_stream_manager()
    sid = 'test_stream'
    # use a local sample video or an invalid url - worker will attempt to open
    url = '/path/does/not/exist.mp4'

    # Add stream
    added = manager.add_stream(sid, url, interval=1.0, use_mock=True)
    assert added is True

    streams = manager.list_streams()
    assert any(s['id'] == sid for s in streams)

    # Remove stream
    removed = manager.remove_stream(sid)
    assert removed is True

    streams = manager.list_streams()
    assert not any(s['id'] == sid for s in streams)


if __name__ == '__main__':
    test_add_and_remove_stream()
    print('stream test passed')
