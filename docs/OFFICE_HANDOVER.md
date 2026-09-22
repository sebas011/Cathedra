# Cathedra Office Handover

Use this guide for the everyday operation of Cathedra on the office computer.

## The essentials

- Start Cathedra by double-clicking `Cathedra.exe`.
- Cathedra is local to this computer. It does not share its records over the network.
- The office database and its backups are kept separately from the application, under `%LOCALAPPDATA%\Cathedra`.
- Do not edit, move, or delete files in that folder manually.

## Daily work

1. Sign in with your local Cathedra account.
2. Use **FSDP**, **Faculty Profile**, and **Faculty Workload** to maintain records.
3. Use the search box and page controls when reviewing long lists.
4. Select **Print This Page** when a clean printed summary is needed.

Staff can add and edit records. Administrators can also delete records, manage accounts, restore backups, and view activity history.

## Daily backup

1. Open **Backup & Export**.
2. Confirm that the database status says **Healthy**.
3. Select **Create Backup**.
4. Wait for the confirmation message before closing Cathedra.

Cathedra retains the newest 30 backups automatically. Use the CSV download buttons on the same page when a spreadsheet copy is needed.

## Restore a backup

Only an administrator should restore records.

1. Open **Backup & Export**.
2. Select the backup by its date and time.
3. Select **Restore Selected Backup** and confirm the choice.
4. Sign in again if Cathedra asks you to.

Cathedra checks the selected backup and makes a safety backup of the current records before it restores anything.

## Accounts and passwords

- Each person should use their own local account.
- Use **Account Security** to change your own password.
- An administrator can set a temporary password for another person. That person should change it after signing in.
- Use **Activity History** to review successful changes made by local accounts.

## Installing an update

1. Create a backup from **Backup & Export**.
2. Close Cathedra.
3. Have the release administrator use the update helper described in [RELEASE_UPDATE.md](RELEASE_UPDATE.md).
4. Open Cathedra and check the dashboard and **Backup & Export**.

The update process replaces application files only. It keeps the office database and backups intact.

## If something looks wrong

1. Stop entering new records.
2. Create a backup if Cathedra is still working.
3. Note what page was open and what action was being taken.
4. Ask the local administrator to review **Activity History**, restore a known-good backup if necessary, or return to the previous application version using the update guide.

## Important boundary

Cathedra is separate from the old ScholarDesk installation. Do not copy, replace, or edit `C:\ScholarDesk` or its database while using Cathedra.
