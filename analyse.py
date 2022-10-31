#!/usr/bin/env python

# Analyse des accidents corporels de la circulation à partir des fichiers csv open data
# - télécharger les fichiers csv et les mettre dans le même dossier que ce script
# https://www.data.gouv.fr/en/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2019/

import sys
import argparse
import glob

parser = argparse.ArgumentParser(
        description='Analyse des accidents corporels de la circulation à partir des fichiers csv open data')
parser.add_argument(
        '--commune', '-c',
        type=str,
        default=None,
        help='Commune à analyser')
parser.add_argument(
        '--departement', '-d',
        type=str,
        default=None,
        help='Département à analyser')
parser.add_argument(
        '--annee', '-a',
        type=int,
        default=None,
        required=True,
        help='Année')
args = parser.parse_args()

commune = args.commune
annee = args.annee
departement = args.departement
delim = ';'

if commune == None and departement == None:
    raise ValueError('soit commune soit département doit être spécifié')

if annee < 2019:
    raise ValueError('ça marche pas pour les années avant 2019 désolé')

id_acc = []

accidents = {}

gravite = {'1' : 'indemne', '2' : 'tué', '3' : 'grave', '4' : 'léger', ' -1' : 'inconnu'}

vehicules = {
0 : 'Indéterminable',
1 : 'Bicyclette',
2 : 'Cyclomoteur <50cm3',
3 : 'Voiturette (Quadricycle à moteur carrossé) (anciennement voiturette ou tricycle à moteur)',
4 : 'Référence inutilisée depuis 2006 (scooter immatriculé)',
5 : 'Référence inutilisée depuis 2006 (motocyclette)',
6 : 'Référence inutilisée depuis 2006 (side-car)',
7 : 'VL seul',
8 : 'Référence inutilisée depuis 2006 (VL + caravane)',
9 : 'Référence inutilisée depuis 2006 (VL + remorque)',
10 : 'VU seul 1,5T <= PTAC <= 3,5T avec ou sans remorque (anciennement VU seul 1,5T <= PTAC <= 3,5T)',
11 : 'Référence inutilisée depuis 2006 (VU (10) + caravane)',
12 : 'Référence inutilisée depuis 2006 (VU (10) + remorque)',
13 : 'PL seul 3,5T <PTCA <= 7,5T',
14 : 'PL seul > 7,5T',
15 : 'PL > 3,5T + remorque',
16 : 'Tracteur routier seul',
17 : 'Tracteur routier + semi-remorque',
18 : 'Référence inutilisée depuis 2006 (transport en commun)',
19 : 'Référence inutilisée depuis 2006 (tramway)',
20 : 'Engin spécial',
21 : 'Tracteur agricole',
30 : 'Scooter < 50 cm3',
31 : 'Motocyclette > 50 cm3 et <= 125 cm3',
32 : 'Scooter > 50 cm3 et <= 125 cm3',
33 : 'Motocyclette > 125 cm3',
34 : 'Scooter > 125 cm3',
35 : 'Quad léger <= 50 cm3 (Quadricycle à moteur non carrossé)',
36 : 'Quad lourd > 50 cm3 (Quadricycle à moteur non carrossé)',
37 : 'Autobus',
38 : 'Autocar',
39 : 'Train',
40 : 'Tramway',
41 : '3RM <= 50 cm3',
42 : '3RM > 50 cm3 <= 125 cm3',
43 : '3RM > 125 cm3',
50 : 'EDP à moteur',
60 : 'EDP sans moteur',
80 : 'VAE',
99 : 'Autre véhicule'
}

intersection =  {
 1 : 'Hors intersection',
 2 : 'Intersection en X',
 3 : 'Intersection en T',
 4 : 'Intersection en Y',
 5 : 'Intersection à plus de 4 branches',
 6 : 'Giratoire',
 7 : 'Place',
 8 : 'Passage à niveau',
 9 : 'Autre intersection'
}
conditions_atmos = {
-1 : 'Non renseigné',
 1 : 'Normale',
 2 : 'Pluie légère',
 3 : 'Pluie forte',
 4 : 'Neige - grêle',
 5 : 'Brouillard - fumée',
 6 : 'Vent fort - tempête',
 7 : 'Temps éblouissant',
 8 : 'Temps couvert',
 9 : 'Autre'
}

type_de_collision = {
-1 : 'Non renseigné',
 1 : 'Deux véhicules - frontale',
 2 : 'Deux véhicules – par l’arrière',
 3 : 'Deux véhicules – par le coté',
 4 : 'Trois véhicules et plus – en chaîne',
 5 : 'Trois véhicules et plus - collisions multiples',
 6 : 'Autre collision',
 7 : 'Sans collision'
}

