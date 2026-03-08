from telecom_browser_mcp.live_verification import classify_browser_failure


def test_browser_runtime_classifies_host_sandbox_constraint() -> None:
    message = (
        "TargetClosedError: [FATAL:sandbox_host_linux.cc:41] "
        "Check failed: . shutdown: Operation not permitted (1)"
    )
    assert classify_browser_failure(message) == "host_runtime_constraint"


def test_browser_runtime_classifies_missing_lib_dependency() -> None:
    message = "error while loading shared libraries: libnspr4.so: cannot open shared object file"
    assert classify_browser_failure(message) == "browser_dependency_missing"
