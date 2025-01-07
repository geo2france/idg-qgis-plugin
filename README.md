# IDG

Plugin pour QGIS 3 fournissant un accès simple aux données d'Infrastructures de Données Géographiques (IDG) et d'autres ressources nationales géographiques utiles.
Il s'agit du remplaçant des extensions historiques de Géo2France, DataGrandEst, GéoBretagne, indigeo.... Le plugin IDG vise à les remplacer au sein d'un outil unifié et modernisé.

Ses principaux intérêts par rapport aux anciens plugins :

- Un plugin personnalisable
- Un plugin unifié pour faciliter les opérations de maintenance
- Le support de toutes les sources de données reconnues par QGIS
- La possibilité pour les plateformes d'intégrer des styles évolués
- Une meilleure intégration dans QGIS (dans son Explorateur et sa fenêtre de préférences notamment)

Canal de discussions : <https://matrix.to/#/!DqHgKIoltGIikFRreo:matrix.org>

Accès aux données des plateformes :

- [DataGrandEst](https://datagrandest.fr/)
- [GéoBretagne](https://geobretagne.fr)
- [Géo2France](https://geo2france.fr)
- [OPenIG](https://openig.org)
- [Géoplateforme](https://www.ign.fr/geoplateforme/la-geoplateforme-en-bref)
- [GéoPaysdeBrest](https://geo.brest-metropole.fr/portal/apps/sites/#/geopaysdebrest)

## Mise en œuvre

## Installer le plugin

Pré-requis :

- QGIS version LTR [3.28] ou supérieure
- Une connexion Internet (les ressources mises à disposition via le plugin sont accessibles en ligne uniquement)

Depuis le dépôt QGIS officiel :

- se rendre dans le gestionnaire d'extensions de QGIS (Extensions > Installer/Gérer les extensions)
- rechercher le plugin _IDG_

Depuis un fichier ZIP :

- télécharger le fichier ZIP de la dernière version du plugin sur la page [release](https://github.com/geo2france/idg-qgis-plugin/releases) du projet Github
- se rendre dans le gestionnaire d'extensions de QGIS (Extensions > Installer/Gérer les extensions)
- sélectionner l'entrée _Installer depuis un ZIP_
- sélectionner le fichier téléchargé et lancer l'installation

Une fois installé, le plugin ajoute les éléments suivants à l'interface graphique de QGIS :

- le menu Extensions > IDG
- une entrée _IDG_ dans le panneau _Explorateur_ de QGIS
- une entrée _IDG_ dans la fenêtre des options de QGIS (fenêtre accessible via le menu Préférences > Options)

### Utiliser le plugin

Dans le panneau _Explorateur_ de QGIS, le contenu de l'entrée _IDG_ pour dérouler son contenu. Il s'agit d'une liste arborescente qui présente les couches de données proposées par plateforme et organisées par thématiques et sous-thématiques.

<p align="center">
  <img src="repo/screenshot_browser_1.png" alt="QGIS Browser" />
</p>

#### Naviguer dans l'arborescence de données

L'entrée _IDG_ de l'_Explorateur_ de QGIS contient une vue arborescente de l'ensemble des couches de données partagées par les plateformes de données qui contribuent au plugin. Pour explorer cette arborescence, il suffit de doublecliquer sur un répertoire de cette arborescence ou de cliquer sur le petit triangle situé à sa gauche, comme pour toute autre partie de l'_Explorateur_ QGIS.

#### Ajouter une couche de données à la carte

Pour ajouter une couche de données présente dans cette arborescence à la carte, vous avez deux possibilités :

- Doublecliquer sur la couche de données dans l'_Explorateur_ de QGIS
- Faire un clic droit sur la couche de données et sélectionner l'entrée _Ajouter la couche à la carte_ du menu contextuel

Une fois que vous avez ajouté une couche à votre projet QGIS, vous êtes libre d'y apporter les personnalisations dont vous avez besoin, que ce soit en matière de filtre et d'apparence.

> [!NOTE]
> Ces couches de données sont des ressources en lignes. Lorsque vous ajoutez une couche à votre carte, QGIS fait une copie de sa définition dans votre projet QGIS ; il ne réalise pas une copie des données. Intégrer une de ces couches dans votre projet n'en fait des données gérées en local. Vous n'avez donc, en général, pas la possibilité d'en modifier le contenu.

> [!NOTE]
> Une fois que cette copie est réalisée, une modification ultérieure de la définition de la couche par la plateforme ne sera pas répercutée sur votre projet. Par exemple :
>
> - si l'administrateur de la plateforme met à jour le style de la couche de données, votre projet conservera le style qui a été appliqué lors d'intégration de la couche dans votre projet ou bien le style particulier que vous avez choisi si vous lui avez appliqué une personnalisation
> - si l'administrateur de la plateforme met à jour l'URL de la couche de données, votre projet conservera l'ancienne URL (qui pourrait ne plus fonctionner donc)
> - si l'administrateur de la plateforme supprime la couche de données, votre projet conservera cette couche de données (qui pourrait ne plus fonctionner également)

Il est donc possible que, en raison de modifications opérées par les administrateurs des plateformes, vous deviez mettre à jour votre projet QGIS en supprimant des couches et en les remplaçant par d’autres dont les définitions ont été mises à jour.

#### Accéder aux métadonnées d'une couche de données

Pour accéder aux métadonnées d'une couche depuis l'_Explorateur de QGIS :

- faites un clic droit sur la couche de données
- sélectionnez _Afficher les métadonnées..._ dans le menu contextuel
- QGIS devrait ouvrir la fiche de métadonnées dans votre navigateur internet

Cette fonction n'est accessible que pour les jeux de données pour lesquels le lien de métadonnées a été correctement renseigné par l'administrateur de la plateforme.

#### Activer et déactiver une plateforme

L'organisation de ces couches de données a été définie pour chaque plateforme par son administrateur de données. Le plugin n'impose pas de règles communes ; aucune homogénéité n'est attendue pour leur classement.

La liste des plateformes visibles dans l'entrée _IDG_ de l'explorateur peut être personnalisée. Pour cela, rendez-vous dans la fenêtre des options du plugin (par exemple via le menu _Extensions > IDG > Paramètres_). En cochant/décochant une plateforme, vous l'affichez ou la masquez dans le panneau _Explorateur_ de QGIS (une fois que vos changements sont validés en cliquant sur le bouton _OK_)
Depuis les paramètres du plugin, vous avez la possibilité d'afficher/masquer les plateformes.

> [!NOTE]
> **Temps de chargement d'une plateforme**
>
> Le temps de chargement/mise à jour de l'entrée _IDG_ dans l'_Explorateur_ est conséquent (cela peut aller jusqu'à plusieurs dizaines de secondes) car la description des données de chaque plateforme est constituée d'un projet QGIS potentiellement très volumineux dont le contenu doit être contrôlé par QGIS. Lors de l'activation ou la désactivation d'une plateforme, vous devriez faire l'expérience de ce temps de chargement long. Une fois que ces fichiers sont chargés par QGIS l'exploitation du plugin est fluide.
>
> Nous vous recommandons donc :
>
> - d'être patient par rapport au temps de chargement de ces fichiers
> - de limiter l'affichage des plateformes à celles dont vous avez réellement besoin

### Référencer une plateforme

Créer un nouveau projet et y ajouter les couches que vous souhaitez diffuser.

> [!WARNING]
> Les couches doivent pouvoir être accessibles depuis n'importe où (fichiers distants, flux WMS/WFS, etc.) ; il ne doit **pas** s'agir de fichiers locaux.

Il est recommandé d'[organiser les couches en groupes et sous-groupes]<https://docs.qgis.org/3.34/fr/docs/user_manual/introduction/general_tools.html#group-layers-interact>).

Dans les propriétés du projet, remplissez les champs suivants :

- **Métadonnées > Identification > Titre** : Le nom de la plateforme qui sera visible par l'utilisateur (ex : Géo2France)
- **Métadonnées > Identification > Résumé** : Facultatif, une brève présentation qui sera visible au survol
- **Métadonnées > Liens** : Vous pouvez ajouter ici des liens vers les différents services de votre plateforme (ex : contact, catalogue, etc.)
   Ceux-ci seront accessibles à l'utilisateur via un clic droit sur le nom de la plateforme. Ajoutez un lien nommé `icon` pour ajouter une icône personnalisée à la plateforme (ou format PNG ou SVG)

Pour chaque couche, vous pouvez définir :

- **Métadonnées > Identification > Titre & Réumé** Un titre et un résumé
- **Métadonnées > Identification > Liens** Créer un lien nommé "Metadata" vers la fiche de métadonnées
- Une symbologie (style, étiquettes, formulaires, etc.)

Enregistrez le fichier projet (au format QGS ou QGZ) et **déposez-le sur un un serveur web** accessible pour tous les utilisateurs (serveur HTTP, Github, cloud, etc.).

Pour proposer l'ajout d'une plateforme dans le plugin : **éditez le fichier [default_idg.json](plugin/idg/config/default_idg.json)** et faites une _pull request_.

## Auteurs

- Développeurs : [Jean-Baptiste Desbas - Région Hauts-de-France](https://github.com/jbdesbas), [Benjamin Chartier - Optéos](https://github.com/bchartier), [Julie Pierson - UMR LETG](https://github.com/juliepierson)
- Source d'inspiration : [Nicloas Damiens - Picardie Nature](https://github.com/ndamiens)
- Autres contributeurs : [Viencent Fabry - Région Hauts-de-France](https://github.com/vfabry), [Nicolas Rochard - Région Hauts-de-France](https://github.com/Doctor-Who), [Stéphane Mével-Viannay](https://github.com/smevel), [Loïc Écault](https://github.com/lecault), [Tom Brunelle - OPenIG](https://github.com/tbrunelle9)
- [Julien Moura - Oslandia](https://github.com/Guts) pour le [template](https://oslandia.gitlab.io/qgis/template-qgis-plugin/) du plugin.
- Auteurs des icônes de QGIS, reprises dans l'arbre des ressources

## Licence

GNU Public License (GPL) Version 2
