# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"


import json
import random
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction


from .utils import JsonManager, TimeManager
from .prolog_consults import PrologConsult
from .GoogleApi import Calendar
from .TelegramApi import TelegramAPI

import wikipedia


file = JsonManager()
time = TimeManager()
calendar = Calendar()
telegram = TelegramAPI()

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
            return [SlotSet("surname_check", False)]

        info["last_name"] = surname

        file.saveById(fromData["id"], info)
        dispatcher.utter_message(text = "Buenisimo " + info["first_name"])
        return [SlotSet("surname_check", False)]



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
            mensaje = 'Estoy libre, asi que ando viendo que puedo hacer'
        dispatcher.utter_message(text = mensaje)
        return[]


class ResponseMood(Action):
    def name(self) -> Text:
        return "action_mood"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mood = tracker.get_slot("mood")
        message = ''
        if mood == 'good':
            message = random.choice(["Me alegro!", "Que bueno!", "Buenisimo"])
        if mood == 'bad':
            message = random.choice(["Uy, sea lo que sea, espero que mejore", "Que mal, espero que se solucione pronto", "Que pena, espero que se solucione pronto"])
        if mood == 'neutral':
            message = random.choice(["Espero no pase nada malo", "Espero que no sea nada grave", "Espero que no sea nada malo"])
        
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
            nick = info.get("nick", fromData["first_name"])
            return [SlotSet("who_is_chatting", nick)]

        newData = {}
        newData["first_name"] = fromData["first_name"]
        lastname = fromData.get("last_name")

        if not lastname:
            return [SlotSet("surname_check", True)]

        newData["last_name"] = lastname
        file.saveById(fromData["id"], newData)
        return []

class WhoIsTalking(Action):
    def name(self) -> Text:
        return "action_who_is_talking"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        input_data=tracker.latest_message
        metadata = input_data["metadata"]["message"]
        fromData = metadata["from"]
        info = file.getById(fromData["id"])
        
        return [SlotSet("who_is_chatting", info["first_name"]), SlotSet("was_called", True)]

class CheckAvailability(Action):
    def name(self) -> Text:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("check_availabilty")
        meet_hour = int(tracker.get_slot("meet_hour"))
        meet_day = tracker.get_slot("meet_day")

        if not meet_day:
            dispatcher.utter_message(text = "No me dijiste el dia")
            return []

        agenda = prolog.consultAgenda(time.getDay(), meet_hour)
        calendarAgenda = calendar.available(int(time.getDayByName(meet_day)), meet_hour)
        if agenda:
            message = "No puedo, a esa hora estoy " + str(agenda[0]["Actividad"])
        elif calendarAgenda:
            message = "No puedo, tengo una reunion a esa hora"
        else:
            return[FollowupAction("action_make_meeting")]
        dispatcher.utter_message(text = message)
        return []

class MakeMeeting(Action):
    def name(self) -> Text:
        return "action_make_meeting"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        chat_info = tracker.latest_message["metadata"]["message"]["chat"]
        chat_id = chat_info["id"]
        name = tracker.latest_message["metadata"]["message"]["from"]["first_name"]
        meet_hour = int(tracker.get_slot("meet_hour"))
        meet_day = tracker.get_slot("meet_day")
        chat_type = chat_info["type"]

        if chat_type == "group" or chat_type == "supergroup":
            summary = "Reunion de " + chat_info["title"]
        else:
            summary = "Reunion con " + name

        event = {
            'summary': summary,
            'description': 'Reunion con ' + name,
            'day': int(time.getDayByName(meet_day)),
            'hour': meet_hour,
        }
        event = calendar.saveMeet(event)
        event_id = event["id"]
        event_link = event["htmlLink"]
        telegram.sendMessage(chat_id, f"Buenisimo, nos vemos a las {str(meet_hour)}  el {str(meet_day)}")
        
        if chat_type == "group" or chat_type == "supergroup":
            telegram.sendMessage(chat_id, f"Anote la reunion en un calendar asi no la perdemos, les dejo el link: {event_link}")
            message = telegram.sendMessage(chat_id, "Si alguno mas va a unirse a al reunion respondame este mensaje porfa")
            message_id = str(message["result"]["message_id"])
            return [SlotSet("message_id", message_id), SlotSet("event_id", event_id)]
        return [SlotSet("event_id", event_id), FollowupAction("action_listen")]

class AddToMeet(Action):
    def name(self) -> Text:
        return "action_add_to_meet"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        reply_info = tracker.latest_message["metadata"]["message"].get("reply_to_message")
        message_info = tracker.latest_message["metadata"]["message"]
        sender = message_info["from"].get("username")
        chat_info = tracker.latest_message["metadata"]["message"]["chat"]
        message_id = int(tracker.get_slot("message_id"))

        event_id = tracker.get_slot("event_id")
        if reply_info:
            replied_to = int(reply_info["message_id"])
            if message_id == replied_to:
                chat_id = chat_info["id"]
                if not sender:
                    sender = message_info["from"]["first_name"]
                telegram.sendMessage(chat_id, f"Dale @{sender}, te agrego a la reunion")
                calendar.addParticipant(event_id, message_info["from"]["first_name"])
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

        if all_utters:
            utter = random.choice(all_utters)


            dispatcher.utter_message(text = utter["text"], answer_message=metadata["message_id"])
        elif action in actions:
            action = domain["actions"]
            index = (action.index(f"action_{intentExtracted}"))
            return[FollowupAction(actions[index]), SlotSet("was_called", False)]
        else:
            dispatcher.utter_message(text = "No te entendi", answer_message=metadata["message_id"])
        return [SlotSet("was_called", False)]

class GetInfo(Action):
    def name(self) -> Text:
        return "action_get_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        metadata = tracker.latest_message["metadata"]["message"]
        wikipedia.set_lang("es")
        topic = str(tracker.get_slot("actual_topic")).replace(" ", "_")
        info = wikipedia.page(topic)
        dispatcher.utter_message(text = f"No se mucho del tema... pero dejame investigo y paso algo de info", answer_message=metadata["message_id"])
        dispatcher.utter_message(text = info.summary, answer_message=metadata["message_id"])
        dispatcher.utter_message(text = f"Dejo mas info para el lector interesado {info.url}")
        return []



        

        
