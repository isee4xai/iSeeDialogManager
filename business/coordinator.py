from http import client
import business.storage as storage
import business.bt.bt as bt
import ui.logger as logger
import ui.interface as interface
import json
import business.api as api

# API_BASE = "http://localhost:3000/api/"
API_BASE = "https://api-dev.isee4xai.com/api/"
class Coordinator:

    def __init__(self, client_id, socket) -> None:
        self.client_id = client_id
        self.history = []
        self.interface = interface.WebSocket(socket)
        self.world = storage.World()

        self.logger = logger.Logger()
        self.ontology = storage.Ontology(self)
        self.bt = bt.BehaviourTree(self)

    def init(self, j_data):
        self.world.store("user_token", j_data["user"]["token"])
        self.world.store("usecase_id", j_data["usecase_id"])
        self.world.store("user_name", j_data["user"]["name"])
        # self.user = storage.User(j_data["user"], self)
        self.usecase = storage.Usecase(j_data["usecase_id"], self)
        self.world

    async def start(self):
        await self.bt.run()

    async def send(self, message):
        await self.interface.send(message)

    async def send_and_receive(self, message, answer_slot):
        self.history.append(message)
        answer = await self.interface.send_and_receive(message)
        self.history.append(answer)
        self.world.store(answer_slot, answer)

    def modify_world(self, _variable, _value):
        self.world.store(_variable, _value)

    def check_world(self, _variable):
        return self.world.get(_variable)

    def modify_usecase(self, _variable, _value=None):
        self.usecase.store(_variable, _value)

    def check_usecase(self, _variable):
        return self.usecase.get(_variable)

    def check_ontology(self, _variable):
        return self.ontology.get(_variable)

    def get_personas(self):
        return self.usecase.get_personas()

    def get_questions(self):
        return self.usecase.get_questions()

    def modify_strategy(self):
        new_exp_strategy = self.usecase.get_persona_intent_explanation_strategy()
        self.bt.plug_strategy(new_exp_strategy, "Explanation Strategy")

    def modify_intent(self):
        self.usecase.modify_intent()

    def modify_evaluation(self):
        # populate evaluation strategy
        new_eval_strategy = self.usecase.get_persona_evaluation_strategy()
        self.bt.plug_strategy(new_eval_strategy, "Evaluation Strategy")

    def log(self, message):
        self.logger.log(message)

    def get_api(self, url, params):
        return api.request(url, params, {})

    def get_secure_api(self, path, params):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }

        url = API_BASE +"usecases/" + self.world.get("usecase_id") + path

        return api.request(url, params, headers)

    def get_secure_api_post(self, path, body):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }
        url = API_BASE +"usecases/" + self.world.get("usecase_id") + path
        return api.requestPOST(url, body, headers)

    def reset(self):
        self.history = []
        self.world = storage.World()
        self.logger = logger.Logger()
        self.ontology = storage.Ontology(self)
        self.bt = bt.BehaviourTree(self)

    def save_conversation(self):
        print(self.history)