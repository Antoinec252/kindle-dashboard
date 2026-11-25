# Fêtes du jour (calendrier français). "+" = Saint, "*" = Sainte, sinon texte affiché tel quel.
SAINTS = {
 1: ["Jour de l'An", "+Basile", "*Geneviève", "+Odilon", "+Édouard", "+Mélaine", "+Raymond", "+Lucien", "*Alix", "+Guillaume",
     "+Paulin", "*Tatiana", "*Yvette", "*Nina", "+Rémi", "+Marcel", "*Roseline", "*Prisca", "+Marius", "+Sébastien",
     "*Agnès", "+Vincent", "+Barnard", "+François de Sales", "Conversion de saint Paul", "*Paule", "*Angèle", "+Thomas d'Aquin", "+Gildas", "*Martine",
     "*Marcelle"],
 2: ["*Ella", "Chandeleur", "+Blaise", "*Véronique", "*Agathe", "+Gaston", "*Eugénie", "*Jacqueline", "*Apolline", "+Arnaud",
     "Notre-Dame de Lourdes", "+Félix", "*Béatrice", "+Valentin", "+Claude", "*Julienne", "+Alexis", "*Bernadette", "+Gabin", "*Aimée",
     "+Damien", "*Isabelle", "+Lazare", "+Modeste", "+Roméo", "+Nestor", "*Honorine", "+Romain", "+Auguste"],
 3: ["+Aubin", "+Charles le Bon", "+Guénolé", "+Casimir", "*Olive", "*Colette", "*Félicité", "+Jean de Dieu", "*Françoise", "+Vivien",
     "*Rosine", "*Justine", "+Rodrigue", "*Mathilde", "*Louise", "*Bénédicte", "+Patrice", "+Cyrille", "+Joseph", "+Herbert",
     "*Clémence", "*Léa", "+Victorien", "*Catherine de Suède", "Annonciation", "*Larissa", "+Habib", "+Gontran", "*Gwladys", "+Amédée",
     "+Benjamin"],
 4: ["+Hugues", "*Sandrine", "+Richard", "+Isidore", "*Irène", "+Marcellin", "+Jean-Baptiste de la Salle", "*Julie", "+Gautier", "+Fulbert",
     "+Stanislas", "+Jules", "*Ida", "+Maxime", "+Paterne", "+Benoît-Joseph", "+Anicet", "+Parfait", "*Emma", "*Odette",
     "+Anselme", "+Alexandre", "+Georges", "+Fidèle", "+Marc", "*Alida", "*Zita", "*Valérie", "*Catherine de Sienne", "+Robert"],
 5: ["Fête du Travail", "+Boris", "Sts Philippe et Jacques", "+Sylvain", "*Judith", "*Prudence", "*Gisèle", "Victoire 1945", "+Pacôme", "*Solange",
     "*Estelle", "+Achille", "*Rolande", "+Matthias", "*Denise", "+Honoré", "+Pascal", "+Éric", "+Yves", "+Bernardin",
     "+Constantin", "+Émile", "+Didier", "+Donatien", "*Sophie", "+Bérenger", "+Augustin", "+Germain", "+Aymar", "+Ferdinand",
     "Visitation"],
 6: ["+Justin", "*Blandine", "+Kévin", "*Clotilde", "+Igor", "+Norbert", "+Gilbert", "+Médard", "*Diane", "+Landry",
     "+Barnabé", "+Guy", "+Antoine de Padoue", "+Élisée", "*Germaine", "+Jean-François Régis", "+Hervé", "+Léonce", "+Romuald", "+Silvère",
     "+Rodolphe", "+Alban", "*Audrey", "+Jean-Baptiste", "+Prosper", "+Anthelme", "+Fernand", "+Irénée", "Sts Pierre et Paul", "+Martial"],
 7: ["+Thierry", "+Martinien", "+Thomas", "+Florent", "+Antoine", "*Mariette", "+Raoul", "+Thibault", "*Amandine", "+Ulrich",
     "+Benoît", "+Olivier", "Sts Henri et Joël", "Fête nationale", "+Donald", "Notre-Dame du Mont-Carmel", "*Charlotte", "+Frédéric", "+Arsène", "*Marina",
     "+Victor", "*Marie-Madeleine", "*Brigitte", "*Christine", "+Jacques", "Sts Anne et Joachim", "*Nathalie", "+Samson", "*Marthe", "*Juliette",
     "+Ignace de Loyola"],
 8: ["+Alphonse", "+Julien Eymard", "*Lydie", "+Jean-Marie Vianney", "+Abel", "Transfiguration", "+Gaétan", "+Dominique", "+Amour", "+Laurent",
     "*Claire", "*Clarisse", "+Hippolyte", "+Évrard", "Assomption", "+Armel", "+Hyacinthe", "*Hélène", "+Jean Eudes", "+Bernard",
     "+Christophe", "+Fabrice", "*Rose de Lima", "+Barthélemy", "+Louis", "*Natacha", "*Monique", "+Augustin", "*Sabine", "+Fiacre",
     "+Aristide"],
 9: ["+Gilles", "*Ingrid", "+Grégoire", "*Rosalie", "*Raïssa", "+Bertrand", "*Reine", "Nativité de Marie", "+Alain", "*Inès",
     "+Adelphe", "+Apollinaire", "+Aimé", "Croix glorieuse", "+Roland", "*Édith", "+Renaud", "*Nadège", "*Émilie", "+Davy",
     "+Matthieu", "+Maurice", "+Constant", "*Thècle", "+Hermann", "Sts Côme et Damien", "+Vincent de Paul", "+Venceslas", "+Michel", "+Jérôme"],
 10: ["*Thérèse de l'Enfant-Jésus", "+Léger", "+Gérard", "+François d'Assise", "*Fleur", "+Bruno", "+Serge", "*Pélagie", "+Denis", "+Ghislain",
     "+Firmin", "+Wilfried", "+Géraud", "+Juste", "*Thérèse d'Avila", "*Edwige", "+Baudouin", "+Luc", "+René", "*Adeline",
     "*Céline", "*Élodie", "+Jean de Capistran", "+Florentin", "+Crépin", "+Dimitri", "*Émeline", "Sts Simon et Jude", "+Narcisse", "*Bienvenue",
     "+Quentin"],
 11: ["Toussaint", "Défunts", "+Hubert", "+Charles", "*Sylvie", "*Bertille", "*Carine", "+Geoffroy", "+Théodore", "+Léon",
     "Armistice 1918", "+Christian", "+Brice", "+Sidoine", "+Albert", "*Marguerite", "*Élisabeth", "*Aude", "+Tanguy", "+Edmond",
     "Présentation de Marie", "*Cécile", "+Clément", "*Flora", "*Catherine", "*Delphine", "+Séverin", "+Jacques de la Marche", "+Saturnin", "+André"],
 12: ["*Florence", "*Viviane", "+François-Xavier", "*Barbara", "+Gérald", "+Nicolas", "+Ambroise", "Immaculée Conception", "+Pierre Fourier", "+Romaric",
     "+Daniel", "*Jeanne-Françoise de Chantal", "*Lucie", "*Odile", "*Ninon", "*Alice", "+Gaël", "+Gatien", "+Urbain", "+Théophile",
     "+Pierre Canisius", "*Françoise-Xavière", "+Armand", "*Adèle", "Noël", "+Étienne", "+Jean", "Saints Innocents", "+David", "+Roger",
     "+Sylvestre"],
}


def fete(d):
    raw = SAINTS[d.month][d.day - 1]
    if raw[0] == "+":
        return "Saint " + raw[1:]
    if raw[0] == "*":
        return "Sainte " + raw[1:]
    return raw
