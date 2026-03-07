import platform


class EnvironmentInspector:
    def get_snapshot(self, session) -> dict:
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "session_environment_classification": session.environment_classification,
            "headless": session.headless,
            "browser_type": session.browser_type,
        }
