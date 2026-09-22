# Cathedra Desktop Release Guide

## What the office receives

Run `desktop\build-release.ps1` on the release workstation. It creates a self-contained `desktop\release\Cathedra` folder containing `Cathedra.exe`, the Python runtime, required libraries, the built frontend, and the initial Cathedra database.

Copy the entire `Cathedra` folder to the office PC. The office PC does not need Python or Node.js.

## First launch

1. Place the release folder somewhere the user can run applications, such as `C:\Cathedra`.
2. Double-click `Cathedra.exe`.
3. Cathedra starts a local-only service and opens a dedicated Edge app window. If Edge is unavailable, it opens the default browser.
4. On the first run, create the local administrator account. Use a memorable username and a password of at least 10 characters. This account can add staff accounts and restore backups.

The executable is built without a console window. It listens only on `127.0.0.1`, so the application is not exposed to other computers on the network.

## Where office data lives

On first launch, Cathedra copies its initial database to:

```text
%LOCALAPPDATA%\Cathedra\cathedra.db
```

This writable data folder also contains the `backups` directory used by **Backup & Export**. Replacing the application folder does not replace existing office data.

## Everyday backup and recovery

- Use **Backup & Export** to create a snapshot before major changes or at the end of the workday. Cathedra retains the newest 30 backups automatically.
- An administrator can select a backup and choose **Restore Selected Backup** from the same page. Cathedra verifies the selected file and saves a safety backup of the current records before restoring it.
- After a restore, sign in again if Cathedra asks you to do so. Restoring a very old backup can also restore its older local accounts.

## Release workstation prerequisites

Only the release workstation needs these tools:

- Python with the project backend virtual environment
- Node.js and npm
- Internet access the first time PyInstaller is installed

Run this from the project root:

```powershell
.\desktop\build-release.ps1
```

The script builds frontend assets, installs PyInstaller into `backend\.venv`, and produces the no-console Windows application folder.

## Validate a release

On a release workstation, use the launcher without opening a window:

```powershell
.\desktop\release\Cathedra\Cathedra.exe --no-browser
```

Then open `http://127.0.0.1:8100/api/v1/health` and expect `{"status":"ok"}`. Open `http://127.0.0.1:8100` to check that the built Cathedra interface is served by the local app.

## Updating Cathedra

Use the guided release helper rather than replacing files one at a time:

1. Close Cathedra on the office PC.
2. Keep the incoming `Cathedra` release folder separate from the installed folder.
3. On the release workstation or with an IT administrator, run:

   ```powershell
   .\desktop\update-release.ps1 -NewReleaseFolder 'C:\Incoming\Cathedra' -InstalledFolder 'C:\Cathedra'
   ```

4. The helper checks that the new folder is a valid Cathedra release, moves the old application folder to a timestamped `Cathedra.previous-...` folder, then copies the new version into place.
5. Launch `C:\Cathedra\Cathedra.exe`.

The helper never changes `%LOCALAPPDATA%\Cathedra`, so the office database and backups remain available. Keep the timestamped prior folder until the updated application has been checked. To roll back the application, close Cathedra, rename the current `Cathedra` folder, and rename the retained `Cathedra.previous-...` folder back to `Cathedra`.

## Important boundary

This desktop package does not read, copy, or change `C:\ScholarDesk` or its database. Cathedra’s data stays in `%LOCALAPPDATA%\Cathedra`.
