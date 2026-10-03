# Plan d'exécution différée — sécurité de l'auto-hébergement interne

Date : 2026-09-29. Mise à jour : 2026-10-03. État : lots 0 à 3 exécutés ; PR #71 des lots 1 à 3 ouverte en brouillon ; aucun déploiement.
Référence de l'audit : commit `306918c`, branche `codex/fix-maplibre-worker-bundle`.

Référence préparée pour les corrections : `677f14ecab5552c5171fe3d2877059d1e191bbff`, branche `codex/security-internal-hardening`. Le bilan local du lot 0 est conservé hors du dépôt.

État Git du lot 1 au 2026-09-30 : [PR #71](https://github.com/leto1210/Unifi-Log-Insights/pull/71), tête `e370aaf`, branche locale synchronisée et propre. Les trois derniers commits (`91eed92`, `71e7120`, `e370aaf`) cadrent le contrôle UniFi self-hosted, masquent une erreur inattendue du test de connexion et précisent la documentation de `UNIFI_API_KEY`. Les 66 tests ciblés des fichiers touchés passent ; vérifier à nouveau la CI avant toute suite publiée.

État Git du lot 2 au 2026-10-03 : commit `d152655` créé dans le checkout isolé, puis intégré dans la branche de la PR #71 sous `66101fb`, à partir de `e370aaf`. A4-A6 et la documentation sont implémentés, sans déploiement. Vérifications : 791 tests backend, 141 tests UI, build UI et syntaxe des neuf Python touchés réussis. Le smoke test conteneur reste au lot 3.

État Git du lot 3 au 2026-10-03 : branche `codex/security-internal-lot-3` fondée sur la tête `5a0ad61` de la PR #71. Les commits `c31450c` (import UniFi), `7bf841f` (volume vierge), `553bd10` (verrou npm) et `99ae033` (tests A7) sont intégrés à la branche de la PR #71 avec ce bilan. Aucun déploiement. Vérifications : 795 tests backend, 141 tests UI, build UI, syntaxe Python et shell, puis santé, enrôlement, connexion, refus anonyme et redémarrage sur volume Docker vierge jetable.

## 1. Objectif et périmètre

Améliorer la sécurité et la disponibilité d'une application auto-hébergée sur un réseau interne. Ne pas concevoir ce chantier comme une préparation à une exposition Internet. Les clients possibles sont l'administrateur, des utilisateurs internes, des intégrations et des agents munis de jetons API. Une machine interne compromise reste un scénario pertinent.

Conserver le mode mono-utilisateur explicitement choisi avec `AUTH_ENABLED=false`, les contrôleurs locaux et les installations avec certificats auto-signés. Distinguer ce mode volontaire de l'installation incomplète avec `AUTH_ENABLED=true`.

Les lots 0 à 3 ont été lancés par demandes distinctes, puis commités et poussés dans la PR #71 à la demande. Cette publication n'autorise pas automatiquement fusion, déploiement, rotation de secrets, modification des équipements ou migration de la base de production.

## 2. Consignes communes à tous les agents

1. Lire `AGENTS.md`, les consignes RTK locales, les leçons pertinentes et ce plan. Préfixer les commandes shell par `rtk` ; utiliser `rtk proxy` si nécessaire.
2. Revalider le code courant : l'audit est un point de départ, pas une garantie que le défaut existe encore. Relever le commit de base et examiner les changements intervenus.
3. Ne pas toucher aux modifications préexistantes ni à `.understand-anything/`. Aucun secret réel, log de production ou identifiant réseau réel dans tests, rapports ou commits.
4. Une tâche, un agent, un ensemble de fichiers réservé. Toute extension du périmètre doit être signalée à l'orchestrateur avant édition d'un fichier partagé.
5. Reproduire le défaut par un test ciblé avant correction, puis montrer sa disparition. Tester les fonctions et routes de production ; ne pas recopier l'algorithme dans le test.
6. Utiliser des clients simulés pour les intégrations, des données synthétiques et une base jetable quand nécessaire. Aucune requête de charge ni tentative d'exploitation sur la production.
7. Préserver les priorités de configuration env > DB > défaut, les interrupteurs d'intégration et les limites transactionnelles. Capturer atomiquement les champs de configuration interdépendants.
8. Conserver un seul cache de réponses : `receiver/response_cache.py`. Ne pas ajouter un second cache maison.
9. Si un retour de fonction change, rechercher tous ses appelants et adapter le contrat complet. Si un contrat API change, vérifier aussi le frontend et MCP.
10. Respecter style, docstrings et seuil de couverture documentaire Python du dépôt. Vérifier la syntaxe de chaque fichier Python modifié avant soumission et commit.
11. Rendre un compte rendu : défaut et conditions, fichiers modifiés, choix de compatibilité, tests exécutés et résultats, limitations, dépendances et éventuel retour arrière. Ne pas confondre un test bloqué avec un test réussi.

## 3. Orchestration et isolation

- Capacité : un orchestrateur + au maximum trois agents spécialisés actifs. Ne pas demander aux agents de déléguer à leur tour.
- L'orchestrateur possède `tasks/todo.md`, ce plan, les documents communs et l'intégration Git. Les agents ne modifient pas ces fichiers.
- Préférer un checkout isolé géré pour le chantier, après inspection des worktrees attachés. Ne pas choisir silencieusement la branche d'audit comme base : identifier la base d'intégration appropriée et vérifier son état.
- Dans un checkout partagé, aucune commande checkout/reset/merge/cherry-pick/commit par les agents. L'orchestrateur sérialise toutes les opérations Git et ne change pas de branche pendant leurs travaux.
- Les tâches d'un même lot ont des fichiers de production distincts. Les tests nouveaux portent des noms dédiés ; ne pas modifier `conftest.py` en parallèle.
- Un agent qui doit changer un fichier réservé propose un ajustement à l'orchestrateur ; celui-ci sérialise le changement ou déplace la tâche au lot suivant.
- Revue de chaque livraison avant intégration ; un commit cohérent par tâche lorsque les commits font partie du lancement. Aucune correction partielle publiée pour déclencher une revue.
- Ne passer au lot suivant qu'après validation du lot courant. Les trois slots peuvent être réutilisés ; pas besoin de conserver tous les agents en parallèle.

## 4. Lots de corrections

### Lot 0 — Préparation par l'orchestrateur

- [x] Relever branche, commit, état Git, consignes locales et éventuels correctifs déjà présents.
- [x] Préparer le checkout et une liste précise des fichiers réservés par agent.
- [x] Créer un environnement Python de test isolé à partir des requirements du dépôt et installer les dépendances frontend verrouillées ; ne pas modifier les manifests pour résoudre un problème local.
- [x] Exécuter les tests de référence et relever les échecs préexistants ; vérifier que les versions d'outils conviennent au projet courant.
- [x] Confirmer le périmètre lancé : demande utilisateur du 2026-09-30 limitée au lot 0. Aucun lot suivant lancé.

Lors de l'audit, l'environnement Python disponible manquait notamment de `requests` et `bcrypt`. Le lot 0 a levé cette limitation : 699 tests backend et 129 tests frontend réussis, build frontend réussi. Les tests de confiance proxy comportent encore une copie de l'ancien modèle : à remplacer par des tests du code réel dans A1. Ce résultat de référence ne prouve pas l'absence des défauts audités.

### Lot 1 — Disponibilité, autorisations et secrets (trois agents)

État : A1, A2 et A3 réalisés, documentés et poussés dans la [PR #71](https://github.com/leto1210/Unifi-Log-Insights/pull/71). Validation intégrée avant les trois derniers commits : 733 tests backend, 129 tests frontend, build UI et syntaxe Python réussis. Après ces commits, 66 tests backend ciblés et la syntaxe des sept fichiers Python touchés ont été revérifiés. La validation transverse complète et le smoke test conteneur restent au lot 3.

#### A1 — Spécialiste authentification : installation et droits effectifs

Fichiers réservés : `receiver/routes/auth.py`, `receiver/api.py`, `receiver/routes/tokens.py`, tests d'authentification dédiés et `receiver/tests/test_auth_proxy_trust.py`.

Objectifs :
- Avec `AUTH_ENABLED=true` et aucun administrateur configuré, fermer par défaut toutes les routes applicatives sauf une liste minimale explicite de routes de santé/enrôlement/bootstrap réellement nécessaires.
- Ne pas permettre lecture de logs, export de secrets, configuration ou création de jetons durant cette phase. Le secret d'installation reste nécessaire pour l'enrôlement.
- Préserver `AUTH_ENABLED=false` comme choix explicite de mode interne mono-utilisateur.
- Traiter l'ensemble vide des droits effectifs comme « aucun droit », jamais comme « revenir aux droits bruts ». Vérifier aussi le cas d'un propriétaire sans permissions.
- Préserver la compatibilité des jetons sans propriétaire existants intentionnels ; ne pas les révoquer en masse silencieusement. Supprimer leur création anonyme pendant l'installation protégée.
- Examiner le parcours HTTPS/secret proxy du tout premier démarrage : ne pas fermer l'API en créant un verrouillage administratif impossible à résoudre. Documenter une récupération locale autorisée sans rendre le secret publiquement accessible.

Tests : matrice auth désactivée / installation incomplète / administrateur existant ; setup sans/avec token ; accès anonyme aux routes sensibles refusé avant setup ; token interdit avant setup même sous HTTPS ; droits vides refusés ; permissions wildcard et jetons intentionnellement sans propriétaire préservés ; session lecteur ; secret proxy invalide ; conservation des routes publiques indispensables.

Validation : middleware et routes réels avec dépendances DB substituées, plus parcours d'enrôlement sur base jetable. Ne pas modifier `setup.py` : transmettre tout besoin à A4 après intégration.

#### A2 — Spécialiste intégrations : destination des secrets

Fichiers réservés : `receiver/routes/unifi.py`, `receiver/unifi/core.py`, `receiver/routes/pihole.py`, `receiver/pihole_api.py` et tests dédiés.

Objectifs :
- Refuser la réutilisation d'un secret enregistré ou d'environnement lorsque la destination fournie diffère de celle à laquelle il est associé.
- Définir une comparaison normalisée explicite : schéma, hôte, port effectif et éventuel chemin de base ; refuser userinfo et formes ambiguës. Ne pas interdire les IP privées, indispensables à l'usage interne.
- Un changement de destination nécessite des identifiants fournis explicitement pour cette destination ; un champ vide n'autorise pas une récupération implicite de l'ancien secret.
- Empêcher qu'une redirection HTTP transporte clé, mot de passe ou session vers une autre destination. Examiner tous les appels portant ces secrets, pas seulement la première requête.
- Utiliser un instantané cohérent destination/secret pendant le test ; ne pas sauvegarder la configuration sur échec. Respecter la politique existante d'activation des intégrations et expliciter les routes de configuration autorisées.
- Conserver les certificats auto-signés explicitement acceptés. Le durcissement TLS général est hors de cette tâche.

Tests : destination identique acceptée ; destination différente refusée avant tout appel réseau ; clé environnement ; identifiants UniFi self-hosted ; mot de passe Pi-hole omis ; ports/schémas/chemins ambigus ; redirection malveillante ; test échoué sans écriture ; rechargement concurrent sans association de secrets à une autre destination. Utiliser des secrets factices.

Livrer à A5 le contrat d'erreur et les éventuels besoins UI. Ne pas modifier le frontend dans ce lot.

#### A3 — Spécialiste performance : cache borné

Fichiers réservés : `receiver/response_cache.py`, `receiver/tests/test_response_cache.py`.

Objectifs :
- Ajouter une limite explicite d'entrées et une politique d'éviction déterministe ; purger les entrées expirées même si leur clé n'est jamais relue.
- Garder la signature publique de `ttl_cache`, les réexports, les copies défensives, la sécurité multithread et la non-mise en cache des exceptions.
- Justifier une borne adaptée et le coût de la purge ; ne pas verrouiller les traitements DB longs sous le verrou global.
- Une borne d'entrées n'est pas une borne d'octets : documenter cette limite et vérifier la taille maximale des réponses des appelants avant de conclure sur la mémoire.

Tests : horloge simulée, milliers de clés distinctes, purge après expiration, plafond jamais dépassé, éviction attendue, concurrence, copie défensive et exceptions. Aucun `sleep` long ; vérifier que le stockage reste borné, pas seulement que les valeurs expirent.

### Lot 2 — Compléments après le lot 1

État : A4, A5 et A6 intégrés dans la branche de la PR #71. `/api/setup/status` renvoie seulement `setup_complete`, la paire clé UniFi/hôte est lue dans un instantané et écrite dans une transaction lors de l'import, l'UI guide le premier administrateur et garde les erreurs de déconnexion visibles, et les exports CSV neutralisent aussi les segments de formule après séparateur alternatif. La revue avant commit a corrigé une course de cache du Dashboard après déconnexion. Les suites complètes passent.

Traçabilité : la PR #71 était à `e370aaf` avant le lancement. A4, A5 et A6 ont travaillé sur une branche isolée fondée sur cette tête ; leurs modifications ont été regroupées dans `d152655`. La demande du 2026-10-03 autorise leur intégration à la PR #71. Aucun équipement de production n'a été contacté.

#### A4 — Spécialiste API/DB : statut d'installation sans comptage coûteux

Fichiers réservés : `receiver/routes/setup.py`, helper DB strictement nécessaire, tests dédiés au statut et à l'export.

Objectifs :
- Remplacer le comptage exact public par l'information minimale réellement consommée. Rechercher tous les consommateurs avant de choisir présence (`EXISTS`), état stocké ou estimation.
- Ne pas transformer silencieusement un champ `logs_count` exact en estimation : conserver ou faire évoluer explicitement le contrat et son affichage.
- Si un comptage exact reste nécessaire, le séparer du bootstrap public et limiter son coût ; ne pas simplement cacher le problème derrière un TTL court.
- Vérifier après A1 que l'export incluant un secret reste inaccessible anonymement pendant l'installation et interdit aux jetons après activation.
- Corriger l'import de configuration : une **nouvelle** clé UniFi importée doit être associée à l'hôte importé ou effectif dans `unifi_api_key_host`. L'import d'un hôte seul ne doit jamais réassocier l'ancienne clé. Vérifier la compatibilité des sauvegardes existantes.

Point de départ vérifié : `receiver/routes/setup.py:82` appelle encore `count_logs()` pour `logs_count`, alors que `/api/auth/status` ne fait déjà plus ce comptage. Aucun consommateur `logs_count` n'a été trouvé dans `ui/src` ; rechercher aussi les clients externes avant de modifier le contrat. L'import de `setup.py` écrit la clé et l'hôte sans écrire `unifi_api_key_host`.

Tests : statut utilisable avant setup et avec auth active, absence de comptage complet dans le chemin public, contrat explicite pour `logs_count`, export réservé aux droits attendus, mode auth volontairement désactivé conservé, import clé+hôte et import hôte seul. Coordonner tout changement UI avec A5 avant édition.

#### A5 — Spécialiste frontend : erreurs sensibles et déconnexion

Fichiers réservés : `ui/src/App.jsx`, `ui/src/api.js`, `ui/src/components/Login.jsx` ou un écran dédié, `ui/src/components/UniFiConnectionForm.jsx`, `ui/src/components/SettingsPihole.jsx`, `ui/src/lib/sessionCache.js` et tests UI dédiés. A4 ne modifie pas ces fichiers sans transfert explicite.

Objectifs :
- Adapter les formulaires au contrat A2 : quand la destination change, demander de nouveaux identifiants et expliquer le refus sans exposer le secret.
- Avec `AUTH_ENABLED=true` et aucun administrateur, afficher l'enrôlement initial via `/api/auth/setup` avant l'assistant applicatif protégé. Préserver le mode `AUTH_ENABLED=false` et ne pas rouvrir les routes applicatives anonymes.
- Ne pas présenter une déconnexion distante comme réussie si sa requête échoue ; afficher l'échec et permettre de réessayer. Distinguer nettoyage local et révocation serveur.
- Purger les caches de données sensibles à la déconnexion réussie et lors d'un changement d'identité, sans casser la navigation ordinaire.
- Adapter les consommateurs du statut seulement si A4 l'exige. Aucun remaniement visuel général.

Point de départ vérifié : `App.jsx` affiche actuellement l'assistant applicatif dès `setup_complete=false` ; `api.js` expose `authSetup` mais l'UI ne l'appelle pas. Le logout masque l'échec réseau dans `App.jsx`, tandis que `api.js` traite un 401 comme une session déjà expirée. Les formulaires UniFi/Pi-hole permettent encore de supposer qu'un secret sauvegardé suit un nouvel hôte ; `sessionCache.js` ne fournit pas de purge.

Tests : premier administrateur avec et sans secret valide, auth volontairement désactivée, erreur réseau/500 à la déconnexion, 401 déjà expiré, succès avec état nettoyé, aucune réutilisation de données du compte précédent, changement d'hôte nécessitant identifiants, retour d'erreur API intelligible. Exécuter Vitest et le build de production.

#### A6 — Spécialiste exports : neutralisation des formules CSV

Fichiers réservés : `receiver/query_helpers.py`, `receiver/tests/test_query_helpers.py`, tests d'export dédiés. Modifier les routes d'export uniquement après accord de l'orchestrateur.

Contexte : constat complémentaire de la revue parallèle, absent du premier tableau de synthèse. `sanitize_csv_cell` dans `receiver/query_helpers.py` laisse encore passer une chaîne commençant par un chiffre après `-`, même si la suite est une formule. Les exports de `receiver/routes/logs.py` et `receiver/routes/stats.py` l'utilisent. L'exécution dans Excel n'a pas été testée ; revalider avant correction.

Objectifs : n'exempter que les nombres négatifs intégralement valides selon une grammaire documentée, et neutraliser le reste sans altérer les cellules ordinaires. Vérifier les préfixes dangereux et caractères de contrôle déjà couverts.

Tests : `-5`, `-123.45`, `-.5` préservés ; `-1+1` et une formule utilisant une URL factice neutralisés ; autres préfixes de formules, valeurs vides, texte normal et sortie des exports réels. Ne jamais activer une formule contre un service réel.

### Lot 3 — Validation transverse, documentation et dépendances

État : A7 et A8 terminés localement. La revue indépendante a reproduit un transfert des anciens identifiants UniFi self-hosted lors d'un import d'hôte seul ; l'import lie désormais ces identifiants à leur ancien hôte ou refuse le changement si celui-ci est inconnu. Le premier smoke test de l'image a révélé que quatre tables créées par `init.sql` n'appartenaient pas à l'utilisateur exécutant leurs migrations ; la propriété est corrigée seulement pour ces tables lors de l'initialisation d'un volume vierge. Un second smoke test complet passe, y compris après redémarrage. `undici` est mis à jour uniquement dans le verrou npm.

#### A7 — Spécialiste QA sécurité, indépendant des correctifs

Lecture seule des changements A1-A6 ; nouveaux tests de régression possibles dans des fichiers réservés.

- Vérifier les frontières entre installation, sessions, jetons et mode sans authentification.
- Tester les contrats API/frontend et MCP après intégration, notamment l'ensemble vide de droits.
- Refaire les preuves avec modules réels et services factices. Signaler les défauts à l'auteur ; sérialiser les reprises de fichiers.
- Classer les résultats selon l'usage interne ; ne pas transformer une possibilité théorique en exploitation démontrée.

#### A8 — Spécialiste dépendances

Fichiers réservés : `ui/package-lock.json`, `ui/package.json` uniquement si nécessaire.

- Refaire `npm audit` sur la base courante. Lors de l'audit initial, `undici 7.29.0` était concerné par GHSA-3wwx-pv8p-q78v, en développement uniquement ; 7.29.1 était corrigé.
- Appliquer la mise à jour minimale compatible du verrou, sans `audit fix --force` ni montée majeure opportuniste.
- Vérifier audit production et complet, Vitest et build. Ne pas traiter l'absence d'avis npm comme une certification de sécurité.
- Inventorier les vulnérabilités Python et de l'image si les outils sont disponibles ; proposer séparément les changements supplémentaires, sans mise à jour aveugle de tout l'environnement.

#### Orchestrateur — Documentation et intégration

- Mettre à jour les documents pertinents sous `docs/wiki/`, ainsi que `.env.example` seulement si le contrat de configuration change.
- Documenter le parcours d'installation sécurisé, le mode interne sans authentification, les nouvelles contraintes de destination des secrets et les limitations connues.
- Vérifier l'absence de conflit entre les livraisons et conserver des commits séparables par sujet.
- Exécuter la validation finale ci-dessous avant de déclarer les lots terminés.

### Lot 4 — Durcissement optionnel, à lancer explicitement

Ces tâches ne bloquent pas les lots 1 à 3 pour l'usage interne.

**A9 — PostgreSQL embarqué :** propriétaire de `entrypoint.sh`, configuration PostgreSQL et tests conteneur. Remplacer `trust` par une authentification explicite compatible avec les migrations. Tester volume vierge ET volume préexistant, redémarrage, connexion applicative, maintenance locale et mode DB externe. Prévoir sauvegarde et retour arrière ; ne jamais modifier automatiquement un volume de production ni supposer qu'un changement d'initdb répare les volumes existants.

**A10 — Chaîne de construction :** propriétaire du Dockerfile et des workflows. Épingler les actions à des SHA vérifiés, minimiser les permissions par job, vérifier l'intégrité des paquets téléchargés et proposer des scans proportionnés. Vérifier les architectures supportées et le build complet. Ne pas changer simultanément les versions majeures des outils.

**A11 — Réseau et TLS :** évaluation documentaire en lecture seule de la segmentation souhaitée et des options TLS Pi-hole. Ne pas forcer la validation TLS sans parcours viable pour certificats auto-signés. Ne pas modifier le pare-feu, les ports publiés ni les équipements. Les recommandations doivent distinguer réseau d'administration, utilisateurs, IoT et invités sans inventer la topologie réelle.

## 5. Critères de fin et vérifications

- [x] Toutes les tâches du périmètre lancé ont une reproduction, une correction et une revue indépendante.
- [x] Chaque test de sécurité ajouté traverse le code de production concerné.
- [x] Syntaxe de chaque Python modifié et de `entrypoint.sh` vérifiée.
- [x] Suite backend complète : 795 tests réussis avec l'interpréteur de l'environnement préparé.
- [x] Frontend : 141 tests réussis et build Vite de production réussi.
- [x] `git diff --check`, revue du diff et absence de secrets ou fichiers temporaires ajoutés.
- [x] Image construite et smoke test local isolé sur volume vierge : santé, enrôlement, connexion, refus anonyme et redémarrage. Conteneur et volume supprimés.
- [ ] Si A9 est lancé : tests supplémentaires sur volume ancien synthétique et DB externe, sauvegarde/restauration validée.
- [x] Rapport final : voir le bilan du lot 3 ci-dessous.

Pour la suite, suivre les règles du dépôt pour revue externe, limitation des déclenchements et suivi. La PR #71 est déjà ouverte ; vérifier sa CI et ses commentaires avant d'y ajouter un correctif, et regrouper les corrections retenues. Ne pas déclencher de nouvelle revue ou automatisation au seul titre de la mise à jour du plan. Utiliser les outils d'automatisation réellement disponibles au moment du lancement plutôt qu'une commande historique inexistante.

## 6. Prompt pour la suite à instruire

> Revalide la tête, la CI et les commentaires de la PR #71 après l'intégration du lot 3. Examine les quatre commits et le bilan, puis traite les seuls retours confirmés. Ne fusionne pas, ne lance pas le lot 4 et ne déploie pas sans demande distincte. Ne contacte pas les équipements de production.

Le lot 4 reste optionnel et doit être demandé explicitement ; toujours revalider la base Git, respecter les dépendances et isoler les changements.

## 7. Revue de préparation

- [x] Menaces recadrées sur l'usage interne.
- [x] Fichiers partagés et ordre d'intégration identifiés.
- [x] Critères de preuve, compatibilité et validation définis.
- [x] Déploiement et durcissement optionnel séparés des corrections principales.
- [x] Lot 0 exécuté et documenté le 2026-09-30.
- [x] Lot 1 exécuté et proposé dans la PR #71, tête synchronisée à `e370aaf` le 2026-09-30.
- [x] Lot 2 implémenté, vérifié et intégré à la branche de la PR #71 le 2026-10-03 ; aucune validation conteneur ni déploiement.
- [x] Lot 3 exécuté, vérifié et intégré à la branche de la PR #71 le 2026-10-03, sans déploiement.
- [ ] Lot 4 non commencé.

## 8. Bilan du lot 3

La revue A7 a ajouté des tests traversant les vraies routes d'import et le résolveur UniFi, le contrôle des droits MCP effectifs vides et une matrice de courtes cellules CSV réinterprétées avec des séparateurs alternatifs. Le correctif de l'import empêche une clé ou un login historique de suivre silencieusement un nouvel hôte. Sur volume vierge, l'image ne démarrait pas car `sessions` appartenait à `postgres` alors que les migrations s'exécutent comme `unifi` ; les quatre tables de `init.sql` sur lesquelles ces migrations effectuent un DDL reçoivent désormais le bon propriétaire dans la seule branche d'initialisation. Aucun volume préexistant n'a été modifié.

L'audit npm production signale 0 avis. L'audit complet est passé de 8 à 5 avis `high`, tous rattachés à `braces` dans des outils de développement ; npm ne propose pas de correctif compatible au niveau racine. Les scanners Python et image (`pip-audit`, Trivy, Grype, Syft) ne sont pas installés : leur absence n'est pas une preuve d'absence de vulnérabilités. Les avertissements Vite sur la taille du bundle et les imports dynamiques restent présents.

Avant fusion ou déploiement, le retour arrière du lot 3 consiste à retirer ses commits de la PR par des commits de réversion ciblés. L'image et les données du test étaient jetables et ont été nettoyées. Une migration de base préexistante et le durcissement PostgreSQL restent dans le lot 4 optionnel.
