# GRAMMAIRE EVA v1

## CONVENTIONS

- `[X]`        : X est optionnel
- `{X}`        : X répété 0 ou plusieurs fois
- `X | Y`      : soit X, soit Y
- `"texte"`    : token littéral (mot-clé, symbole)
- `<nom>`      : référence à une autre règle
- `'a'`        : le caractère a

Une seule instruction par ligne.
Le champ `ligne` des tokens sert à détecter les fins d'instruction.
Aucun token NEWLINE n'est produit par le lexer.

Toutes les comparaisons et affectations sont NON chaînées :
  a < b < c        → INTERDIT
  a ← b ← c        → INTERDIT


================================================================================
1. PROGRAMME (RACINE)
================================================================================

<programme>  →  <algorithme>

<algorithme> →  "algorithme" <nom>
                { <fonction> | <procedure> }
                [ <bloc_variables> ]
                [ <bloc_constantes> ]
                "debut"
                <instructions>
                "fin"

Contraintes :
  - Un seul algorithme par fichier.
  - Fonctions et procédures avant les déclarations.
  - Déclarations avant "debut".
  - "debut" ... "fin" encadrent le corps principal.

Produit : Algorithme(nom, fonctions, procedures, declarations, corps)


================================================================================
2. FONCTIONS ET PROCÉDURES
================================================================================

<fonction>   →  "fonction" <nom> "(" [ <parametres> ] ")" ":" <type>
                [ <bloc_variables> ]
                [ <bloc_constantes> ]
                "debut"
                <instructions>
                "fin"

<procedure>  →  "procedure" <nom> "(" [ <parametres> ] ")"
                [ <bloc_variables> ]
                [ <bloc_constantes> ]
                "debut"
                <instructions>
                "fin"

<parametres> →  <parametre> { "," <parametre> }

<parametre>  →  <nom> ":" <type>

Contraintes :
  - Une fonction a OBLIGATOIREMENT un type de retour.
  - Une procédure n'a JAMAIS de type de retour.
  - Paramètres séparés par des virgules.

Produit : Fonction(nom, parametres, type_retour, declarations, corps)
          Procedure(nom, parametres, declarations, corps)
          Parametre(nom, type)


================================================================================
3. DÉCLARATIONS
================================================================================

<bloc_variables>  →  "variables"  { <declaration_variable> | <declaration_tableau> }

<bloc_constantes> →  "constantes" { <declaration_constante> | <declaration_tableau_const> }


3.1 VARIABLES
--------------------------------------------------------------------------------

<declaration_variable> →  <liste_noms> ":" <type> [ "←" <expression> ]

<liste_noms> →  <nom> { "," <nom> }

Exemples :
  X : entier
  X, Y, Z : reel
  X : entier ← 0
  A, B : reel ← 3.14

Produit : un DeclarationVariable par nom de la liste.
          DeclarationVariable(nom, type, valeur_initiale)


3.2 CONSTANTES
--------------------------------------------------------------------------------

<declaration_constante> →  <nom> [ ":" <type> ] "←" <expression>

Exemples :
  PI ← 3.14
  PI : reel ← 3.14
  MAX ← 100

Produit : DeclarationConstante(nom, valeur, type)
          type peut être None si non précisé.


3.3 TABLEAUX
--------------------------------------------------------------------------------

Déclaration dans le bloc VARIABLES :

  <declaration_tableau> →  "tableau" <nom> "(" <dimensions> ")" ":" <type>
                           [ "←" "(" <liste_expressions> ")" ]

Déclaration dans le bloc CONSTANTES :

  <declaration_tableau_const> →  "tableau" <nom> ":" <type>
                                 "←" "(" <liste_expressions> ")"

<dimensions>        →  <expression> { "," <expression> }   (1 ou 2 dimensions)
<liste_expressions> →  <expression> { "," <expression> }

Exemples :
  Tableau T(5) : entier
  Tableau T(5) : entier ← (1, 2, 3, 4, 5)
  Tableau M(3, 3) : reel
  Tableau JOURS : chaine ← ("Lundi", "Mardi", "Mercredi")

Produit : DeclarationTableau(nom, type, dimensions, valeurs_initiales)
          dimensions = None pour un tableau constant.


================================================================================
4. INSTRUCTIONS
================================================================================

<instructions> →  { <instruction> }

<instruction>  →  <affectation>
                | <ecrire>
                | <lire>
                | <si>
                | <cas>
                | <pour>
                | <tant_que>
                | <repeter>
                | <retourne>
                | <appel_instruction>


4.1 AFFECTATION
--------------------------------------------------------------------------------

<affectation> →  <cible> "←" <expression>

<cible> →  <nom>
         | <nom> "(" <liste_expressions> ")"

