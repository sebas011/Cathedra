"""Cathedra's Windows desktop launcher entry point for PyInstaller."""

import argparse
import ctypes
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


APP_NAME = "Cathedra"
DEFAULT_PORT = 8100


def resource_path(*parts: str) -> Path:
    """Find a file from either a PyInstaller bundle or the source checkout."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return root.joinpath(*parts)


def writable_data_directory(override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_app_data / APP_NAME


def prepare_data_directory(data_directory: Path) -> None:
    data_directory.mkdir(parents=True, exist_ok=True)
    active_database = data_directory / "cathedra.db"
    if active_database.exists():
        return
    bundled_database = resource_path("backend", "scholardesk_v2_dev.db")
    if not bundled_database.exists():
        raise RuntimeError("The bundled Cathedra database could not be found.")
    shutil.copy2(bundled_database, active_database)


def service_is_ready(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/health", timeout=1) as response:
            return response.status == 200
    except OSError:
        return False


def wait_for_service(port: int, timeout_seconds: int = 20) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if service_is_ready(port):
            return True
        time.sleep(0.25)
    return False


def port_is_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) != 0


def show_error(message: str) -> None:
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(None, message, APP_NAME, 0x10)
    else:
        print(message, file=sys.stderr)


def write_startup_error(message: str) -> None:
    data_directory = Path(os.environ.get("CATHEDRA_DATA_DIR", writable_data_directory(None)))
    try:
        data_directory.mkdir(parents=True, exist_ok=True)
        (data_directory / "launcher-error.log").write_text(message, encoding="utf-8")
    except OSError:
        pass


def open_app_window(url: str) -> None:
    edge_locations = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
    ]
    edge = next((candidate for candidate in edge_locations if candidate.exists()), None)
    if edge:
        subprocess.Popen([str(edge), f"--app={url}", "--new-window"])
    else:
        webbrowser.open_new(url)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch Cathedra as a local desktop application.")
    parser.add_argument("--data-dir", help="Override the writable Cathedra data folder.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Local-only port for the Cathedra service.")
    parser.add_argument("--no-browser", action="store_true", help="Start the local service without opening a window.")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    data_directory = writable_data_directory(arguments.data_dir)
    prepare_data_directory(data_directory)
    os.environ["CATHEDRA_DATA_DIR"] = str(data_directory)
    os.environ["CATHEDRA_FRONTEND_DIST"] = str(resource_path("frontend", "dist"))
    backend_root = resource_path("backend")
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    import uvicorn
    from app.main import app

    url = f"http://127.0.0.1:{arguments.port}"
    if not service_is_ready(arguments.port):
        if not port_is_available(arguments.port):
            show_error(f"Port {arguments.port} is already in use by another application.")
            raise SystemExit(1)
        configuration = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=arguments.port,
            log_config=None,
            access_log=False,
        )
        server = uvicorn.Server(configuration)
        threading.Thread(target=server.run, daemon=True).start()
        if not wait_for_service(arguments.port):
            show_error("Cathedra could not start its local service.")
            raise SystemExit(1)

    if not arguments.no_browser:
        open_app_window(url)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as caught:
        message = f"Cathedra could not start.\n\n{caught}"
        write_startup_error(message)
        show_error(message)
        raise
