class AideLexer:

    def index_Error(self, L: int = 0) -> bool:
        if self.index + L < len(self.code_source):
            return True
        return False

    #---------------------------------------------------------------------------------------------
    def espace(self) -> None:
        self.index += 1

    #---------------------------------------------------------------------------------------------
    def retour_ligne(self) -> None:
        self.ligne += 1
        self.index += 1

    #---------------------------------------------------------------------------------------------
    def commentaire(self) -> None:
        self.index += 1
        ligne_depart = self.ligne
        while (
            self.index_Error() and (self.code_source[self.index] not in self._commentaire)
        ):
            if self.code_source[self.index] == "\n":
                self.ligne += 1
            self.index += 1
        
        # ✅ Si on n'a PAS trouvé le délimiteur fermant → erreur
        if not self.index_Error():
            self.erreur(
                "Bloc de commentaire jamais fermé // Unclosed comment block 🙈",
                ligne_depart,
            )
        
        # ✅ consommer le % fermant
        self.index += 1

    #---------------------------------------------------------------------------------------------
    def un_seul_caractere(self) -> None:
        ligne_depart: int = self.ligne
        self.index += 1

        if not self.index_Error():
            self.erreur(
                "Fichier terminé brutalement, inspecte la dernière ligne // File ends abruptly, check the last line 🔍",
            )

        if not self.index_Error(1) or self.code_source[self.index + 1] != "'":
            self.erreur(
                "Entre deux apostrophes '' il faut exactement UN caractère // Between two quotes '' there must be exactly ONE character ✋"
            )

        self.token_append("CARACTERE", self.code_source[self.index], ligne_depart)
        self.index += 2

    #---------------------------------------------------------------------------------------------
    def chaine_caractere(self) -> None:
        ligne_depart: int = self.ligne

        if not self.index_Error():
            self.erreur(
                "Fichier terminé brutalement, inspecte la dernière ligne // File ends abruptly, check the last line 🔍",
            )

        self.index += 1
        depart = self.index

        while (self.index_Error()
               and self.code_source[self.index] != '"'
               and self.code_source[self.index] != "\n"):
            self.index += 1

        if self.index_Error() and self.code_source[self.index] != '"':
            self.erreur(
                "Chaîne non fermée // Unclosed string 🧵",
            )
        if not self.index_Error():
            self.erreur(
                "Fin de fichier anormale // Abnormal end of file ⛔",
            )

        valeur: str = self.code_source[depart:self.index]
        self.index += 1

        self.token_append("CHAINE_CARACTERE", valeur, ligne_depart)

    #---------------------------------------------------------------------------------------------
    def parenthese(self) -> None:
        type_: str = "PAREN_OUVRANT" if self.code_source[self.index] == "(" else "PAREN_FERMANT"
        self.token_append(type_, self.code_source[self.index])
        self.index += 1

    #---------------------------------------------------------------------------------------------
    def numerique(self) -> None:
        depart: int = self.index
        point_utiliser: bool = False

        while (
                self.index_Error()
               and (
                    self.code_source[self.index].isdigit() 
                    or self.code_source[self.index] == "_" 
                    or (
                        self.code_source[self.index] == "." 
                        and not point_utiliser
                        )
                    )
               and self.code_source[self.index] != "\n"):
            if self.code_source[self.index] == "_":
                self.index += 1
                continue
            if self.code_source[self.index] == ".":
                point_utiliser = True
            self.index += 1

        if not self.code_source[self.index - 1].isdigit():
            self.erreur(
                "Les nombres doivent être des entiers ou réels sur une seule ligne // Numbers must be integers or reals on a single line 🔢",
            )

        try:
            valeur = int(self.code_source[depart:self.index]) if not point_utiliser else float(self.code_source[depart:self.index])
            
        except Exception as e:
            self.erreur(
                "Le nombre est mal former",
            )
        self.token_append("NOMBRE", valeur)

    #---------------------------------------------------------------------------------------------
    def symbole(self) -> None:
        valeur_un: str = self.code_source[self.index]
        self.index += 1

        if self.index_Error():
            valeur_deux: str = valeur_un + self.code_source[self.index]
            valide, type_ = self.verificateur(valeur_deux)
            if valide:
                self.index += 1
                self.token_append(type_, valeur_deux)
                return # Je ne sais pas comment me passer du return

        # fallback 1 caractère
        valide, type_ = self.verificateur(valeur_un)
        if not valide:
            self.erreur(
                f"Symbole non reconnu : '{valeur_un}' // Unrecognized symbol: '{valeur_un}' ❓"
            )
        self.token_append(type_, valeur_un)

    #---------------------------------------------------------------------------------------------
    def verificateur(self, valeur: str) -> None:
        valide: bool = True
        type_: str = "identifiant"
        if valeur in self.le_json["mots_cles"]:
            type_ = "mots_cles"
        elif valeur in self.le_json["operateurs_logiques"]:
            type_ = "operateurs_logiques"
        elif valeur in self.le_json["operateurs_comparaison"]:
            type_ = "operateurs_comparaison"
        elif valeur in self.le_json["operateurs_arihmetiques"]:
            type_ = "operateurs_arihmetiques"
        elif valeur in self.le_json["valeur_booleen"]:
            type_ = "valeur_booleen"
        elif valeur in self.le_json["operateurs_affectation"]:
            type_ = "operateurs_affectation"
        elif valeur in self.le_json["separateur"]:
            type_ = "separateur"
        elif valeur in self.le_json["declaration_type"]:
            type_ = "declaration_type"
        else:
            valide = False
        return valide, type_

    #---------------------------------------------------------------------------------------------
    def alpha(self) -> None:
        depart_index: int = self.index

        # ✅ table pré-calculée : mot normalisé -> (type, valeur_canonique)
        table: dict[str, tuple[str, str]] = self.le_json["table_mots"]

        meilleur_fin_i: int = self.index
        meilleur_type: str = "identifiant"
        meilleur_valeur: str = ""

        temp_i: int = self.index
        mots: list[str] = []

        while len(mots) < MAX:
            mot: str = ""
            while (self.index_Error(temp_i)
                   and (self.code_source[temp_i].isalnum() or self.code_source[temp_i] in ("_", "'"))):
                mot += self.code_source[temp_i]
                temp_i += 1

            if mot == "":
                break

            mots.append(mot)
            candidat_norm: str = sans_accents(" ".join(mots))

            if candidat_norm in table:
                meilleur_fin_i = temp_i
                meilleur_type, meilleur_valeur = table[candidat_norm]   # ✅ déballage du tuple

            debut_esp: int = temp_i
            while (index_Error(code_source, temp_i)
                   and code_source[temp_i] in (" ", "\t")):
                temp_i += 1

            if temp_i == debut_esp:
                break

        if meilleur_type == "identifiant":
            mot_brut: str = mots[0]
            valeur: str = sans_accents(mot_brut)
            meilleur_fin_i = depart_index + len(mot_brut)
        else:
            valeur = meilleur_valeur

        self.token_append(meilleur_type, valeur)
        self.index = meilleur_fin_i
