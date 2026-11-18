# Guide & Cahier des Charges — Laboratoire de Robotique (Meca500)
**Module :** Control & Automation — Precision Engineering (Master UniBE / BFH)  
**Assistant de cours :** Tizian BUERGI (`tizian.buergi@bfh.ch`)  
**Lieu :** Collaborative Room 2 (GUE24/26)  
**Date limite de rendu du rapport final :** **Lundi 04.01.2027 à 09:00** (sur BFH Moodle)  
**Pondération :** **30% de la note** de la partie Robotique.

---

## 📋 Informations Générales & Modalités d'Évaluation

### Livrables obligatoires
1. **Un rapport de groupe unique** (format PDF, rédigé avec Typst dans `report/main.typ`).
2. **Tous les scripts Python développés** (dans `src/`).
3. **Une vidéo de démonstration** : au moins 5 cycles continus du test de répétabilité de la Session 3.
4. **Schémas techniques obligatoires dans le rapport** :
   - Schémas d'attribution de tous les repères (base, articulations, bride, outil laser TCP, capteur caméra).
   - Tableau récapitulatif de toutes les matrices de transformation de repères.
   - Croquis de l'espace de travail global du robot avec les repères positionnés.
   - Analyse réflexive : problèmes rencontrés, méthodes de résolution, pistes d'amélioration futures et feedback sur le cours.

### Règles d'or de sécurité en laboratoire
* La main de l'opérateur doit **constamment reposer sur le bouton d'arrêt d'urgence physique (E-Stop)** pendant les mouvements du robot.
* Démarrer systématiquement les mouvements à vitesse réduite (**vitesse $\le 5\%$**).
* **Règle de concurrence réseau** : Une seule connexion active à la fois sur le contrôleur du robot (interface web ou script Python). En Python, toujours exécuter `del meca` en fin d'utilisation pour libérer le socket.

---

## 🛠️ Session 1 : Meca500, Sécurité & Jogging (13.11 & 18.11)

### Connexion & Réseau
* **Wi-Fi Robot** : SSID = `Meca500` | Mot de passe = `us3rus3r`.
* **Interface Web (Soft Teach Pendant)** : `http://192.168.0.100` ou `http://192.168.0.101`.

### Questions et tâches obligatoires pour le rapport
#### 1. Informations produit
1. Marque (*Mecademic*) et modèle exact (*Meca500 r4*).
2. Avantages et faiblesses du robot ? Particularités mécaniques et électroniques ? (contrôleur ultra-compact intégré dans la base, absence de jeu mécanique, précision de 5 µm vs charge utile limitée, portée réduite, protocole propriétaire).
3. Applications industrielles cibles (micro-assemblage, horlogerie, contrôle qualité optique, lab automation).
4. Charge utile maximale nominale (0.5 kg nominal, 1 kg avec dynamique réduite).
5. Emplacement des boutons d'arrêt d'urgence.
6. **Test de l'Arrêt d'Urgence** : Déclencher puis relâcher le bouton d'arrêt d'urgence. Quelles sont les étapes logicielles et matérielles exactes nécessaires pour réactiver et relancer le robot après un E-Stop ?

#### 2. Degrés de liberté & Jogging
1. Combien d'articulations physiques ? Combien de degrés de liberté (DOF) ? *(6 rotoïdes / 6 DOF)*.
2. **Joint Jogging (Espace articulaire)** : Tester chaque articulation dans l'interface web. Relever les limites angulaires exactes en degrés pour chacun des 6 axes ($\theta_1$ à $\theta_6$).
3. **Cartesian Jogging (Espace cartésien)** : 
   - Jusqu'où le robot peut-il aller dans chaque direction $X, Y, Z$ ?
   - Peut-on orienter la bride de manière arbitraire ?
   - Comparer l'espace de travail pratique mesuré avec la fiche technique constructeur.

#### 3. Pilotage Python (`src/Meca500Test.py`)
* **Attention** : Ne jamais exécuter le script de haut en bas ! Utiliser le mode cellules interactives (`#%%` avec `Shift + Entrée`).
* Tester plusieurs combinaisons de consignes articulaires et vérifier que la pose cartésienne retournée correspond à la réalité physique.

---

## 📐 Session 2 : Cinématique Directe & Outil Laser (25.11 & 02.12)

### Objectifs
Dériver et implémenter la cinématique directe du Meca500 en symbolique avec **SymPy**, comparer avec le contrôleur interne et calibrer l'offset de l'outil laser (**Tool Center Point / TCP**).

