from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet
from mobilityService import *
import datetime as dt

class ActionStopApi(Action):
    
    def name(self) -> Text:
        return "action_stop_api"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        preprocess = "WS"
        dispatcher.utter_message(text=f"{dt.datetime.now()}")
      
        input_partenza = tracker.get_slot("input_partenza")        
        input_arrivo = tracker.get_slot("input_arrivo")
        time = tracker.get_slot("time")
            
        """Gestione risposta con itinerario completo"""                
        fermata_vicina_partenza = SelectStop(Stop_list, input_partenza, preprocess, sinonimi)
        fermata_vicina_arrivo = SelectStop(Stop_list, input_arrivo, preprocess, sinonimi)
        # dispatcher.utter_message(text = f"DEBUG La fermata riconosciuta da Rasa è partenza: {input_partenza} e arrivo: {input_arrivo}.")
        # dispatcher.utter_message(text = f"DEBUG La fermata py di partenza è {fermata_vicina_partenza} e quella di arrivo è {fermata_vicina_arrivo} con partenza ad ore {time}")
        dispatcher.utter_message(text = f"La fermata di partenza riconosciuta è {fermata_vicina_partenza} e quella di arrivo è {fermata_vicina_arrivo}.")
        
        if fermata_vicina_partenza == fermata_vicina_arrivo:
            dispatcher.utter_message(text = f"Sono confuso... ho capito che la fermata di partenza è: {fermata_vicina_partenza} e la fermata di arrivo è: {fermata_vicina_arrivo}. Prova a correggere il dato sbagliato!")
        else: 
            orafinale = getInfoTime(time)
            percorso = getInfoSingleJourney(fermata_vicina_partenza, fermata_vicina_arrivo, orafinale)
            print(percorso)
            dispatcher.utter_message(text = f"{percorso}")
            dispatcher.utter_message(
                template="utter_nuovo_itinerario"
            )
        return [SlotSet("input_partenza", fermata_vicina_partenza), SlotSet("input_arrivo", fermata_vicina_arrivo), SlotSet("time", time)]
    
class ActionResetAllSlots(Action):
    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text=f"{dt.datetime.now()}")
        return [AllSlotsReset()]