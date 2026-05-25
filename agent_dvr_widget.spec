# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Agent DVR Widget (PyQt6 + WebEngine, taille réduite)

import os

block_cipher = None

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
ICON_FILE = os.path.join(SPEC_DIR, "assets", "camera.ico")

EXCLUDE_MODULES = [
    "PyQt6.QtQuick",
    "PyQt6.QtQml",
    "PyQt6.QtQuick3D",
    "PyQt6.QtQuickWidgets",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtPdf",
    "PyQt6.QtPdfWidgets",
    "PyQt6.QtBluetooth",
    "PyQt6.QtNfc",
    "PyQt6.QtPositioning",
    "PyQt6.QtLocation",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSql",
    "PyQt6.QtTest",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtOpenGLWidgets",
    "PyQt6.QtWebEngineQuick",
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "PIL",
    "tkinter",
]

EXCLUDE_DLL_FRAGMENTS = (
    "Qt6Quick3D",
    "Qt6QuickControls",
    "Qt6QuickTemplates",
    "Qt6QuickDialogs",
    "Qt6QuickEffects",
    "Qt6QuickParticles",
    "Qt6QuickShapes",
    "Qt6QuickVectorImage",
    "Qt6QuickTimeline",
    "Qt6QuickTest",
    "Qt6QuickLayouts",
    "Qt6Quick3DXr",
    "Qt6Quick.dll",
    "Qt6Qml",
    "Qt6Pdf",
    "Qt6Multimedia",
    "Qt6ShaderTools",
    "Qt6WebEngineQuick",
    "Qt6WebChannelQuick",
    "Qt6Labs",
    "Qt6Designer",
    "Qt6Help",
    "Qt6Sql",
    "Qt6Svg",
    "Qt6Charts",
    "Qt6DataVisualization",
    "Qt6Graphs",
    "Qt6HttpServer",
    "Qt6Location",
    "Qt6Positioning",
    "Qt6Sensors",
    "Qt6SerialPort",
    "Qt6Bluetooth",
    "Qt6Nfc",
    "Qt6RemoteObjects",
    "Qt6Scxml",
    "Qt6StateMachine",
    "Qt6Test",
    "Qt6UiTools",
    "Qt6VirtualKeyboard",
    "Qt6WebSockets",
    "Qt6Xml",
    "Qt6ActiveQt",
    "Qt6SpatialAudio",
    "Qt6TextToSpeech",
)

KEEP_TRANSLATIONS = (
    "qtbase_fr.qm",
    "qtwebengine_fr.qm",
    "qtwebengine_en.qm",
    "qtbase_en.qm",
)

EXCLUDE_QML_DIRS = (
    "QtQuick3D",
    "QtMultimedia",
    "QtTest",
    "QtQuick/Pdf",
    "QtQuick/Particles",
    "QtCharts",
    "QtDataVisualization",
    "QtGraphs",
    "QtLocation",
    "QtPositioning",
    "QtSensors",
    "QtBluetooth",
    "QtNfc",
    "QtRemoteObjects",
    "QtScxml",
    "QtStateMachine",
    "QtVirtualKeyboard",
    "QtWebSockets",
    "QtLabs",
)


def _path_tail(path):
    return path.replace("\\", "/").lower()


def filter_binaries(binaries):
    out = []
    for entry in binaries:
        name = _path_tail(entry[0])
        if any(frag.lower() in name for frag in EXCLUDE_DLL_FRAGMENTS):
            continue
        out.append(entry)
    return out


def filter_datas(datas):
    out = []
    for entry in datas:
        dest = _path_tail(entry[0])
        if ".debug.pak" in dest or ".debug.bin" in dest:
            continue
        if "devtools_resources.debug" in dest:
            continue
        if "/translations/" in dest or dest.endswith(".qm"):
            base = os.path.basename(dest)
            if base not in KEEP_TRANSLATIONS:
                continue
        if "/qml/" in dest:
            if any(f"/qml/{d.lower()}/" in dest for d in EXCLUDE_QML_DIRS):
                continue
            if "/qml/qtquick/" in dest and "/qtwebengine/" not in dest:
                if any(
                    x in dest
                    for x in (
                        "/controls/",
                        "/dialogs/",
                        "/layouts/",
                        "/particles/",
                        "/shapes/",
                        "/timeline/",
                        "/tooling/",
                        "/effects/",
                        "/pdf/",
                    )
                ):
                    continue
        out.append(entry)
    return out


a = Analysis(
    ["Agent-DVR-desktop-widget.py"],
    pathex=[],
    binaries=[],
    datas=[(ICON_FILE, "assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDE_MODULES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.binaries = filter_binaries(a.binaries)
a.datas = filter_datas(a.datas)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AgentDVR_Widget",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_FILE,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AgentDVR_Widget",
)
