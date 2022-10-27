from __future__ import annotations
import logging

from typing import Optional, Any, Dict, List, Text

from rasa.shared.core.domain import Domain
from rasa.core.policies.policy import Policy, PolicyPrediction, confidence_scores_for

from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

from rasa.core.featurizers.tracker_featurizers import (
    TrackerFeaturizer,
)

from rasa.core.constants import (
    POLICY_MAX_HISTORY,
)

import importlib.util
spec = importlib.util.spec_from_file_location("utils", "actions/utils.py")
foo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(foo)


logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.POLICY_WITHOUT_END_TO_END_SUPPORT, is_trainable=False
)
class Repeated(Policy):
	def __init__(
			self,
        	config: Dict[Text, Any],
        	model_storage: ModelStorage,
        	resource: Resource,
        	execution_context: ExecutionContext,
        	featurizer: Optional[TrackerFeaturizer] = None,
        	lookup: Optional[Dict] = None,
		) -> None:

		config[POLICY_MAX_HISTORY] = None
		super().__init__(config, model_storage, resource, execution_context, featurizer)
		self.answered = False
		self.priority = 5
		self.messages = []
	def train(
			self,
			training_trackers: List[TrackerWithCachedStates],
			domain: Domain,
			**kwargs: Any,
	) -> Resource:
		"""Trains the policy on given training trackers.
        Args:
            training_trackers:
                the list of the :class:`rasa.core.trackers.DialogueStateTracker`
            domain: the :class:`rasa.shared.core.domain.Domain`
            interpreter: Interpreter which can be used by the polices for featurization.
        """
		pass

	def get_default_config() -> Dict[Text, Any]:
		return {
			"priority": 5,
		}

	def predict_action_probabilities(
			self,
			tracker: DialogueStateTracker,
			domain: Domain,
			rule_only_data: Optional[Dict[Text, Any]] = None,
			**kwargs: Any,
	) -> PolicyPrediction:
		json = foo.JsonManager()
		result = self._default_predictions(domain)
		intent = str(tracker.latest_message.intent["name"])
		last_action = tracker.latest_action_name
		
		if last_action == "action_listen":
			metadata = tracker.latest_message.metadata
			from_id = metadata["message"]["from"]["id"]
			chat_type = metadata["message"]["chat"]["type"]
			chat_id = str(metadata["message"]["chat"]["id"])
			last_intent = json.getDataByKey(from_id, "last_intent")
			last_chat = json.getDataByKey(from_id, "last_chat")
			if last_intent == intent and last_chat == chat_id:
				tracker.clear_followup_action()
				if chat_type == "private":
					result = confidence_scores_for(str("utter_repeated"), 1.0, domain)
				else:
					result = confidence_scores_for(str("action_listen"), 1.0, domain)
			else:
				json.saveDataByKey(from_id, "last_intent", intent)
				json.saveDataByKey(from_id, "last_chat", chat_id)

		return self._prediction(result)

	def _metadata(self) -> Dict[Text, Any]:
		return {
			"priority": self.priority,
		}


	@classmethod
	def _metadata_filename(cls) -> Text:
		return "repeated_policy.json"