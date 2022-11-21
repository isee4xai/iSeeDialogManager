from http import client
import business.storage as storage
import business.bt.bt as bt
import ui.logger as logger
import ui.interface as interface
import json
import business.api as api

class Coordinator:

    def __init__(self, client_id, usecase_id, socket) -> None:
        self.client_id = client_id
        self.usecase_id = usecase_id
        self.interface = interface.WebSocket(socket)
        self.world = storage.World()
        
        self.logger = logger.Logger()
        
        
        self.usecase = storage.Usecase(usecase_id, self)
        self.ontology = storage.Ontology()
        self.bt = bt.BehaviourTree(self)

    async def start(self):
        await self.bt.run()

    async def send(self, message):
        await self.interface.send(message)

    async def send_and_receive(self, message, answer_slot):
        answer = await self.interface.send_and_receive(message)
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
        # plug explanation strategy
        # new_exp_strategy = self.usecase.get_persona_explanation_strategy()
        # self.bt.plug_strategy(new_exp_strategy, "Explanation Strategy")
        None

    def modify_intent(self):
        self.usecase.modify_intent()

    def modify_evaluation(self):
        # populate evaluation strategy
        new_eval_strategy = self.usecase.get_persona_evaluation_strategy()
        self.bt.plug_strategy(new_eval_strategy, "Evaluation Strategy")

    def log(self, message):
        self.logger.log(message)

    def call_api(self, base_url, id, params):
        return api.request(base_url+"/"+id, params)

    def reset(self):
        self.world = storage.World()
        self.logger = logger.Logger()
        self.usecase = storage.Usecase(self.usecase_id, self)
        self.ontology = storage.Ontology()
        self.bt = bt.BehaviourTree(self)
