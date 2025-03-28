# Projet Programmation par Contraintes

## Introduction

Ce projet a pour but de vous permettre d'appliquer concrètement les méthodes et outils vus en cours sur les problématiques de recherche (Search), de programmation par contraintes (CSP), et de raisonnement logique avancé (SAT/SMT). Vous serez amenés à résoudre des problèmes réels ou réalistes à l'aide de ces techniques en développant un projet complet, depuis la modélisation jusqu'à la solution opérationnelle.


## Modalités du projet

### Livrables

Chaque groupe devra forker ce dépôt  Git et déposer son travail dans un répertoire dédié du dépôt. Ce répertoire contiendra :

- Le code source complet, opérationnel, documenté et maintenable (en Python, C#, C++, ou autre).
- Le matériel complémentaire utilisé pour le projet (datasets, scripts auxiliaires, etc.).
- Les slides utilisés lors de la présentation finale.
- Un notebook explicatif détaillant les étapes du projet, les choix de modélisation, les expérimentations et les résultats obtenus.

Les livraisons se feront via des **pull requests**, qui devront être régulièrement mises à jour durant toute la durée du projet de sorte que l'enseignant puisse suivre l'avancement et éventuellement apporter des retours et de sorte que tous les élèves aient pu prendre connaissance des travaux des autres groupes avant la soutenance avec évaluation collégiale.

### Présentation

- Présentation orale finale avec support visuel (slides).
- Démonstration de la solution opérationnelle devant la classe.

### Évaluation

- Évaluation collégiale : chaque élève évaluera les autres groupes en complément de l’évaluation réalisée par l’enseignant.
- Critères : clarté, originalité, robustesse de la solution, qualité du code, pertinence des choix méthodologiques et organisation.

## Utilisation des LLMs

### Outils à disposition

Pour faciliter la réalisation du projet, vous aurez accès à plusieurs ressources avancées :

- **Plateforme Open-WebUI** : intégrant des modèles d'intelligence artificielle d'OpenAI et locaux très performants, ainsi que des plugins spécifiques et une base de connaissances complète alimentée par la bibliographie du cours (indexée via ChromaDB, taper # en conversation pour invoquer les KB).
- **Clés d'API OpenAI et locales** : mise à votre disposition pour exploiter pleinement les capacités des modèles GPT dans vos développements.
- **Notebook Agentique** : un notebook interactif permettant d'automatiser la création ou la finalisation de vos propres notebooks, facilitant ainsi la structuration et l'amélioration de vos solutions.

### Combinaison LLM et CSP

Vous avez également la possibilité d'intégrer les Large Language Models (LLMs) directement dans votre projet CSP afin d'en étendre significativement les capacités, via :

- Une utilisation directe des LLM pour assister la conception ou la résolution de CSP complexes.
- Le recours au "function calling" : fournir à un LLM un accès direct à votre CSP, permettant ainsi au modèle de piloter la résolution du problème de manière plus flexible et intuitive. Le notebook agentique fourni constitue un exemple pratique et efficace de cette méthodologie légère mais puissante. La normalisation en cours des MCPs constitue également un excellent exemple d'application de cette approche (vous développez un MCP utilisant la PrCon dans le cadre de votre projet).

## 8. Calendrier sportif (Sports Tournament Scheduling)  
Élaboration du calendrier de rencontres d’un championnat (par ex. tournoi toutes rondes en football), en respectant de multiples contraintes: alternance domicile/extérieur, disponibilités de stades, équité entre équipes (pas plus de X déplacements consécutifs, etc.). Ces problèmes, très complexes, ont motivé de nombreux travaux en CP. Par exemple, l’ordonnancement d’un tournoi « round-robin » peut se modéliser par contrainte avec des variables représentant qui rencontre qui à chaque journée, et des *global constraints* pour éviter les « breaks » (deux matchs Domicile ou Extérieur de suite) ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=consider%20single%20round,to%20e%0Eciently%20prove%20this%20result)). La CP a permis de prouver des bornes théoriques, comme le nombre minimal de « breaks » (n–2 pour n équipes) en quelques secondes, exploitant la propagation sur des contraintes globales spécifiques ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=once%20during%20all%20the%20periods,powerful%20%0Cltering%20algorithms%20are%20associated)). Plus généralement, la littérature sur le scheduling sportif montre l’intérêt de CP pour gérer les règles complexes imposées par les ligues ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=Sport%20scheduling%20problems%20is%20an,Some%20systems%20dedicated%20to)).  
**Références :** Régin (CP 2008), *Minimizing breaks in sports schedules* – modèle CP pour tournoi rondes simples ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=consider%20single%20round,to%20e%0Eciently%20prove%20this%20result)) ([sls.dvi](http://cse.unl.edu/~choueiry/Documents/Regin/minbreak.pdf#:~:text=once%20during%20all%20the%20periods,powerful%20%0Cltering%20algorithms%20are%20associated)); Schaerf (1999), *Sports scheduling* – revue d’approches; *ITC 2021 Sports Scheduling Track* (compétition utilisant CP et métaheuristiques).

