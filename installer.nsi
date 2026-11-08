; ============================================================
;  Leave Planner — Windows Installer
;  Built with NSIS (https://nsis.sourceforge.io)
;
;  Prerequisites:
;    1. Build the PyInstaller bundle first:
;         .venv\Scripts\pyinstaller.exe leave_planner.spec
;    2. Install NSIS, then compile this script:
;         makensis installer.nsi
;
;  Output: LeavePlannerSetup.exe
; ============================================================

!define APP_NAME        "Leave Planner"
!define APP_VERSION     "1.1.0"
!define APP_PUBLISHER   "DaveTheBomb"
!define APP_EXE         "LeavePlanner.exe"
!define APP_FOLDER      "LeavePlanner"
!define INSTALLER_NAME  "LeavePlannerSetup.exe"
!define INSTALL_DIR     "$PROGRAMFILES64\${APP_NAME}"
!define REG_KEY         "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

; ── General ──────────────────────────────────────────────────────────────────
Name              "${APP_NAME} ${APP_VERSION}"
OutFile           "${INSTALLER_NAME}"
InstallDir        "${INSTALL_DIR}"
InstallDirRegKey  HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor     /SOLID lzma
Unicode           True

; ── Pages ────────────────────────────────────────────────────────────────────
!include "MUI2.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON    "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON  "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Installer ────────────────────────────────────────────────────────────────
Section "Install" SecInstall

    SetOutPath "$INSTDIR"

    ; Copy the entire PyInstaller output folder
    File /r "dist\${APP_FOLDER}\*.*"

    ; ── Uninstaller ──────────────────────────────────────────────────────────
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; ── Registry: Add/Remove Programs entry ──────────────────────────────────
    WriteRegStr   HKLM "${REG_KEY}" "DisplayName"      "${APP_NAME}"
    WriteRegStr   HKLM "${REG_KEY}" "DisplayVersion"   "${APP_VERSION}"
    WriteRegStr   HKLM "${REG_KEY}" "Publisher"        "${APP_PUBLISHER}"
    WriteRegStr   HKLM "${REG_KEY}" "InstallLocation"  "$INSTDIR"
    WriteRegStr   HKLM "${REG_KEY}" "UninstallString"  '"$INSTDIR\Uninstall.exe"'
    WriteRegDWORD HKLM "${REG_KEY}" "NoModify"         1
    WriteRegDWORD HKLM "${REG_KEY}" "NoRepair"         1

    ; ── Start Menu shortcut ──────────────────────────────────────────────────
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut  "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
                    "$INSTDIR\${APP_EXE}"
    CreateShortcut  "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" \
                    "$INSTDIR\Uninstall.exe"

    ; ── Desktop shortcut (always created) ───────────────────────────────────
    CreateShortcut  "$DESKTOP\${APP_NAME}.lnk" \
                    "$INSTDIR\${APP_EXE}"

SectionEnd

; ── Uninstaller ──────────────────────────────────────────────────────────────
Section "Uninstall"

    ; Remove installed files
    RMDir /r "$INSTDIR"

    ; Remove Start Menu entries
    RMDir /r "$SMPROGRAMS\${APP_NAME}"

    ; Remove Desktop shortcut
    Delete "$DESKTOP\${APP_NAME}.lnk"

    ; Remove registry entry
    DeleteRegKey HKLM "${REG_KEY}"

SectionEnd
