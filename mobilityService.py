import requests
import json
from LevDistance import *
from BenchmarkEvaluation import *
from sinonimiFermate import *
from datetime import datetime

#inizializzo liste
Stop_list = []
Long_list = []
Lat_list = []
IdStop_list = []
Id_list = []

def getStopInfo(Stop_list, Long_list, Lat_list, IdStop_list):
    agency = ["12", "10", "5", "6", "16", "17"]
    for number in agency:
        api = "https://tn.smartcommunitylab.it/core.mobility/getroutes/" #id agency: 12
        api_agency = api + number
        response_agency = requests.get(api_agency).text
        route_info = json.loads(response_agency) 
        route_dict = {} #dizionario ID al posto di una lista in modo che mantengo struttura key:value
        for route_id in route_info:
            #print("La route id è: ", route_id)
            route_dict.update(route_id["id"])
            id = route_dict['id'] # ---> sfruttando la chiave ['id'] genera lista id linee per ricavare fermate
            Id_list.append(id)
            request_stop = "https://tn.smartcommunitylab.it/core.mobility/getstops/" + number
            api_stop = request_stop + "/" + id
            response = requests.get(api_stop).text # salvo il testo dell'oggetto nella variabile risposta 
            if response == '': # serve x gestire linee sospese
                print('Non trova la linea.')
                Id_list.pop() #rimuove ultimo elemento lista Id_list
                continue # continua a cercare le linee con vari id
            response_info = json.loads(response)
            #ESTRAZIONE STOPS --> FERMATE
            for info in response_info:
                stop = info["name"].replace('"', '') # x togliere virgolette
                if stop not in Stop_list:
                    Stop_list.append(stop)
                    Long_list.append(info["longitude"])
                    Lat_list.append(info["latitude"])
                    IdStop_list.append(info["id"])
    return Stop_list, Long_list, Lat_list, IdStop_list
getStopInfo(Stop_list, Long_list, Lat_list, IdStop_list) #RICHIAMO FUNZIONE

# TABELLA CON DATI PRINCIPALI
# for i in range(len(Stop_list)):
#     print(i, Stop_list[i], Long_list[i], Lat_list[i], IdStop_list[i])

def getInfoTime(time):
    ora = time[11:16]
    minuti = time[14:16]
    #print(ora)
    strtime = str(ora)
    #print(strtime)
    orafinale = ""
    cifratemporanea = strtime[0:2]
    cifra = int(cifratemporanea)
    #print(cifra)
    if (cifra < 12):
        orafinale = ora + "AM"
    else:
        time12provv = cifra - 12
        time12 = str(time12provv) + ":" + minuti
        orafinale = time12 + "PM"
    print(orafinale)
    return orafinale

