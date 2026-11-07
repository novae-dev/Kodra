from kodra.memory.project_memory import ProjectMemoryManager


def test_project_memory_initialization_and_persistence(tmp_path):
    # Create fake package.json and python file
    (tmp_path / "package.json").write_text('{"dependencies": {"react": "^19.0.0"}}', encoding="utf-8")
    (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")

    mgr = ProjectMemoryManager(tmp_path)
    cfg = mgr.get_config()

    assert "React" in cfg.tech_stack
    assert "Python" in cfg.tech_stack
    assert (tmp_path / "kodra.json").exists()

    # Record task history
    mgr.record_task_history(
        task="Create login page",
        plan_id="plan-123",
        success=True,
        summary="Created Login.tsx",
        files_modified=["Login.tsx"],
    )

    # Re-instantiate from disk
    mgr2 = ProjectMemoryManager(tmp_path)
    cfg2 = mgr2.get_config()
    assert len(cfg2.history) == 1
    assert cfg2.history[0]["task"] == "Create login page"
    assert cfg2.history[0]["files_modified"] == ["Login.tsx"]
