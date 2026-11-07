from fastapi.testclient import TestClient
from kodra.server.app import app
from kodra.config import settings

client = TestClient(app)


def test_root_and_health(tmp_path):
    settings.set_workspace(tmp_path)
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["name"] == "Kodra Agent"

    res_h = client.get("/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"


def test_workspace_and_project_endpoints(tmp_path):
    settings.set_workspace(tmp_path)
    (tmp_path / "main.py").write_text("print('test')", encoding="utf-8")

    res = client.get("/workspace")
    assert res.status_code == 200
    assert res.json()["files_count"] >= 1

    res_p = client.get("/project")
    assert res_p.status_code == 200
    assert "main.py" in res_p.json()["files"]


def test_file_read_write(tmp_path):
    settings.set_workspace(tmp_path)
    # Write file
    write_res = client.post("/file", json={"path": "demo.py", "content": "x = 42\n"})
    assert write_res.status_code == 200
    assert (tmp_path / "demo.py").exists()

    # Read file
    read_res = client.get("/file?path=demo.py")
    assert read_res.status_code == 200
    assert read_res.json()["content"] == "x = 42\n"


def test_plan_generate_execute_lifecycle(tmp_path):
    settings.set_workspace(tmp_path)
    # 1. Generate plan
    plan_res = client.post(
        "/plan",
        json={"task": "Create greeting utility in greet.py", "multi_agent": False},
    )
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert len(plan_data["steps"]) >= 1

    # 2. Validate plan
    val_res = client.post("/plan/validate", json=plan_data)
    assert val_res.status_code == 200
    assert val_res.json()["valid"] is True

    # 3. Execute plan
    exec_res = client.post(
        "/plan/execute",
        json={"plan": plan_data, "auto_approve": True},
    )
    assert exec_res.status_code == 200
    assert exec_res.json()["result"]["success"] is True
    assert (tmp_path / "greet.py").exists()

    # 4. Check history
    hist_res = client.get("/history")
    assert hist_res.status_code == 200
    assert len(hist_res.json()["history"]) >= 1