### Questions et tâches obligatoires pour le rapport
#### 1. Cinématique directe interne (Interface Web)
1. Que contiennent les 6 éléments du vecteur articulaire ? ($[\theta_1, \theta_2, \theta_3, \theta_4, \theta_5, \theta_6]$ en degrés).
2. Que contiennent les 6 éléments du vecteur cartésien $^B X$ ? ($[X, Y, Z, Rx, Ry, Rz]$ avec positions en mm et orientations sous forme d'angles d'Euler en degrés).
3. **Tableau comparatif des 7 configurations articulaires** :
   Relever dans l'interface web la pose cartésienne $^B X$ pour :
   * $[0^\circ, 0^\circ, 0^\circ, 0^\circ, 0^\circ, 0^\circ] \rightarrow [190\text{ mm}, 0\text{ mm}, 308\text{ mm}, 0^\circ, 90^\circ, 0^\circ]$
   * $[90^\circ, 0^\circ, 0^\circ, 0^\circ, 0^\circ, 0^\circ]$
   * $[0^\circ, 0^\circ, -90^\circ, 0^\circ, 0^\circ, 0^\circ]$
   * $[0^\circ, 90^\circ, -90^\circ, 0^\circ, 0^\circ, 0^\circ]$
   * $[0^\circ, 0^\circ, 0^\circ, 90^\circ, 0^\circ, 0^\circ]$
   * $[0^\circ, 0^\circ, 0^\circ, 0^\circ, 90^\circ, 0^\circ]$
   * $[0^\circ, 0^\circ, 0^\circ, 0^\circ, 0^\circ, 90^\circ]$

#### 2. Dérivation symbolique avec SymPy
1. Établir la chaîne de transformations homogènes $^{0}T_6 = A_1(\theta_1) \cdot A_2(\theta_2) \cdots A_6(\theta_6)$ avec les longueurs géométriques réelles ($l_0, l_2, l_3, l_4, l_6$ issues de la datasheet).
2. **Représentation de l'orientation** : Quelle convention d'angles d'Euler permet de retrouver exactement les valeurs de l'interface Mecademic ? *(Angles fixes / extrinsèques XYZ vs angles d'Euler intrinsèques)*.
3. Calculer les 7 poses avec votre modèle SymPy et les comparer aux valeurs du contrôleur. Sont-elles rigoureusement identiques ? Expliquer d'éventuels décalages (conventions DH, zéros d'angles).

#### 3. Calibration de l'outil laser (TCP)
1. Dériver la matrice de transformation homogène $^{F}T_{\text{TCP}}$ (plan mécanique `docs/LaserTool.pdf`, longueur laser nominale $d_z = 264\text{ mm}$).
2. **Réorientation du poignet** : À la position articulaire zéro $[0,0,0,0,0,0]$, le laser ne pointe pas verticalement vers la table. Quels angles spécifiques donner au poignet ($\theta_4, \theta_5, \theta_6$ uniquement, avec $\theta_1 = \theta_2 = \theta_3 = 0$) pour orienter le faisceau laser parfaitement à la verticale vers le bas ?
3. Configurer l'offset d'outil dans le contrôleur (`SetTrf(x, y, z, α, β, γ)` ou `meca.setToolOffset(...)`).
4. Vérifier la nouvelle pose $^B X$ rapportée à la position zéro et comparer avec votre modèle symbolique incluant le TCP ($^B T_{\text{TCP}} = ^B T_F \cdot ^F T_{\text{TCP}}$).

---

## 🎯 Session 3 : Répétabilité selon ISO 9283 (09.12 & 18.12)

### Matériel & Dispositif de mesure
* **Caméra industrielle** : SVS-Vistek `exo183MU3` (CMOS monochrome Sony IMX183CLK, $5496 \times 3672$ px, taille pixel $2.4\,\mu\text{m}$, zone active $13.19 \times 8.81\text{ mm}$).
* **Flux caméra en direct** : `http://192.168.0.25:8080`.
* **Distance de travail du laser** : $264\text{ mm}$ le long de l'axe $Z$ de l'outil.
* **Deux configurations d'essai imposées (poses caméra dans le repère Base)** :
  * **Configuration repliée $\{F\}$ (Folded)** :  
    $^B X_F = [189.43, 180.00, 49.62, -112.20^\circ, 9.67^\circ, 93.91^\circ]$
  * **Configuration tendue $\{S\}$ (Stretched)** :  
    $^B X_S = [158.10, -2.54, 52.89, 100.93^\circ, 12.94^\circ, -92.48^\circ]$

### Questions et tâches obligatoires pour le rapport
#### 1. Calibration & Coins du capteur caméra
1. Calculer mathématiquement $^B T_{F\_T}$ et $^B T_{S\_T}$ pour amener le TCP laser à l'origine du capteur avec une distance normale de $264\text{ mm}$.
2. Déplacer le robot en vitesse lente (`SetCartLinVel(10)`), allumer le laser et enregistrer l'image du spot centré.
3. En mode jog repère outil (TRF), trouver et noter les **4 poses cartésiennes extrêmes** correspondant aux 4 coins du capteur CMOS (le spot doit rester entièrement dans la zone active des pixels).

