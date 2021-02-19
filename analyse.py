#!/usr/bin/env python

# Analyse des accidents corporels de la circulation a partir des fichiers csv open data
# - telecharger les fichiers csv depuis :
# https://www.data.gouv.fr/en/datasets/bases-de-donnees-annuelles-des-accidents-corporels-de-la-circulation-routiere-annees-de-2005-a-2019/
# - changer la commune et l'annee :

commune = '92012'
annee = 2019

id_acc = []

accidents = {}

gravite = {'1' : 'indemne', '2' : 'tue', '3' : 'grave', '4' : 'leger'}

def get_header(line):
    h = line.rstrip().replace('"', '').split(';')
    h = dict(zip(h, range(len(h))))
    return h

with open('caracteristiques-' + str(annee) + '.csv') as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(';')
        try:
            com = data[head['com']]
        except:
            break
        if com == commune:
            Num_Acc = data[head['Num_Acc']]
            id_acc.append(Num_Acc)
            accidents[Num_Acc] = {}
            accidents[Num_Acc]['lat'] = data[head['lat']].replace(',','.')
            accidents[Num_Acc]['long'] = data[head['long']].replace(',','.')
            accidents[Num_Acc]['usagers'] = []
            accidents[Num_Acc]['catv'] = []

#print id_acc

velos = []

with open('vehicules-' + str(annee) + '.csv') as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(';')
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

cyclistes = []

with open('usagers-' + str(annee) + '.csv') as f:
    head = get_header(f.readline())
    for l in f:
        data = l.rstrip().replace('"', '').split(';')
        try:
            Num_Acc = data[head['Num_Acc']]
        except:
            break
        if not Num_Acc in id_acc:
            continue
        catu = data[head['catu']]
        grav = gravite[data[head['grav']]]
        id_vehicule = data[head['id_vehicule']]
        accidents[Num_Acc]['usagers'].append([catu, grav])
        if id_vehicule in velos and catu != '3':
            cyclistes.append([Num_Acc, grav])


#print accidents

with open('pietons.csv', 'w') as f:
    f.write("lat,long,grav,catv\n")
    for v in accidents.values():
        catv = v['catv']
        if '1' in catv or '80' in catv:
            catv = 'velo'
        else:
            catv = 'vehicule'
        for u in v['usagers']:
            if u[0] == '3':
                f.write('%s,%s,%s,%s\n' % (v['lat'], v['long'],u[1],catv))

with open('cyclistes.csv', 'w') as f:
    f.write("lat,long,grav\n")
    for Num_Acc, grav in cyclistes:
        v = accidents[Num_Acc]
        f.write('%s,%s,%s\n' % (v['lat'], v['long'],grav))

