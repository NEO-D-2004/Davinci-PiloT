"""
DaVinci Resolve API Wrappers Module.
Provides safe, robust methods to query ProjectManager, CurrentProject, CurrentTimeline, and MediaPool.
Ref: https://extremraym.com/cloud/resolve-scripting-doc/#davinci-resolve-api
"""

from typing import Optional, Dict, Any, List
from app.models.resolve_models import ProjectInfo, TimelineInfo, MediaPoolInfo, ResolveState
from app.services.logger_service import app_logger


class ResolveApiWrapper:
    """Safe wrapper for DaVinci Resolve Scripting API calls."""

    def __init__(self, resolve_handle: Any = None) -> None:
        self.resolve = resolve_handle

    def set_handle(self, resolve_handle: Any) -> None:
        self.resolve = resolve_handle

    def get_version(self) -> str:
        """Get DaVinci Resolve version string."""
        if not self.resolve:
            return "Disconnected"
        try:
            ver = self.resolve.GetVersion()
            if isinstance(ver, list):
                return ".".join(str(v) for v in ver)
            return str(ver)
        except Exception as e:
            app_logger.warning(f"Failed to get Resolve version: {e}")
            return "Unknown"

    def get_product_name(self) -> str:
        """Get product name (e.g. DaVinci Resolve Studio)."""
        if not self.resolve:
            return "DaVinci Resolve"
        try:
            return self.resolve.GetProductName()
        except Exception:
            return "DaVinci Resolve"

    def get_project_manager(self) -> Optional[Any]:
        """Get ProjectManager handle."""
        if not self.resolve:
            return None
        try:
            return self.resolve.GetProjectManager()
        except Exception as e:
            app_logger.error(f"Error fetching ProjectManager: {e}")
            return None

    def query_project_info(self) -> ProjectInfo:
        """Query active project metadata."""
        pm = self.get_project_manager()
        if not pm:
            return ProjectInfo()

        try:
            project = pm.GetCurrentProject()
            if not project:
                return ProjectInfo(name="No Project Open", is_loaded=False)

            name = project.GetName() or "Untitled Project"
            width = project.GetSetting("timelineResolutionWidth") or "1920"
            height = project.GetSetting("timelineResolutionHeight") or "1080"
            frame_rate = project.GetSetting("timelineFrameRate") or "24"
            timelines_count = project.GetTimelineCount() or 0

            return ProjectInfo(
                name=name,
                resolution=f"{width}x{height}",
                frame_rate=f"{frame_rate} fps",
                timelines_count=timelines_count,
                is_loaded=True
            )
        except Exception as e:
            app_logger.error(f"Error querying active project info: {e}")
            return ProjectInfo(name="Query Error", is_loaded=False)

    def query_timeline_info(self) -> TimelineInfo:
        """Query active timeline metadata."""
        pm = self.get_project_manager()
        if not pm:
            return TimelineInfo()

        try:
            project = pm.GetCurrentProject()
            if not project:
                return TimelineInfo()

            timeline = project.GetCurrentTimeline()
            if not timeline:
                return TimelineInfo(name="No Active Timeline", is_active=False)

            name = timeline.GetName() or "Untitled Timeline"
            start_tc = timeline.GetStartFrame() or 0
            video_tracks = timeline.GetTrackCount("video") or 0
            audio_tracks = timeline.GetTrackCount("audio") or 0

            # Calculate total clips across video tracks
            total_clips = 0
            for i in range(1, video_tracks + 1):
                items = timeline.GetItemListInTrack("video", i) or []
                total_clips += len(items)

            return TimelineInfo(
                name=name,
                start_timecode=str(start_tc),
                video_tracks_count=video_tracks,
                audio_tracks_count=audio_tracks,
                total_clips=total_clips,
                is_active=True
            )
        except Exception as e:
            app_logger.error(f"Error querying timeline info: {e}")
            return TimelineInfo(name="Query Error", is_active=False)

    def query_media_pool_info(self) -> MediaPoolInfo:
        """Query Media Pool metadata."""
        pm = self.get_project_manager()
        if not pm:
            return MediaPoolInfo()

        try:
            project = pm.GetCurrentProject()
            if not project:
                return MediaPoolInfo()

            media_pool = project.GetMediaPool()
            if not media_pool:
                return MediaPoolInfo()

            root_folder = media_pool.GetRootFolder()
            if not root_folder:
                return MediaPoolInfo()

            subfolders = root_folder.GetSubFolderList() or []
            clips = root_folder.GetClipList() or []

            return MediaPoolInfo(
                root_folder_name=root_folder.GetName() or "Master",
                subfolders_count=len(subfolders),
                total_clips_count=len(clips)
            )
        except Exception as e:
            app_logger.error(f"Error querying media pool info: {e}")
            return MediaPoolInfo()

    def query_full_state(self) -> ResolveState:
        """Query aggregated Resolve state."""
        if not self.resolve:
            return ResolveState(is_connected=False, error_message="Resolve not connected")

        version = self.get_version()
        product = self.get_product_name()
        project = self.query_project_info()
        timeline = self.query_timeline_info()
        media_pool = self.query_media_pool_info()

        return ResolveState(
            is_connected=True,
            resolve_version=version,
            product_name=product,
            project=project,
            timeline=timeline,
            media_pool=media_pool
        )