def getInfoSingleJourney(fermata_vicina_partenza, fermata_vicina_arrivo, orafinale):
    # GESTIONE QUERY + FILE JSON
    url = "https://tn.smartcommunitylab.it/core.mobility/plansinglejourney"
    json_input = {
        "to":{
        "lon":"11.139687",
        "stopId":None,
        "name":None,
        "stopCode":None,
        "lat":"46.044758"
        },
        "routeType":"fastest",
        "resultsNumber":1,
        "departureTime":"04:25PM",
        "from":{
        "lon":"11.154592",
        "stopId":None,
        "name":None,
        "stopCode":None,
        "lat":"46.065956"
        },
        "date":"04/22/2022",
        "transportTypes":[
        "BUS",
        "TRAIN"
        ]
    }
    
    #INPUT PARTENZA - LON E LAT
    print("La fermata di partenza è: ", fermata_vicina_partenza)
    for i in range(len(Stop_list)):
        if (fermata_vicina_partenza == Stop_list[i]):
            lon1 = Long_list[i]
            lat1 = Lat_list[i]
            lon_partenza = str(lon1)
            lat_partenza = str(lat1)
            # print("lon_partenza:", lon_partenza)     
            # print("lat_partenza: ", lat_partenza)
            
    #INPUT ARRIVO - LON E LAT
    print("La fermata di arrivo è: ", fermata_vicina_arrivo)
    for i in range(len(Stop_list)):
        if (fermata_vicina_arrivo == Stop_list[i]):
            lon1 = Long_list[i]
            lat1 = Lat_list[i]
            lon_arrivo = str(lon1)
            lat_arrivo = str(lat1)
            # print("lon_arrivo:", lon_arrivo)     
            # print("lat_arrivo: ", lat_arrivo)

    #GESTIONE TEMPORALE
    today = str(datetime.today().strftime('%m/%d/%Y'))
        # str --> trasformazione in stringa
        # datetime.today() --> estrae giorno e ora attuale
        #  """" + strftime(...) --> estrae specifici dati, es in questo caso mese/giorno/anno
    
    #departureTime = str(dpTime)
    
    # AGGIORNAMENTO JSON CON LON/LAT DI PARTENZA/ARRIVO
    json_input.update({"to":{
        "lon":lon_arrivo,
        "stopId":None,
        "name":None,
        "stopCode":None,
        "lat":lat_arrivo
        },
        "routeType":"fastest",
        "resultsNumber":1,
        "departureTime":orafinale,
        "from":{
        "lon":lon_partenza,
        "stopId":None,
        "name":None,
        "stopCode":None,
        "lat":lat_partenza
        },
        "date":today,
        "transportTypes":[
        "TRANSIT"
        ]
    })

    print(json_input)
    res = requests.post(url,json=json_input).text #importante il text perchè permette dopo di caricare la risposta in modo da poter elaborare i dati
    output_Response = json.loads(res)
    print(res)
    print(output_Response)
    percorso = ""
    
    #GESTIONE RISPOSTA
    for informazione in output_Response:
        leg = informazione["leg"] # leg = elementi del percorso (tratte)
        legId = len(leg) # --> legId = rappresenta un elemento del risultato di pianificazione del percorso unico
        # SUDDIVISIONE IN TRATTE (LEG)
        for legId in leg:
            informazioni_trasporto = []
            transport = legId["transport"]
            informazioni_trasporto.append(transport)
            for informazione in informazioni_trasporto:
                type = informazione["type"]
            
            #infoBus
            if(type == "BUS"):                
                informazioni_partenza = []
                informazioni_arrivo = []
                informazioni_extra = []
                informazioni_fare = []
                numero_bus = []
                        
                startime = legId["startime"]/1000
                partenzaf = datetime.fromtimestamp(startime)
                partenza = str(partenzaf)            
                
                endtime = legId["endtime"]/1000 #da convertire
                arrivof = datetime.fromtimestamp(endtime)
                arrivo = str(arrivof)
                
                durata = int(legId["duration"]/60) #perchè è in millisecondi
                hh=int(durata/60)      # hh contiene le ore (2)
                mm=int(durata-hh*60)   # mm contiene i minuti che rimangono (9)
                # printf "%d or%s %d minut%s\n",hh,hh==1?"a":"e",mm,mm==1?"o":"i" # stampa ben fatta
                    
                if (mm == 1):
                    minuti = " minuto"
                else: 
                    minuti = " minuti"
                if (hh == 1):
                    ore = " ora "
                else:
                    ore = " ore "   
                                    
                for informazione in informazioni_trasporto:
                    route = informazione["routeShortName"]
                routeShortName = route
                        
                da = legId["from"]
                informazioni_partenza.append(da)
                for informazione in informazioni_partenza:
                    name_part = informazione["name"].replace('"', '')
                nome_partenzaBUS = name_part
                            
                a = legId["to"]
                informazioni_arrivo.append(a)
                for informazione in informazioni_arrivo:
                    name_arr = informazione["name"].replace('"', '')
                nome_arrivoBUS = name_arr

                extra = legId["extra"]
                informazioni_extra.append(extra)
                
                if extra != None:
                    #print(informazioni_extra)
                    for informazione in informazioni_extra:
                        fare = informazione["fare"]
                        informazioni_fare.append(fare)
                        for informazione_cent in informazioni_fare:
                            cent = informazione_cent["cents"]
                            costo = cent/60
                    costo_biglietto = int(costo)
                
                percorso = percorso + "Devi prendere il bus n° " + str(routeShortName) + " a " + str(nome_partenzaBUS) + " alle " + str(partenza[11:16]) + " che arriva a " + str(nome_arrivoBUS) + " alle ore " + str(arrivo[11:16]) + ". \n"
                percorso = percorso + "La durata stimata è di circa " + str(hh) + str(ore) + str(mm) + str(minuti) + ".\n"
                # + " con un costo di: " + str(costo_biglietto) + "€. \n"

            #infoWalk
            if(type == "WALK"):                
                informazioni_partenza = []
                informazioni_arrivo = []
                informazioni_extra = []
                informazioni_fare = []
                numero_treno = []
                        
                startime = legId["startime"]/1000
                partenzaf = datetime.fromtimestamp(startime)
                partenza = str(partenzaf)
                #print(partenza[11:16])
                
                endtime = legId["endtime"]/1000 #da convertire
                arrivo = datetime.fromtimestamp(endtime)
                durataWALK = int(legId["duration"]/60) #perchè è in secondi
                if (durataWALK == 1):
                    minuti = "minuto"
                else:
                    minuti = "minuti"
                        
                for informazione in informazioni_trasporto:
                    route = informazione["routeShortName"]
                routeShortName = route
                        
                da = legId["from"]
                informazioni_partenza.append(da)
                for informazione in informazioni_partenza:
                    name_part = informazione["name"].replace('"', '')
                nome_partenzaWALK = name_part
                            
                a = legId["to"]
                informazioni_arrivo.append(a)
                for informazione in informazioni_arrivo:
                    name_arr = informazione["name"].replace('"', '')
                nome_arrivoWALK = name_arr
                
                
                da = "da "
                a = "a "
                if (durataWALK > 0):
                    if nome_partenzaWALK == "corner of path and steps":
                        da = "dall'"
                        nome_partenzaWALK = "angolo della strada"
                    if nome_arrivoWALK == "corner of path and steps":
                        a = "all'"
                        nome_arrivoWALK = "angolo della strada"
                    if nome_partenzaWALK == "sidewalk":
                        da = "dal "
                        nome_partenzaWALK = "marciapiede"
                    if nome_arrivoWALK == "sidewalk":
                        a = "al "
                        nome_arrivoWALK = "marciapiede"
                    if nome_partenzaWALK == "service road":
                        da = "dalla "
                        nome_partenzaWALK = "strada"
                    if nome_arrivoWALK == "service road":
                        a = "alla "
                        nome_arrivoWALK = "strada"
                    if nome_partenzaWALK == "underpass":
                        da = "dal "
                        nome_partenzaWALK = "sottopassaggio"
                    if nome_arrivoWALK == "underpass":
                        a = "al "
                        nome_arrivoWALK = "sottopassaggio"
                    if nome_partenzaWALK == "bike path":
                        da = "dalla "
                        nome_partenzaWALK = "pista ciclabile"
                    if nome_arrivoWALK == "bike path":
                        a = "alla "
                        nome_arrivoWALK = "pista ciclabile"
                    percorso = percorso + "Devi camminare per " + str(durataWALK) + " " + str(minuti) + " circa " + str(da) + str(nome_partenzaWALK) + " " + str(a) + str(nome_arrivoWALK) + ". \n"
            
            #infoTrain
            if(type == "TRAIN"):                
                informazioni_partenza = []
                informazioni_arrivo = []
                informazioni_extra = []
                informazioni_fare = []
                numero_bus = []
                        
                startime = legId["startime"]/1000
                partenzaf = datetime.fromtimestamp(startime)
                partenza = str(partenzaf)            
                
                endtime = legId["endtime"]/1000 #da convertire
                arrivof = datetime.fromtimestamp(endtime)
                arrivo = str(arrivof)
                
                durata = int(legId["duration"]/60) #perchè è in millisecondi                
                hh=int(durata/60)      # hh contiene le ore (2)
                mm=int(durata-hh*60)   # mm contiene i minuti che rimangono (9)
                # printf "%d or%s %d minut%s\n",hh,hh==1?"a":"e",mm,mm==1?"o":"i" # stampa ben fatta
                    
                if (mm == 1):
                    minuti = " minuto"
                else: 
                    minuti = " minuti"
                if (hh == 1):
                    ore = " ora "
                else:
                    ore = " ore "
                    
                for informazione in informazioni_trasporto:
                    route = informazione["routeShortName"]
                routeShortNameTRENO = route
                        
                da = legId["from"]
                informazioni_partenza.append(da)
                for informazione in informazioni_partenza:
                    name_part = informazione["name"].replace('"', '')
                nome_partenzaTRENO = name_part
                            
                a = legId["to"]
                informazioni_arrivo.append(a)
                for informazione in informazioni_arrivo:
                    name_arr = informazione["name"].replace('"', '')
                nome_arrivoTRENO = name_arr

                extra = legId["extra"]
                informazioni_extra.append(extra)
                
                if extra != None:
                    #print(informazioni_extra)
                    for informazione in informazioni_extra:
                        fare = informazione["fare"]
                        informazioni_fare.append(fare)
                        for informazione_cent in informazioni_fare:
                            cent = informazione_cent["cents"]
                            costo = cent/60
                    costo_biglietto = int(costo)
                    
                if routeShortNameTRENO == "RG":
                    routeShortNameTRENO = "regionale"
                
                percorso = percorso + "Devi prendere il treno " + str(routeShortNameTRENO) + " a " + str(nome_partenzaTRENO) + " alle " + str(partenza[11:16]) + " che arriva a " + str(nome_arrivoTRENO) + " alle ore " + str(arrivo[11:16]) + ". \n"
                percorso = percorso + "La durata stimata è di circa " + str(hh) + str(ore) + str(mm) + str(minuti) + ".\n"
                # + " con un costo di: " + str(costo_biglietto) + "€. \n"
                
    return percorso

