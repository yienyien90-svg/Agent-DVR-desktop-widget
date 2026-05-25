# Agent DVR Desktop Widget

Petit overlay Windows pour afficher le flux **Agent DVR** dans une fenêtre flottante, toujours au-dessus des autres applications.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-WebEngine-green)
![Windows](https://img.shields.io/badge/OS-Windows-lightgrey)

## Fonctionnalités

- Fenêtre sans bordure, semi-transparente, repositionnable
- Affichage de la page Agent DVR via `QWebEngineView`
- Réduction en icône (bouton de restauration)
- Panneau réglages : URL, opacité, rechargement
- Raccourci `Échap` pour quitter

## Prérequis

- Windows 10/11
- [Python 3.10+](https://www.python.org/downloads/)
- [Agent DVR](https://www.ispyconnect.com/) en cours d'exécution (par défaut `http://localhost:8090`)

## Installation (développement)

```powershell
git clone https://github.com/yienyien90-svg/Agent-DVR-desktop-widget.git
cd Agent-DVR-desktop-widget
python -m pip install -r requirements.txt
python test_widget.py
```

## Compiler l'exécutable

```powershell
build.bat
```

L'exécutable est généré dans `dist\AgentDVR_Widget\AgentDVR_Widget.exe`.

> **Note taille** : l'exe embarque Chromium (Qt WebEngine), environ **300 Mo** après optimisation. Le dossier `dist/` n'est pas versionné sur GitHub — chaque utilisateur compile localement.

Lancement rapide après compilation :

```powershell
Lancer_AgentDVR_Widget.bat
```

## Configuration

Modifier l'URL par défaut dans `test_widget.py` :

```python
AGENT_DVR_URL = "http://localhost:8090/?viewIndex=0#Live"
```

Ou via le bouton **⚙** dans l'application.

## Structure du projet

| Fichier | Rôle |
|---------|------|
| `test_widget.py` | Application principale |
| `agent_dvr_widget.spec` | Configuration PyInstaller (build allégé) |
| `build.bat` | Installe les deps, génère l'icône, compile |
| `create_icon.py` | Génère `assets/camera.ico` |

## Publier une release GitHub (optionnel)

1. Compiler avec `build.bat`
2. Zipper `dist\AgentDVR_Widget\` (dossier complet)
3. Créer une **Release** sur GitHub et y joindre le zip

## Licence

MIT — voir [LICENSE](LICENSE).
