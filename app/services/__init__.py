from .logger_service import LoggerService, logger_service, app_logger

__all__ = ["LoggerService", "logger_service", "app_logger", "ResolveService", "resolve_service"]


def __getattr__(name: str):
    if name == "ResolveService":
        from .resolve_service import ResolveService
        return ResolveService
    elif name == "resolve_service":
        from .resolve_service import resolve_service
        return resolve_service
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