#TABELLA CON DATI PRINCIPALI
# for i in range(len(Stop_list)):
#     print(i, Stop_list[i], Long_list[i], Lat_list[i], IdStop_list[i])

#TABELLA SOLO FERMATE
# for i in range(len(Stop_list)):
#     print(Stop_list[i])

# fermata_corretta = "Povo Piazza Manci"
# stop = "Piazza Povo"
M = ["W", "WS", "C", "CS", "CWS"]

# print("fermata_input: ", fermata_input, "levDistance", "fermata_corretta: ", fermata_corretta)
# for item in M:
#     a = NormStop(fermata_input, item)
#     b = NormStop(fermata_corretta, item)
#     lev = LevDistanceParole(a, b)
#     print(item, "-->        ", a,"    ", lev,"     ", b)

#SelectStop(Stop_list, fermata_input, preprocess)
# for item in M:
#     a = NormStop(fermata_input, item)
#     b = NormStop(stop, item)
#     lev = LevDistanceParole(a, b)
#     print(item, a, "----", b, "----", lev)

# ciclo che, selezionando 5 routine (per parole, lettere o entrambe), calcola la distanza tra la fermata di input in confronto a tutte le fermate che estrae dal database. Dopo aver riportato la fermata più vicina riporta anche la fermata che dovrebbe selezionare, in rapporto alla fermata selezionata dalla routine, per capire perchè seleziona una fermata piuttosto che un'altra.
# for item in M:   
#     a = SelectStop(Stop_list, fermata_input, item)
#     print(a, item)
#     a1 = NormStop(fermata_input, item)
#     b1 = NormStop(a, item)
#     lev1 = LevDistanceParole(a1, b1)
#     c1 = NormStop(fermata_corretta, item)
#     lev2 = LevDistanceParole(a1, c1)
#     print(lev1,"    ", a1,"        ", b1)
#     print(lev2,"    ", a1,"        ", c1)
#     print(" ")
    