Exemples :
  X ← 5
  X ← X + 1
  T(i) ← 10
  M(i, j) ← 3.14

Produit : Affectation(cible, valeur)
          cible = Identifiant  ou  AppelFonction (converti en Indexation plus tard)


4.2 ECRIRE ET LIRE
--------------------------------------------------------------------------------

<ecrire> →  "ecrire" "(" <liste_expressions> ")"

<lire>   →  "lire" "(" <liste_cibles> ")"

<liste_cibles> →  <cible> { "," <cible> }

Exemples :
  Ecrire("Bonjour")
  Ecrire("x = ", x)
  Ecrire(a + b)
  Lire(X)
  Lire(X, Y)
  Lire(X, N(i))

Produit : Ecrire(arguments)
          Lire(cibles)


4.3 SI
--------------------------------------------------------------------------------

<si> →  "si" <expression> "alors"
        <instructions>
        [ "sinon" <instructions> ]
        "fin si"

Produit : Si(condition, alors, sinon)
          sinon = liste vide si absent.


4.4 CAS
--------------------------------------------------------------------------------

<cas> →  "cas" <expression> "vaut"
         { <branche_cas> }
         [ "sinon" ":" <instructions> ]
         "fin cas"

<branche_cas> →  <expression> ":" <bloc_ou_instruction>

<bloc_ou_instruction> →  <instruction>
                       | "debut" <instructions> "fin"

Règles :
  - Une branche avec UNE SEULE instruction n'a pas besoin de Debut/Fin.
  - Une branche avec PLUSIEURS instructions DOIT être encadrée par Debut ... Fin.
  - Le bloc Debut ... Fin d'une branche ne produit PAS de nœud AST.
    Les instructions sont mises directement dans branche.instructions.
  - Le Sinon n'a JAMAIS besoin de Debut/Fin.
  - Le Sinon n'a pas de "valeur", juste les instructions jusqu'à Fin Cas.

Exemples :

  Cas n vaut
      1 : Ecrire("Lundi")
      2 : Ecrire("Mardi")
      Sinon : Ecrire("Erreur")
  Fin Cas

  Cas age vaut
      "pomme" :
          Debut
              Ecrire("Kilo 2200")
              Ecrire("Reduction 25%")
          Fin
      "banane" :
          Debut
              Ecrire("Kilo 3200")
              Ecrire("Reduction 35%")
          Fin
      Sinon :
          Ecrire("Fruit inconnu")
  Fin Cas

Produit : Cas(expression, branches, sinon)
          BrancheCas(valeur, instructions)


4.5 POUR
--------------------------------------------------------------------------------

<pour> →  "pour" <nom> "←" <expression> "a" <expression>
          "pas" <expression>
          "faire"
          <instructions>
          "fin pour"

Contraintes :
  - Le "pas" est OBLIGATOIRE.

Produit : Pour(indice, debut, fin, pas, corps)


4.6 TANT QUE
--------------------------------------------------------------------------------

<tant_que> →  "tant que" <expression> "faire"
              <instructions>
              "fin tant que"

Produit : TantQue(condition, corps)


4.7 REPETER
--------------------------------------------------------------------------------

<repeter> →  "repeter"
             <instructions>
             "jusqu'a" <expression>

Contraintes :
  - Pas de "fin repeter". La boucle se termine par "jusqu'a" <condition>.

Produit : Repeter(corps, condition)


4.8 RETOURNE
--------------------------------------------------------------------------------

<retourne> →  "retourne" <expression>

Produit : Retourne(valeur)


4.9 APPEL DE PROCÉDURE (instruction)
--------------------------------------------------------------------------------

<appel_instruction> →  <nom> "(" <liste_expressions> ")"

Produit : AppelInstruction(nom, arguments)


================================================================================
5. EXPRESSIONS
================================================================================

<expression> →  <ou_expr>

<ou_expr>       →  <et_expr> { "ou" <et_expr> }
<et_expr>       →  <non_expr> { "et" <non_expr> }
<non_expr>      →  "non" <non_expr>
                 | <comparaison>
<comparaison>   →  <additif> [ <op_comp> <additif> ]
<additif>       →  <multiplicatif> { ( "+" | "-" ) <multiplicatif> }
<multiplicatif> →  <puissance> { ( "*" | "/" | "div" | "mod" ) <puissance> }
<puissance>     →  <unaire> [ "^" <puissance> ]
<unaire>        →  "-" <unaire>
                 | <primaire>

<primaire>      →  <nombre>
                 | <chaine>
                 | <caractere>
                 | <booleen>
                 | <appel_fonction>
                 | <identifiant>
                 | "(" <expression> ")"

<appel_fonction> →  <nom> "(" <liste_expressions> ")"

<op_comp> →  "=" | "<" | ">" | "<=" | ">=" | "<>"


