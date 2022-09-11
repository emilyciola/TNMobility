def NormStop(fermata, preprocess):
    #W, WS, C, CS, CWS W = word, C = char, S = sort
    fermata = fermata.lower()
    fermata = fermata.strip() # strip --> toglie spazio inizio e fine stringa
    #fermata = "Povo Piazza Manci" #input stringa
    if preprocess == "W":
        return fermata
    if preprocess == "WS":
        fermataL = fermata.split()
        fermataL.sort()
        fermata_n = ' '.join(fermataL)
        return fermata_n
    if preprocess == "C":
        fermata_ = fermata.replace(" ", "_")
        fermataI = list(fermata_)
        fermataC = ' '.join(fermataI)
        return fermataC
    if preprocess == "CS":
        fermata_ = fermata.replace(" ", "_")
        fermataI = list(fermata_)
        fermataI.sort()
        fermataB = ' '.join(fermataI)
        return fermataB
    if preprocess == "CWS":
        fermataL = fermata.split()
        fermataL.sort()
        fermata_n = ' '.join(fermataL)
        fermata_ = fermata_n.replace(" ", "_")
        fermataI = list(fermata_)
        fermataW = ' '.join(fermataI)
        return fermataW
        
def LevDistanceParole(fermata_input, fermata_vicina):
    dist = [] #inizializzo array per poter calcolare dopo la distanza
    fV1 = "- " + fermata_input #fV --> fermata input
    fC1 = "- " + fermata_vicina #fC --> fermata controllo
    a = fV1.split() # split --> separa i caratteri della stringa e li posiziona in array
    b = fC1.split()
    l_a = len(a) + 1 # calcolo la lunghezza della stringa A
    #print(l_a)
    #print(a[0], b[0]) # stampo le due stringhe
    #print(a, b)

    #INIZIALIZZO INDICI E VARIABILI
    for i in range(0, len(a) + 1):
        for j in range(0, len(b) + 1):
            dist.append(0)
    for i in range(len(a)):
        dist[i] = i
    for j in range(len(b)):
        dist[j * l_a] = j

    #INIZIO IL CONFRONTO
    for i in range(1, len(a)):
        for j in range(1, len(b)):
            #CONFRONTO A e B
            if (a[i] == b[j]):
                m = 0
            else:
                m = 1
            m1 = dist[(i - 1) + (j - 1) * l_a] + m
            m2 = dist[(i) + (j - 1) * l_a] + 1
            m3 = dist[(i - 1) + (j) * l_a] + 1
            if (m1 < m2):
                if (m1 < m3):
                    dist[i + j * l_a] = m1 
                else: 
                    dist[i + j * l_a] = m3
            else:
                if (m2 < m3):
                    dist[i + j * l_a] = m2
                else:
                    dist[i + j * l_a] = m3
            levdist = (dist[i + j * l_a])
            #print(m, i, a[i], j, b[j], dist[i + j * l_a])            
    return levdist

def SelectStop(Stop_list, fermata_input, preprocess, sinonimi):
    coppia_fermate = sinonimi.items()
    min_dist = 1000
    normFermata_input = NormStop(fermata_input, preprocess)
    for stop in Stop_list: #gestione nf e nu
        normStop = NormStop(stop, preprocess)   
        dist = LevDistanceParole(normFermata_input, normStop)
        # print(stop, dist)
        if (dist < min_dist):
            #print(stop, dist)
            min_dist = dist
            fermata_vicina = stop
    for stop in coppia_fermate:
        sinonimo = stop[0]
        nomeuff = stop[1]
        normStop = NormStop(sinonimo, preprocess)   
        dist = LevDistanceParole(normFermata_input, normStop)
        if (dist < min_dist):
            #print(stop, dist)
            min_dist = dist
            fermata_vicina = nomeuff
    # print("Il preprocess è: " + preprocess)
    # print("La distanza minima è: ", min_dist)
    # print("La fermata input è LevDistanceParole: " + normFermata_input)
    print("La fermata più vicina è: " + fermata_vicina)
    return fermata_vicina