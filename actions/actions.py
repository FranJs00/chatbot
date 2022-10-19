# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction


from .utils import JsonManager, TimeManager
from .prolog_consults import PrologConsult


file = JsonManager()
time = TimeManager()

prolog = PrologConsult()


class ConfirmSurname(Action):
    def name(self) -> Text:
        return "action_confirm_surname"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        surname = next(tracker.get_latest_entity_values("surname")).capitalize()

        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        info = file.getById(fromData["id"])

        if fromData["last_name"]:
            return []

        info["last_name"] = surname

        file.saveById(fromData["id"], info)
        dispatcher.utter_message(text = "Buenisimo " + info["first_name"])
        return []




class ShowSubjects(Action):
    def name(self) -> Text:
        return "action_show_subjects"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        result = prolog.consultCourses()
        mensaje = "Actualmente estoy cursando: \n"
        for x in result:
            mensaje += str(x["X"]) + '\n'
        dispatcher.utter_message(text = mensaje)
                    
        return []

class ShowAgenda(Action):
    def name(self) -> Text:
        return "action_what_doing"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        result = prolog.consultAgenda(time.getDay(), time.getHour())
        if result:
            mensaje = 'Actualmente estoy ' + str(result[0]["Actividad"])
        else:
            mensaje = 'Estoy viendo que hacer, probablemente adelante algo de la universidad o trabaje'
        dispatcher.utter_message(text = mensaje)
        return[]

class ConfirmTopic(Action):
    def name(self) -> Text:
        return "action_handle_topics"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        actual_topic = tracker.get_slot("actual_topic")

        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        
        file.saveDataByKey(fromData["id"], "actual_topic", actual_topic)

        return []




class ResponseMood(Action):
    def name(self) -> Text:
        return "action_mood"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mood = tracker.get_slot("mood")

        if mood == 'good':
            message = "Me alegro!"
        if mood == 'bad':
            message = "Uy, sea lo que sea, espero que mejore"
        if mood == 'neutral':
            message = "Espero no pase nada malo"
        
        dispatcher.utter_message(text = message)
        return []

class GetTelegramData(Action):
    def name(self) -> Text:
        return "action_get_tg_data"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        info = file.getById(fromData["id"])

        if info:
            return [SlotSet("who_is_chatting", fromData["first_name"])]

        newData = {}
        newData["first_name"] = fromData["first_name"]
        lastname = fromData.get("last_name")
        print("lastname", lastname, tracker.get_slot("surname_check"))

        newData["last_name"] = lastname
        file.saveById(fromData["id"], newData)
        if not lastname:
            print("No tiene apellido")
            return [SlotSet("surname_check", True)]

        return []

class WhoIsTalking(Action):
    def name(self) -> Text:
        return "action_who_is_talking"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        info = file.getById(fromData["id"])
        
        print("Me llaman")
        return [SlotSet("who_is_chatting", info["first_name"]), SlotSet("was_called", True)]

class CheckAvailability(Action):
    def name(self) -> Text:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        meet_hour = next(tracker.get_latest_entity_values("meet_hour"))
        agenda = prolog.consultAgenda(time.getDay(), meet_hour)
        if agenda:
            message = "No puedo, estoy " + str(agenda[0]["Actividad"])
        else:
            message = "Buenisimo, nos vemos a las " + str(meet_hour)
        dispatcher.utter_message(text = message)
        return []



class AnswerSomeone(Action):
    def name(self) -> Text:
        return "action_answer_someone"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        is_chatting = tracker.get_slot("who_is_chatting")
        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        info = file.getById(fromData["id"])

        if is_chatting != info["first_name"]:
            return []

        intentExtracted = tracker.get_intent_of_latest_message()
        all_utters = domain["responses"].get(f"utter_{intentExtracted}", None)
        actions = domain["actions"]
        action = f"action_{intentExtracted}"
        SlotSet("was_called", False)
        if all_utters:
            utter = random.choice(all_utters)
            print(utter)
            print(metadata["message_id"])
            dispatcher.utter_message(text = utter["text"], answer_message=metadata["message_id"])
        elif action in actions:
            action = domain["actions"]
            index = (action.index(f"action_{intentExtracted}"))
            return[FollowupAction(actions[index]), SlotSet("was_called", False)]
        else:
            dispatcher.utter_message(text = "No te entendi", answer_message=metadata["message_id"])
        return [SlotSet("was_called", False)]



        

        
