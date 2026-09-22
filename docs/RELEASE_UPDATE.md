# Cathedra Release Update Checklist

Use this when installing a newer Cathedra release on the office PC.

## Before updating

1. In Cathedra, create a backup from **Backup & Export**.
2. Close Cathedra completely.
3. Confirm that the incoming release folder contains `Cathedra.exe`.
4. Keep the incoming folder separate from the installed application folder.

## Apply the update

Run the included `desktop\update-release.ps1` helper with the incoming and installed folders. It retains the old application folder beside the installation with a timestamped name, and it leaves the office database and backup folder untouched.

```powershell
.\desktop\update-release.ps1 -NewReleaseFolder 'C:\Incoming\Cathedra' -InstalledFolder 'C:\Cathedra'
```

Then start `Cathedra.exe` from the installed folder. Sign in and check the dashboard, faculty profiles, and **Backup & Export**.

## If a problem appears

1. Close Cathedra.
2. Rename the current installed `Cathedra` folder to another name.
3. Rename the timestamped `Cathedra.previous-...` folder back to `Cathedra`.
4. Start Cathedra again.

This rolls back the application files only. Office records remain under `%LOCALAPPDATA%\Cathedra` throughout the process.