def get_header(line):
    h = line.rstrip().replace('"', '').split(delim)
    h = dict(zip(h, range(len(h))))
    return h

# En 2021 il y a une coquille dans le nom du fichier
filelist = glob.glob('car*cteristiques-' + str(annee) + '.csv')
with open(filelist[0]) as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(delim)
        try:
            com = data[head['com']]
            dep = data[head['dep']]
        except:
            break
        if com == commune or dep == departement:
            Num_Acc = data[head['Num_Acc']]
            id_acc.append(Num_Acc)
            accidents[Num_Acc] = {}
            accidents[Num_Acc]['lat'] = data[head['lat']].replace(',','.')
            accidents[Num_Acc]['long'] = data[head['long']].replace(',','.')
            accidents[Num_Acc]['usagers'] = []
            accidents[Num_Acc]['catv'] = []
            accidents[Num_Acc]['col'] = data[head['col']]
            accidents[Num_Acc]['int'] = data[head['int']]
            accidents[Num_Acc]['atm'] = data[head['atm']]
            accidents[Num_Acc]['col'] = data[head['col']]

print('Nombre d\'accidents dans la zone = %d' % len(accidents))

velos = []

with open('vehicules-' + str(annee) + '.csv') as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(delim)
        try:
            Num_Acc = data[head['Num_Acc']]
        except:
            break
        if not Num_Acc in id_acc:
            continue
        catv = data[head['catv']]
        id_vehicule = data[head['id_vehicule']]
        accidents[Num_Acc]['catv'].append(catv)
        if catv == '1' or catv == '80':
            velos.append(id_vehicule)

print('Nombre de vélos impliqués = %d' % len(velos))

cyclistes = []

with open('usagers-' + str(annee) + '.csv') as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(delim)
        try:
            Num_Acc = data[head['Num_Acc']]
        except:
            break
        if not Num_Acc in id_acc:
            continue
        catu = data[head['catu']]
        grav = gravite[data[head['grav']]]
        id_vehicule = data[head['id_vehicule']]
        an_nais = data[head['an_nais']]
        accidents[Num_Acc]['usagers'].append([catu, grav, an_nais])
        if id_vehicule in velos and catu != '3':
            cyclistes.append([Num_Acc, grav,an_nais])

print('Nombre de cyclistes = %d' % len(cyclistes))

fvelo = open('pietons_x_velo.csv', 'w')
fveh = open('pietons_x_vehicule.csv', 'w')
fvelo.write("lat;long;grav;vehicules;intersection;cond_atmos;annee_naissance\n")
fveh.write("lat;long;grav;vehicules;intersection;cond_atmos;annee_naissance\n")

for v in accidents.values():
    catv = v['catv'].copy()
    veh = [vehicules[int(x)] for x in catv]
    veh = ' x '.join('\'{0}\''.format(w) for w in veh)
    inter = intersection[int(v['int'])]
    atm = conditions_atmos[int(v['atm'])]
    # EDP ne nous intéresse pas
    while '50' in catv:
        catv.remove('50')
    while '60' in catv:
        catv.remove('60')
    if len(catv) == 0:
        continue
    f = None
    while '1' in catv:
        f = fvelo
        catv.remove('1')
    while '80' in catv:
        f = fvelo
        catv.remove('80')
    if len(catv) > 0:
        f = fveh
    for u in v['usagers']:
        if u[0] == '3':
            f.write('%s;%s;%s;%s;%s;%s;%s\n' % (v['lat'], v['long'],u[1],veh,inter,atm,u[2]))
            #print(v)

with open('cyclistes.csv', 'w') as f:
    f.write("lat;long;grav;vehicules;intersection;cond_atmos;annee_naissance\n")
    for Num_Acc, grav, an_nais in cyclistes:
        v = accidents[Num_Acc]
        catv = v['catv'].copy()
        while '1' in catv:
            catv.remove('1')
        while '80' in catv:
            catv.remove('80')
        if len(catv) > 0:
            veh = [vehicules[int(x)] for x in catv]
            veh = ' x '.join('\'{0}\''.format(w) for w in veh)
            inter = intersection[int(v['int'])]
            atm = conditions_atmos[int(v['atm'])]
            f.write('%s;%s;%s;%s;%s;%s;%s\n' % (v['lat'], v['long'],grav,veh,inter,atm,an_nais))

