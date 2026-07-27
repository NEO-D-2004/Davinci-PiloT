"""
Unit tests for DaVinci Resolve Service & Connector.
"""

from unittest.mock import MagicMock
from app.models.resolve_models import ProjectInfo, TimelineInfo, MediaPoolInfo, ResolveState
from app.automation.resolve_api import ResolveApiWrapper
from app.services.resolve_service import ResolveService


def test_resolve_models():
    project = ProjectInfo(name="Demo Project", resolution="1920x1080", frame_rate="24.0 fps", timelines_count=2, is_loaded=True)
    assert project.name == "Demo Project"
    assert project.resolution == "1920x1080"

    timeline = TimelineInfo(name="Main Timeline", video_tracks_count=2, audio_tracks_count=4, total_clips=15, is_active=True)
    assert timeline.name == "Main Timeline"
    assert timeline.total_clips == 15

    media_pool = MediaPoolInfo(root_folder_name="Master", total_clips_count=25)
    assert media_pool.total_clips_count == 25

    state = ResolveState(is_connected=True, project=project, timeline=timeline, media_pool=media_pool)
    assert state.is_connected is True
    assert state.project.name == "Demo Project"


def test_resolve_api_wrapper_disconnected():
    wrapper = ResolveApiWrapper(resolve_handle=None)
    assert wrapper.get_version() == "Disconnected"
    assert wrapper.get_product_name() == "DaVinci Resolve"
    
    project = wrapper.query_project_info()
    assert project.is_loaded is False
    
    timeline = wrapper.query_timeline_info()
    assert timeline.is_active is False


def test_resolve_api_wrapper_mocked():
    mock_resolve = MagicMock()
    mock_resolve.GetVersion.return_value = "19.0.0"
    mock_resolve.GetProductName.return_value = "DaVinci Resolve Studio"

    mock_pm = MagicMock()
    mock_resolve.GetProjectManager.return_value = mock_pm

    mock_proj = MagicMock()
    mock_pm.GetCurrentProject.return_value = mock_proj
    mock_proj.GetName.return_value = "Test Movie"
    mock_proj.GetSetting.side_effect = lambda key: {"timelineResolutionWidth": "3840", "timelineResolutionHeight": "2160", "timelineFrameRate": "60"}.get(key, "")
    mock_proj.GetTimelineCount.return_value = 3

    mock_tl = MagicMock()
    mock_proj.GetCurrentTimeline.return_value = mock_tl
    mock_tl.GetName.return_value = "Final Cut"
    mock_tl.GetStartFrame.return_value = 0
    mock_tl.GetTrackCount.side_effect = lambda track_type: 2 if track_type == "video" else 4
    mock_tl.GetItemListInTrack.return_value = [MagicMock(), MagicMock(), MagicMock()]

    wrapper = ResolveApiWrapper(resolve_handle=mock_resolve)
    state = wrapper.query_full_state()

    assert state.is_connected is True
    assert state.resolve_version == "19.0.0"
    assert state.product_name == "DaVinci Resolve Studio"
    assert state.project.name == "Test Movie"
    assert state.project.resolution == "3840x2160"
    assert state.timeline.name == "Final Cut"
    assert state.timeline.total_clips == 6  # 2 video tracks * 3 items
