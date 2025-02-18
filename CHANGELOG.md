# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-02-18

### Changed

- Amélioration de performances : Téléchargement des fichiers distant en parallèle
- Utilisation du gestionnaire de tâches QGIS (_QgsTaskManager_)
- Meilleure gestion des fichiers projets manquants

## [0.3.2] - 2025-02-03

### Changed

- Désactivation du projet Géoplateforme à la première utilisation du plugin (en attente d'une refonte de ce projet pour améliorer son temps de chargement et sa lisibilité)
- Mise à jour de la lecture des settings pour mieux prendre en compte leurs changements de modèle de données
- Enregistrement des settings à leur lecture si détection d'une différence de version
- Mise à jour du numéro de version du plugin QGIS à l'enregistrement des settings
- Renommage de certaines fonctions et variables

## [0.3.1] - 2025-01-31

### Changed

- Amélioration des performances en ne chargeant pas inutilement les plateformes non utilisées

## [0.3.0] - 2025-01-17

### Changed

- Mise à jour de la plateforme GéoBretagne
- Réorganisation de l'arborescence des fichiers téléchargés par le plugin
- Changement de la structure du fichier de l'index des plateforme (default_idg.json)
- Meilleure intégration à QGIS en utilisant QgsTask et QgsTaskManager
- Amélioration des performances de chargement des fichiers projet des plateformes

### Added

- Ajout de la plateforme GeoPaysdeBrest

## [0.2.5] - 2024-10-10

### Added

- Ajout d'un paramètre pour activer/désactiver le téléchargement du fichier de configuration au lancement (par défaut True) (config_files_download_at_startup)
- Ajout d'un bouton pour forcer le rechargement des fichiers distants

### Changed

- Réorganisation du code en vue d'une maintenance plus facile
- Amélioration de l'organisation des éléments dans la fenêtre de paramétrage du plugin
- Affichage de la liste des IDG dans l'ordre alphabétique (dans la fenêtre de paramétrage)
- Utilisation de la bonne orthographe pour "Géo2France"

### Removed

- Retrait des éléments non fonctionnels du panneau de configuration (plateformes custom)
- Suppression des paramètres obsolètes du plugin (qui étaient accessibles via la fenêtre des paramètres de QGIS)

## [0.2.4a] - 2024-01-12

### Changed

- Ne pas télécharger les fichiers projets des IDG masquées

### Fixed

- Correction de la disparition des plateformes lors d'un clic droit

## [0.2.3] - 2023-12-01

### Added

- Ajout de la plateforme Géoplateforme de l'IGN

### Changed

- Téléchargement des fichiers des plateformes de manière asynchrone
- Amélioration des performances de chargement des fichiers projet des plateformes

### Fixed

- Correction de coquilles dans le readme
- Correction de la restauration des paramètres d'usine
- Correction de problèmes de lancement du plugin

## [0.2.2] - 2023-07-28

### Changed

- Amélioration significatives des performances en réalisant le téléchargement des fichiers hors du thread principal (ne ralentit plus le lancement de QGIS et ne gèle plus l'interface).

## [0.2.1] - 2023-07-19

### Added

- Ajout de la plateforme GéoBretagne

### Fixed

- Correction d'un bug qui provoquait la modification du timeout général utilisé par QGIS.

## [0.2.0] - 2023-07-18

### Added

- Possibilité pour l'administrateur d'ajouter une icône à la plateforme
- Nouveau fichier pour ajouter des plateformes au plugin (default_idg.json)
- Ajout des plateformes OPenIG et DataGrandEst
- Possibilité de masquer les plateformes stock du plugin
- Différenciation des plateformes stock (inclues dans le plugin) et des plateformes custom (url ajoutées par l'utilisateur)
- Ajout d'un timeout pour éviter les crashs lors du téléchargement des fichiers des plateformes
- Tooltip avec la description des plateformes

### Removed

- Suppression de la plateforme demo

## [0.1.0] - 2023-04-13

### Changed

- Utilisation de l'explorateur de QGIS
- Utilisation de la fenêtre des préférences de QGIS pour configurer le plugin