Priorités (de la plus forte à la plus faible) :

  Niveau 1 :  ^                   droite → gauche
  Niveau 2 :  * / div mod         gauche → droite
  Niveau 3 :  + -                 gauche → droite
  Niveau 4 :  = < > <= >= <>      gauche → droite  (non chaîné)
  Niveau 5 :  non                 droite → gauche
  Niveau 6 :  et                  gauche → droite
  Niveau 7 :  ou                  gauche → droite


Exemples :

  2 + 3 * 4          →  OperationBinaire("+", Nombre(2),
                          OperationBinaire("*", Nombre(3), Nombre(4)))

  2 ^ 3 ^ 2          →  OperationBinaire("^", Nombre(2),
                          OperationBinaire("^", Nombre(3), Nombre(2)))

  non x et y         →  OperationBinaire("et",
                          OperationUnaire("non", Identifiant("x")),
                          Identifiant("y"))

  a ou b et c        →  OperationBinaire("ou",
                          Identifiant("a"),
                          OperationBinaire("et", Identifiant("b"), Identifiant("c")))


================================================================================
6. DÉCISIONS DE DESIGN
================================================================================

6.1 APPEL vs INDEXATION

  Le parseur produit TOUJOURS AppelFonction pour un nom(...) en position d'expression.
  La distinction AppelFonction / Indexation est faite par la phase sémantique
  (qui connaît les déclarations).

  Conséquence : N(i) et fib(i) produisent le même nœud AppelFonction en sortie du parseur.

  Idem pour la cible d'une affectation : T(i) ← 5 produit
      Affectation(cible=AppelFonction(nom="T", args=[...]), valeur=...)
  La phase sémantique convertit la cible en Indexation si T est un tableau.

6.2 SÉPARATION DES INSTRUCTIONS

  Aucun token NEWLINE n'est produit par le lexer.
  Le parseur utilise le champ ligne des tokens :
    - Chaque fonction de parsing d'instruction mémorise la ligne de départ.
    - À la fin, elle vérifie que le token courant est sur une ligne différente,
      ou qu'il s'agit d'un marqueur de fin de bloc (Fin Si, Fin, Sinon, etc.).
    - Sinon → erreur "deux instructions sur la même ligne".

6.3 GESTION DES ERREURS

  Le parseur s'arrête à la PREMIÈRE erreur rencontrée.
  Aucune récupération.

6.4 MARQUEURS DE FIN DE BLOC

  Les mots-clés suivants NE produisent PAS de nœud AST :
    - "debut", "fin"       (délimitent un bloc)
    - "alors", "faire"     (séparent condition et corps)
    - "sinon"              (dans Si et Cas)
    - "jusqu'a"            (dans Repeter)
    - "fin si", "fin cas", "fin pour", "fin tant que"

  Ce sont des tokens consommés par le parseur pour savoir où il en est.
  L'information structurelle est portée par les nœuds eux-mêmes.


================================================================================
7. NOEUDS AST PRODUITS
================================================================================

Structure :
  Algorithme, Fonction, Procedure, Parametre

Déclarations :
  DeclarationVariable, DeclarationConstante, DeclarationTableau

Instructions :
  Affectation, Ecrire, Lire, Si, Cas, BrancheCas,
  Pour, TantQue, Repeter, Retourne, AppelInstruction

Expressions :
  Nombre, ChaineCaractere, Caractere, Booleen, Identifiant,
  OperationBinaire, OperationUnaire, AppelFonction, Indexation


================================================================================
8. EXEMPLE COMPLET
================================================================================

Source :

  Algorithme Maximum
  Variables
      X, Y, Max : reel
  Debut
      Ecrire("Entrez deux valeurs : ")
      Lire(X, Y)
      Max ← X
      Si Max < Y Alors
          Max ← Y
      Fin Si
      Ecrire("Le maximum est : ", Max)
  Fin

AST (simplifié) :

  Algorithme(
    nom="Maximum",
    fonctions=[],
    procedures=[],
    declarations=[
      DeclarationVariable("X", "reel", None),
      DeclarationVariable("Y", "reel", None),
      DeclarationVariable("Max", "reel", None),
    ],
    corps=[
      Ecrire(arguments=[ChaineCaractere("Entrez deux valeurs : ")]),
      Lire(cibles=[Identifiant("X"), Identifiant("Y")]),
      Affectation(cible=Identifiant("X"), valeur=Identifiant("X")),
      Si(
        condition=OperationBinaire("<", Identifiant("Max"), Identifiant("Y")),
        alors=[Affectation(cible=Identifiant("Max"), valeur=Identifiant("Y"))],
        sinon=[]
      ),
      Ecrire(arguments=[
        ChaineCaractere("Le maximum est : "),
        Identifiant("Max")
      ])
    ]
  )