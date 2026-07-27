"""
Unit tests for Milestone 3 Timeline Explorer models, parser, and view components.
"""

from app.models.timeline_models import ClipItem, TrackInfo, TimelineMarker, TimelineStructure
from app.automation.bridge_server import parse_timeline_structure
from app.ui.views.timeline_view import TimelineView


def test_timeline_models():
    marker = TimelineMarker(frame=100, timecode="01:00:04:04", color="Blue", name="Scene Start", note="Check color grade")
    assert marker.frame == 100
    assert marker.color == "Blue"
    assert marker.to_dict()["name"] == "Scene Start"

    clip1 = ClipItem(
        clip_id="v_1_1",
        name="A001_C001.mov",
        track_type="video",
        track_index=1,
        start_frame=0,
        end_frame=120,
        duration_frames=120,
        source_path="C:/Media/A001_C001.mov",
        flag_color="Red",
        markers=[marker]
    )
    assert clip1.name == "A001_C001.mov"
    assert clip1.duration_frames == 120
    assert len(clip1.markers) == 1

    clip2 = ClipItem(
        clip_id="v_1_2",
        name="A001_C002.mov",
        track_type="video",
        track_index=1,
        start_frame=120,
        end_frame=240,
        duration_frames=120,
        source_path="C:/Media/A001_C002.mov"
    )

    track_v1 = TrackInfo(track_type="video", track_index=1, name="Video 1", clips=[clip1, clip2])
    assert track_v1.total_clips == 2

    struct = TimelineStructure(
        name="Main Commercial Edit",
        fps=24.0,
        video_tracks=[track_v1],
        audio_tracks=[],
        markers=[marker]
    )

    assert struct.total_video_clips == 2
    assert struct.total_audio_clips == 0
    assert struct.total_clips == 2
    assert len(struct.get_all_clips()) == 2
    assert struct.to_dict()["name"] == "Main Commercial Edit"


def test_parse_timeline_structure_json():
    raw_json = {
        "name": "Test Timeline",
        "start_timecode": "01:00:00:00",
        "duration_frames": 300,
        "duration_timecode": "00:00:12:12",
        "fps": 24.0,
        "video_tracks": [
            {
                "track_type": "video",
                "track_index": 1,
                "name": "Video 1",
                "clips": [
                    {
                        "clip_id": "v_1_1",
                        "name": "Intro.mp4",
                        "track_type": "video",
                        "track_index": 1,
                        "start_frame": 0,
                        "end_frame": 100,
                        "duration_frames": 100,
                        "source_path": "C:/Intro.mp4",
                        "flag_color": "Blue",
                        "markers": []
                    }
                ]
            }
        ],
        "audio_tracks": [],
        "markers": [
            {
                "frame": 50,
                "timecode": "01:00:02:02",
                "color": "Green",
                "name": "Audio Cue",
                "note": "Fade music",
                "duration": 1
            }
        ]
    }

    struct = parse_timeline_structure(raw_json)
    assert struct.name == "Test Timeline"
    assert struct.total_clips == 1
    assert struct.video_tracks[0].clips[0].name == "Intro.mp4"
    assert len(struct.markers) == 1
    assert struct.markers[0].color == "Green"


def test_timeline_view_instantiation(qtbot):
    view = TimelineView()
    qtbot.addWidget(view)

    assert view.summary_lbl.text() == "Timeline: None | 0 Clips (0V / 0A)"
    assert view.clips_table.rowCount() == 0

    # Test update structure
    struct = TimelineStructure(
        name="Demo Edit",
        fps=30.0,
        video_tracks=[
            TrackInfo(
                track_type="video",
                track_index=1,
                name="V1",
                clips=[ClipItem(clip_id="v1", name="Clip_01.mp4", track_type="video", track_index=1, start_frame=0, end_frame=60, duration_frames=60)]
            )
        ]
    )

    view.update_timeline_structure(struct)
    assert "Demo Edit" in view.summary_lbl.text()
    assert view.clips_table.rowCount() == 1
    assert view.clips_table.item(0, 0).text() == "Clip_01.mp4"
