# Control & Automation — Robotics Laboratory (MPE)

Ce dépôt contient le code, la documentation et le rapport pour la partie **Robotics** du cours **Control & Automation** (Master of Precision Engineering - BFH / UniBE).

> 📖 **[Guide complet du laboratoire & Cahier des charges du rapport](docs/LAB_GUIDE.md)** : toutes les questions à traiter par session, le protocole expérimental et la check-list pour la remise du rapport final (deadline : 04.01.2027 à 09:00).

---

## 🛠️ Configuration rapide pour l'équipe (en 2 minutes)

Le projet utilise **`uv`** (par Astral) pour gérer automatiquement l'environnement virtuel Python et les dépendances sans conflits de versions.

### 1. Installer `uv` (si ce n'est pas déjà fait)
* **Windows (PowerShell)** :
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
* **Linux / macOS (Terminal)** :
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Cloner le projet & synchroniser l'environnement
```bash
git clone <URL_DU_DEPOT>
cd "Robotic Laboratory"
uv sync
```
`uv` va automatiquement télécharger la bonne version de Python, créer le dossier `.venv` et installer toutes les dépendances requises (`numpy`, `sympy`, `scipy`, `matplotlib`, `grpcio`, `protobuf`).

### 3. Ouvrir dans VS Code
1. Ouvrez le dossier dans VS Code.
2. Acceptez les extensions recommandées (`Python`, `Ruff`, `Jupyter`, `Tinymist`).
3. L'interpréteur Python est automatiquement configuré sur `.venv/Scripts/python.exe`.

---

## 📂 Structure du projet

```text
Robotic Laboratory/
├── .venv/                      # Environnement virtuel local (géré par uv, ignoré par Git)
├── .vscode/                    # Paramètres d'interpréteur & extensions recommandées
├── data/                       # Données brutes de mesures (spots laser, trajectoires)
├── docs/                       # Manuels officiels (LaserTool.pdf, Meca500 User/Prog manuals)
├── notebooks/                  # Notebooks Jupyter pour l'analyse symbolique (SymPy)
├── report/                     # Rapport du laboratoire (Typst)
│   ├── figures/                # Graphiques générés par les scripts Python
│   └── main.typ                # Document source du rapport
├── src/                        # Drivers et code Python modulaire
│   ├── Meca500.py              # Wrapper de commande TCP/IP pour le robot Meca500
│   ├── MPECamClient.py         # Client gRPC pour la caméra SVS
│   ├── PlotEllipse.py          # Tracé d'ellipses d'incertitude 95% (ISO 9283)
│   ├── Repeatability.py        # Script d'analyse de répétabilité
│   └── ch/                     # Modules gRPC et vision fournis par la BFH
├── pyproject.toml              # Déclaration des dépendances uv
├── uv.lock                     # Lockfile garantissant des versions identiques
└── README.md
```

---

## 🤖 Connexion au matériel physique (Salle GUE24/26)

* **Wi-Fi Robot** : `Meca500` (mot de passe : `us3rus3r`)
* **Pendant logiciel web** : `http://192.168.0.100` ou `http://192.168.0.101`
* **Stream caméra en direct** : `http://192.168.0.25:8080`
* **Test de connexion rapide** :
  ```bash
  uv run python src/Meca500Test.py
  ```
  *(Important : un seul client peut être connecté au robot à la fois. Assurez-vous d'appeler `del meca` ou de fermer le socket en fin de script).*
