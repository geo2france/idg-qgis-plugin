# IDG

Plugin pour QGIS 3 fournissant un accès simple aux données de l'ensemble des Infrastructure de Données Géographiques (IDG) et d'autres ressources nationales géographiques utiles.

## Installation

Pré-requis :

* QGIS version LTR [3.22] ou supérieure
* Une connexion Internet

Installation depuis le dépôt officiel (via le gestionnaire d'extensions de QGIS) :

* Depuis le menu principal : menu Extensions > Installer/Gérer les extensions > IDG

## Utilisation

[UPDATE] [TODO]

Affichage des ressources mises à disposition des utilisateurs via l'extension :

* Dans le menu de QGIS : Internet > IDG > Afficher le panneau IDG

Un nouveau panneau latéral apparaît alors. Il contient une vue arborescente des ressources utiles aux utilisateurs·rices
des plateformes de données géographiques régionales.
Cet arbre contient pour l'instant (version 0.5.0 du plugin) :

* des couches et des styles issues de services internet WMS
* des feature types (classes d'entités) de services internet WFS (avec la possibilité de définir un filtre sur
certaines entités)
* des répertoires facilitant l'organisation et la présentation des ressources décrites ci-dessus

Pour ajouter une couche WMS ou une classe d'entités WFS sur la carte courante de QGIS vous pouvez utiliser l'une des
opérations suivantes :

* double-clic sur le nœud en question
* clic-droit sur le nœud en question et menu contextuel "Ajouter à la carte"
* glisser-déposer du nœud sur la carte de QGIS

L'arbre des ressources n'est pas entièrement renseigné, par conséquent, le double-clic sur certains nœuds peut ne rien
ajouter à la carte courante. Les ressources non correctement paramétrées dans le plugin sont marquées d'une icône avec
un point d'exclamation.

## Conception

### Auteurs

* Benjamin Chartier, Jean-Baptiste Desbas

### Source d'inspiration

* Nicolas Damiens

### Contributeurs

<a href="https://github.com/geo2france/idg-qgis-plugin/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=geo2france/idg-qgis-plugin" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

### Autres remerciements

* Auteurs des icônes de QGIS, reprises dans l'arbre des ressources
* Pour le fichier plugin/geo2france/images/Icon_Simple_Warn.png cf.
<https://commons.wikimedia.org/wiki/File:Icon_Simple_Warn.png>

## Licence

GNU Public License (GPL) Version 2