# a = NormStop(fermata_input, "W")
# print("W: " + a)
# a = NormStop(fermata_input, "WS")
# print("WS: " + a)
# a = NormStop(fermata_input, "C")
# print("C: " + a)
# a = NormStop(fermata_input, "CS")
# print("CS: " + a)
# a = NormStop(fermata_input, "CWS")
# print("CWS: " + a)

# coppia = fermate.items()
# # print(coppia)
# for item in M:  
#     counterFermate = 0
#     counterCorrette = 0 
#     for elemento in coppia:
#         nf = elemento[0]
#         nu = elemento[1]
#         #print(elemento)
#         #print("La fermata fantasiosa si chiama: ", nf)
#         #nu =  list(elemento.values()) #fermata ufficiale
#         #print("La fermata ufficiale si chiama: ", nu)
#         counterFermate = counterFermate + 1
#         a = SelectStop(Stop_list, nf, item, sinonimi)
#         if (a == nu):
#             counterCorrette = counterCorrette + 1
#             # print(sinonimi)
#             #print("corretto", nu, a, nf)
#         #else:
#             #print("Errore di: ", nu, "confusa con: ", a, "input era: ", nf)
#         accuratezza = 100 * counterCorrette / counterFermate
#         print("Accuratezza parziale: ", accuratezza, counterCorrette, counterFermate, item)
#     print("Accuratezza: ", accuratezza, counterCorrette, counterFermate, item)