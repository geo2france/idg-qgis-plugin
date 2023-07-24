# IDG

Plugin pour QGIS 3 fournissant un accès simple aux données de l'ensemble des Infrastructure de Données Géographiques (IDG) et d'autres ressources nationales géographiques utiles.

Canal de discussions : https://matrix.to/#/!DqHgKIoltGIikFRreo:matrix.org

![QGIS Browser](repo/screenshot_browser_1.png)

Accès aux données des plateformes :
- [DataGrandEst](https://datagrandest.fr/)
- [GéoBretagne](https://geobretagne.fr)
- [Géo2France](https://geo2france.fr)
- [OPenIG](https://openig.org)

## Installation

Pré-requis :

* QGIS version LTR [3.28] ou supérieure
* Une connexion Internet

* Installation depuis le dépot QGIS : dans le gestionnaire d'exentions (Extensions > Installer/Gérer les extensions), activer les extensions expérimentales et rechercher le plugin _IDG_
* Installation depuis le fichier zip : télécharger depuis la derniere [release](https://github.com/geo2france/idg-qgis-plugin/releases) depuis le dépot github.


## Utilisation

### Administrateur

Créer un nouveau projet et y ajouter les couches que vous souhaitez diffuser.
> **Warning**
> Les couches doivent pouvoir être accessible depuis n'importe où (fichiers distants, flux WMS/WFS, etc.), il ne doit **pas** s'agir de fichiers locaux.


Il est recommandé d'[organiser les couches en groupes et sous-groupes](https://docs.qgis.org/3.22/fr/docs/user_manual/introduction/general_tools.html#group-layers-interact).

Dans les propriétés du projets, remplir les champs suivants :

- **Métadonnées > Identification > Titre** : Le nom de la plateforme qui sera visible par l'utilisateur (ex : Geo2France)
- **Métadonnées > Identification > Résumé** : Facultatif, une brève présentation qui sera visible au survol
- **Métadonnées > Liens** : Vous pouvez ajouter ici des liens vers les différents services de votre plateforme (ex : contact, catalogue, etc.) 
   Ceux-ci seront accessibles à l'utilisateur via un clic droit sur le nom de la plateforme. Ajoutez un lien nommé `icon` pour définir une icône à la plateforme (png ou svg)

Pour chaque couche, vous pouvez définir :
- **Métadonnées > Identification > Titre & Réumé** Un titre et un résumé
- **Métadonnées > Identification > Liens** créer un lien nommé "Metadata" vers la fiche de métadonnées
- Une symbologie (style, étiquettes, formulaires, etc.)

Enregistrez le fichier projet (qgs ou qgz) et **déposez le sur un un serveur web** accessible depuis l'exterieur (serveur HTTP, Github, cloud, etc.).

Pour proposer l'ajout d'une plateforme dans le plugin : **éditez le fichier [default_idg.json](plugin/idg/config/default_idg.json)** 
et faites une _pull request_.


### Utilisateur

Dans le panneau _navigateur_ sur la gauche, double-cliquez sur l'icone **IDG** : cela déroulera les différentes plateformes disponibles.

Depuis les paramètres du plugin, vous avez la possibilité d'afficher/masquer les plateformes.

## Conception

### Auteurs

* Benjamin Chartier, Jean-Baptiste Desbas

### Source d'inspiration

* Nicolas Damiens

### Contributeurs

[TODO]

### Autres remerciements

* [Julien Moura](https://github.com/Guts) (Oslandia) pour le [template](https://oslandia.gitlab.io/qgis/template-qgis-plugin/) du plugin.
* Auteurs des icônes de QGIS, reprises dans l'arbre des ressources


## Licence

GNU Public License (GPL) Version 2
