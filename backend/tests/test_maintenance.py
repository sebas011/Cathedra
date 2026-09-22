from pathlib import Path

from app.api import maintenance


def test_status_backup_and_csv_exports(client, monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(maintenance, "BACKUP_DIR", tmp_path / "backups")

    status = client.get("/api/v1/maintenance/status")
    assert status.status_code == 200
    assert status.json()["database_status"] == "healthy"
    assert status.json()["backup_count"] == 0

    backup = client.post("/api/v1/maintenance/backups")
    assert backup.status_code == 201
    backup_file = maintenance.BACKUP_DIR / backup.json()["filename"]
    assert backup_file.exists()
    assert backup.json()["size_bytes"] == backup_file.stat().st_size

    refreshed_status = client.get("/api/v1/maintenance/status")
    assert refreshed_status.json()["backup_count"] == 1

    restored = client.post("/api/v1/maintenance/restore", json={"filename": backup.json()["filename"]})
    assert restored.status_code == 200
    assert (maintenance.BACKUP_DIR / restored.json()["safety_backup"]).exists()

    for endpoint, heading in (
        ("/api/v1/maintenance/exports/fsdp.csv", "Scholar ID,"),
        ("/api/v1/maintenance/exports/faculty-profiles.csv", "Faculty ID,"),
        ("/api/v1/maintenance/exports/workloads.csv", "Workload ID,"),
    ):
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert response.text.startswith(heading)
