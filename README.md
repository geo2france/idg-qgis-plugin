geo2france-qgis2-plugin
=======================

Plugin pour QGIS 3 fournissant un accès simple aux données de Géo2France et d'autres ressources géographiques utiles en région Hauts-de-France.


Installation
------------

Pré-requis :
* Installation opérationnelle de QGIS 3.0 (utilisez une version LTR récente de préférence).

Installation manuelle :
* Installation :
  * Télécharger le répertoire ./plugin/geo2france
  * Copier ce répertoire dans le répertoire des plugin de votre répertoire personnel (typiquement ~/.qgis2/python/plugins)
* Activation de l'extension :
  * Lancer QGIS
  * Ouvrir le gestionnaire d'extensions
  * Activer le plugin "Geo2France" dans le gestionnaire d'extensions
  * Fermer le gestionnaire d'extensions

Installation automatique (via le gestionnaire d'extensions de QGIS) :
* Déclarer et activer le dépôt suivant : https://www.geo2france.fr/public/qgis3/plugins/plugins.xml
* Rechercher et charger l'extension intitulée "Geo2France"



Utilisation
-----------

Affichage des ressources mises à disposition des utilisateurs via l'extension :
* Dans le menu de QGIS : Extension > Géo2France > Afficher le panneau Géo2France

Un nouveau panneau latéral apparaît alors. Il contient une vue arbosrescente des ressources utiles aux partenaires 
de Géo2France.
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



Notes
-----

Version 0.9.0 :
* portage pour QGIS 3


Auteurs
-------

Auteurs :
* Benjamin Chartier

Source d'inspiration :
* Nicolas Damiens

Autres remerciements :
* Auteurs des icônes de QGIS, reprises dans l'arbre des ressources
* Pour le fichier plugin/geo2france/images/Icon_Simple_Warn.png cf. 
https://commons.wikimedia.org/wiki/File:Icon_Simple_Warn.png


Licence
-------

Licence : New BSD

cf. fichier LICENSE.txt

cf. https://choosealicense.com/licenses/bsd-3-clause/