#### 2. Répétabilité Unidirectionnelle (Python)
1. Interroger la position initiale du spot via le client caméra (`getLaserLocation()`).
2. Définir une pose de dégagement $\{A\}$ à **$-20\text{ mm}$ le long de l'axe $-X$ de l'outil**.
3. Écrire une boucle `for` : Dégagement $\rightarrow$ Retour à la cible $\rightarrow$ Pause $\ge 1\text{ s}$ $\rightarrow$ Mesure $(x, y)$.
4. **Exigence statistique** : Enregistrer **au moins 50 points de mesure** pour la pose repliée $\{F\}$ ET pour la pose tendue $\{S\}$.
5. **Vidéo obligatoire** : Filmer le robot pendant au moins 5 cycles consécutifs.
6. Tracer l'ellipse de confiance à 95% avec `PlotEllipse.py`.
7. **Questions d'analyse** :
   - Les demi-axes de l'ellipse confirment-ils la répétabilité de $5\,\mu\text{m}$ annoncée par Mecademic ?
   - Quelles différences observe-t-on entre la pose repliée $\{F\}$ et la pose tendue $\{S\}$ ? Expliquer physiquement (bras de levier, flexion mécanique des axes, rigidité structurale).

#### 3. Répétabilité Bidirectionnelle
1. Ajouter une seconde direction d'approche à **$+20\text{ mm}$ le long de l'axe $+X$ de l'outil**.
2. Réaliser **au moins 25 cycles complets (soit 50 points au total)** pour $\{F\}$ et $\{S\}$.
3. **Questions d'analyse** :
   - Comment évolue l'ellipse par rapport au test unidirectionnel (dispersion, orientation des axes) ?
   - En quoi l'inversion de sens met-elle en évidence le jeu mécanique (*backlash*) et les frottements/hystérésis ?
   - Comparer le comportement replié vs tendu en bidirectionnel.

#### 4. Suivi de Trajectoire, Vitesse & Adoucissement des Coins (*Corner Blending*)
1. Programmer une trajectoire passant par les 4 coins du capteur caméra :
   - Test 1 : Vitesse lente ($2\text{ mm/s}$) et blending $0\%$ (`SetBlending(0)`).
   - Test 2 : Blending maximal à $100\%$ (`SetBlending(100)`).
   - Test 3 : Augmentation de la vitesse cartésienne ($v > 2\text{ mm/s}$).
2. Enregistrer les trajectoires avec `startTrajectoryRecording()` et `stopTrajectoryRecording()`.
3. Superposer les courbes et analyser :
   - Quelles déformations géométriques apparaissent aux angles ?
   - Quel est l'impact combiné du pourcentage de blending et de la vitesse sur l'arrondi, le dépassement (*overshoot*) et le temps de cycle ?
   - **Exigence graphique** : Chaque figure de trajectoire dans le rapport doit comporter une légende claire indiquant la vitesse et le pourcentage de blending.

---

## 📝 Check-list Finale pour le Rapport Typst (`report/main.typ`)

- [ ] **Page de garde & En-tête** : Noms des étudiants, groupe, date de remise (04.01.2027), logos BFH et UniBE.
- [ ] **Session 1** : Réponses aux 6 questions produit, limites angulaires des 6 articulations, comparaison de l'espace de travail avec la fiche constructeur, description de la procédure E-Stop.
- [ ] **Session 2** : Tableau comparatif des 7 configurations (Contrôleur vs SymPy), justification de la convention d'Euler, dérivation mathématique du TCP laser ($d_z = 264\text{ mm}$), angles du poignet pour pointer à la verticale.
- [ ] **Session 3** : Calculs des poses $\{F\}$ et $\{S\}$, coordonnées des 4 coins caméra, graphiques des ellipses 95% unidirectionnelles ($\ge 50$ pts) et bidirectionnelles ($\ge 25$ cycles), discussion de la répétabilité ($5\,\mu\text{m}$) et de la rigidité replié/tendu, graphiques de suivi de trajectoire avec blending (0% vs 100%) et vitesse.
- [ ] **Schémas géométriques** : Schéma propre de tous les repères et tableau récapitulatif des repères.
- [ ] **Code Python** : Extraits essentiels insérés dans le rapport, scripts complets propres joints dans `src/`.
- [ ] **Vidéo** : Lien ou fichier vidéo de $\ge 5$ cycles de répétabilité.
- [ ] **Conclusion & Retour d'expérience** : Problèmes rencontrés, solutions apportées, pistes futures et feedback sur le TP.
