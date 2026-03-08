from telecom_browser_mcp.models.common import ToolResponse


def test_tool_response_contract_version_required() -> None:
    response = ToolResponse(ok=True, tool="x")
    dumped = response.model_dump(mode="json")
    assert dumped["meta"]["contract_version"] == "v1"
    assert dumped["tool"] == "x"
    assert dumped["ok"] is True
