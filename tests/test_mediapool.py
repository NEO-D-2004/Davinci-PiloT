"""
Unit tests for Milestone 4 Media Pool & Asset Manager models, parser, and view components.
"""

from app.models.mediapool_models import MediaAsset, MediaBin, MediaPoolStructure
from app.automation.bridge_server import parse_mediapool_structure
from app.ui.views.mediapool_view import MediaPoolView


def test_mediapool_models():
    asset1 = MediaAsset(
        media_id="m_1",
        name="Interview_A01.mov",
        asset_type="Video",
        file_path="C:/Project/Footage/Interview_A01.mov",
        resolution="3840x2160",
        fps="23.976",
        duration="00:05:12:00",
        video_codec="ProRes 422 HQ",
        audio_codec="PCM",
        good_take=True,
        scene="10",
        shot="1A",
        take="2"
    )
    assert asset1.name == "Interview_A01.mov"
    assert asset1.resolution == "3840x2160"
    assert asset1.good_take is True
    assert asset1.to_dict()["scene"] == "10"

    asset2 = MediaAsset(
        media_id="m_2",
        name="Background_Music.wav",
        asset_type="Audio",
        file_path="C:/Project/Audio/Background_Music.wav",
        duration="00:03:00:00",
        audio_codec="PCM",
        good_take=False
    )

    sub_bin = MediaBin(
        bin_id="b_audio",
        name="Audio Bins",
        folder_path="Master/Audio Bins",
        assets=[asset2]
    )

    root_bin = MediaBin(
        bin_id="b_master",
        name="Master",
        folder_path="Master",
        subfolders=[sub_bin],
        assets=[asset1]
    )

    struct = MediaPoolStructure(root_bin=root_bin)

    assert struct.total_assets == 2
    assert struct.total_video_assets == 1
    assert struct.total_audio_assets == 1
    assert struct.total_good_takes == 1
    assert len(struct.get_all_assets()) == 2
    assert struct.to_dict()["total_assets"] == 2


def test_parse_mediapool_structure_json():
    raw_json = {
        "root_bin": {
            "bin_id": "root",
            "name": "Master Bin",
            "folder_path": "Master",
            "assets": [
                {
                    "media_id": "asset_1",
                    "name": "Intro_Broll.mp4",
                    "asset_type": "Video",
                    "file_path": "D:/Footage/Intro_Broll.mp4",
                    "resolution": "1920x1080",
                    "fps": "29.97",
                    "duration": "00:00:15:00",
                    "video_codec": "H.264",
                    "audio_codec": "AAC",
                    "audio_channels": 2,
                    "good_take": True,
                    "scene": "1",
                    "shot": "1",
                    "take": "3"
                }
            ],
            "subfolders": []
        }
    }

    struct = parse_mediapool_structure(raw_json)
    assert struct.root_bin.name == "Master Bin"
    assert struct.total_assets == 1
    assert struct.total_video_assets == 1
    assert struct.total_good_takes == 1
    assert struct.get_all_assets()[0].name == "Intro_Broll.mp4"


def test_mediapool_view_instantiation(qtbot):
    view = MediaPoolView()
    qtbot.addWidget(view)

    assert "Master" in view.summary_lbl.text()
    assert view.asset_table.rowCount() == 0

    # Test updating structure
    asset = MediaAsset(
        media_id="a_100",
        name="Promo_Video.mp4",
        asset_type="Video",
        file_path="E:/Promo_Video.mp4",
        good_take=True
    )
    root_bin = MediaBin(name="Master", assets=[asset])
    struct = MediaPoolStructure(root_bin=root_bin)

    view.update_mediapool_structure(struct)

    assert view.asset_table.rowCount() == 1
    assert view.asset_table.item(0, 0).text() == "Promo_Video.mp4"
    assert view.asset_table.item(0, 7).text() == "⭐ Good Take"
