# IDG

Plugin pour QGIS 3 fournissant un accès simple aux données de l'ensemble des Infrastructure de Données Géographiques (IDG) et d'autres ressources nationales géographiques utiles.


## Installation

Pré-requis :

* QGIS version LTR [3.22] ou supérieure
* Une connexion Internet

Installation depuis le dépôt officiel (via le gestionnaire d'extensions de QGIS) :

* Depuis le menu principal : menu Extensions > Installer/Gérer les extensions > IDG

## Utilisation

### Administrateur

Créer un nouveau projet et y ajouter les couches que vous souhaitez diffuser.
> **Warning**
> Les couches doivent pouvoir être accessible depuis n'importe où (fichiers distants ou flux WMS/WFS, etc.), il ne doit **pas** s'agir de fichiers locaux.


Il est recommandé d'[organiser les couches en groupes et sous-groupes](https://docs.qgis.org/3.22/fr/docs/user_manual/introduction/general_tools.html#group-layers-interact).

Dans les propriétés du projets, remplir les champs suivants :

- **Métadonnées > Identification > Titre** : Le nom de la plateforme qui sera visible par l'utilisateur (ex : Geo2France)
- **Métadonnées > Identification > Résumé** : Facultatif, une brève présentation qui sera visible au survol
- **Métadonnées > Liens** : Vous pouvez ajouter ici des liens vers les différents services de votre plateformes (ex : contact, catalogue). 
   Ceux-ci seront accessibles à l'utilisateur via un clique droit sur le nom de la plateforme.

Pour chaque couche, vous pouvez définir :
- Un titre et un résumé (_Propriété > Métadonnées > Identification_)
- Une symbologie
- Une URL de métadonnées : créer un lien nommé "Metadata" dans les propriété de la couche (_Propriété > Métadonnées > Liens_)

Enregistrez le fichier projet ((qgs ou qgz) et déposez le sur un un serveur web (serveur HTTP, Github, Cloud, etc.).

[TODO] Procédure pour enregistrer la plateforme dans les plateforme par défaut du plugin)

### Utilisateur

Dans le panneau _navigateur_ sur la gauche, double-cliquer sur l'icon **IDG** : cela déroulera les différentes plateformes disponibles.

Pour ajouter de nouvelles plateformes, mettre à jour le plugin ou ajouter l'url fournie par l'administrateur dans _préférence > IDG_


## Conception

### Auteurs

* Benjamin Chartier, Jean-Baptiste Desbas

### Source d'inspiration

* Nicolas Damiens

### Contributeurs

[TODO]

### Autres remerciements

* Auteurs des icônes de QGIS, reprises dans l'arbre des ressources
* Pour le fichier plugin/geo2france/images/Icon_Simple_Warn.png cf.
<https://commons.wikimedia.org/wiki/File:Icon_Simple_Warn.png>

## Licence

GNU Public License (GPL) Version 2
