import business.bt.tree_util as tg
import business.bt.nodes.factory as node_factory
import business.bt.bt as bt
from typing import List
from enum import IntEnum
import json


class ResponseType(IntEnum):
    RADIO = 0
    CHECK = 1
    LIKERT = 2
    NUMBER = 3
    INFO = 4
    OPEN = 5


class Response:
    def __init__(self, id, content) -> None:
        self.id = id
        self.content = content


class Question:
    def __init__(self, id, content, rtype, required) -> None:
        self.id = id
        self.content = content
        self.responseType: ResponseType = rtype
        self.responseOptions: List[Response] = []
        self.completed = ""
        self.dimension = ""
        self.intent = ""
        self.validators = None
        self.answer: List[Response] = []
        self.required = required


class World:
    def __init__(self) -> None:
        self.last_user_answer = None
        self.user_intent = ''
        self.survey_is_completed = False
        self.user_greeted = False
        self.user_satisfied = False
        #self.save = JSONS
        self.storage = dict()

    # put or update a value in the storage dictionnary
    def store(self, answer_key, value):
        # this function will need to change when introducing dialog logs
        self.storage[answer_key] = value
        #print("		" + str(answer_key) + " = " + str(value))

    # returns the value of a given key (and create a new entry when doesn't exist)
    def get(self, data_key):
        res = self.storage.get(data_key, None)

        # If the variable doesn't exist in the storage, it is created and set as False
        if (res == None):
            self.storage[data_key] = False
            res = False

        return res


class Ontology:
    def __init__(self) -> None:
        self.storage = dict()
        self.init()

    # TODO load from API in get
    def init(self):
        self.storage["KnowledgeLevel"] = ["no knowledge", "novice",
                                          "advanced beginner", "competent", "proficient", "expert"]

    # put or update a value in the storage dictionnary
    def store(self, _key, _value):
        self.storage[_key] = _value

    # returns the value of a given key (and create a new entry when doesn't exist)
    def get(self, _key):
        res = self.storage.get(_key, None)

        # If the variable doesn't exist in the storage, and valid, it is created
        if not res:
            self.storage[_key] = False
            res = False

        return res


class Usecase:
    def __init__(self, usecase_id, co) -> None:
        self.storage = {}
        self.co = co
        # TODO get usecase by id
        # self.json = self.co.call_api("", usecase_id)
        with open("data/63231e9432f3b8255c1b0346.json", 'r') as usecase_file:
            self.json = json.load(usecase_file)
        # {persona_id: properties{}}
        self.personas = {}
        # {persona_id: intents[]}
        self.persona_intents = {}
        # {persona_id: questions{}}
        self.persona_questions = {}
        # {persona_id: composite explanation strategy}
        self.persona_expstrategy = {}
        # {intent_id: questions[]}
        self.question_intent = {}
        # {persona_id: composite evaluation strategy}
        self.persona_evalstrategy = {}

        self.set_personas()

    def set_personas(self):
        for case in self.json:
            self.store("usecase_name", case["comment"])
            self.store(
                "ai_model_id", case["hasDescription"]["hasAIModel"]["hasModelId"]["value"])
            self.store(
                "ai_model_url", case["hasDescription"]["hasAIModel"]["hasModelURL"]["value"])

            persona_id = case["hasDescription"]["hasUserGroup"]["instance"]
            ai_knowledge = [item["levelOfKnowledge"]["instance"] for item in case["hasDescription"]
                            ["hasUserGroup"]["possess"] if item["classes"][0] == "AI Method Knowledge"][0]
            domain_knowledge = [item["levelOfKnowledge"]["instance"] for item in case["hasDescription"]
                                ["hasUserGroup"]["possess"] if item["classes"][0] == "Domain Knowledge"][0]
            self.personas[persona_id] = {"Name": case["hasDescription"]["hasUserGroup"]["comment"],
                                         "AI Knowledge Level": ai_knowledge,
                                         "Domain Knowledge Level": domain_knowledge}
            intent_id = case["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"]
            if persona_id in self.persona_intents:
                self.persona_intents[persona_id].append(
                    case["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"])
            else:
                self.persona_intents[persona_id] = [
                    case["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"]]
            if persona_id in self.persona_questions:
                self.persona_questions[persona_id].update(
                    {_q["instance"]: _q["comment"] for _q in case["hasDescription"]["hasUserGroup"]["asks"]})
            else:
                self.persona_questions[persona_id] = {
                    _q["instance"]: _q["comment"] for _q in case["hasDescription"]["hasUserGroup"]["asks"]}

            for q in case["hasDescription"]["hasUserGroup"]["asks"]:
                self.question_intent[q["instance"]] = intent_id

            if persona_id in self.persona_expstrategy:
                temp = [t for t in case["hasSolution"]["trees"]
                        if t["id"] == case["hasSolution"]['selectedTree']][0]
                intent_strategy_tree = tg.generate_tree_from_obj(temp, self.co)
                intent = case["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"]

                condition_node = node_factory.makeNode("Equal", intent, intent)
                condition_node.variables = {intent: True}
                condition_node.co = self.co

                sequence_node = node_factory.makeNode(
                    "Sequence", "Sequence_"+intent, "Sequence_"+intent)
                sequence_node.children.append(condition_node)
                sequence_node.children.append(
                    intent_strategy_tree.currentNode.children[0])
                sequence_node.co = self.co

                current_subtree = self.persona_expstrategy[persona_id]
                exstrgy_node = current_subtree.nodes["ExplanationStrategy"]
                exstrgy_node.children.append(sequence_node)

                _nodes = {**current_subtree.nodes, **intent_strategy_tree.nodes, sequence_node.id: sequence_node,
                          condition_node.id: condition_node}
                self.persona_expstrategy[persona_id] = bt.Tree(
                    exstrgy_node, _nodes)

            else:
                temp = [t for t in case["hasSolution"]["trees"]
                        if t["id"] == case["hasSolution"]['selectedTree']][0]
                intent_strategy_tree = tg.generate_tree_from_obj(temp, None)
                intent = case["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"]

                condition_node = node_factory.makeNode("Equal", intent, intent)
                condition_node.variables = {intent: True}
                condition_node.co = self.co

                sequence_node = node_factory.makeNode(
                    "Sequence", "Sequence_"+intent, "Sequence_"+intent)
                sequence_node.children.append(condition_node)
                sequence_node.children.append(
                    intent_strategy_tree.currentNode.children[0])
                sequence_node.co = self.co

                exstrgy_node = node_factory.makeNode(
                    "Sequence", "ExplanationStrategy", "ExplanationStrategy")
                exstrgy_node.children.append(sequence_node)
                exstrgy_node.co = self.co

                _nodes = {**intent_strategy_tree.nodes, exstrgy_node.id: exstrgy_node, sequence_node.id: sequence_node,
                          condition_node.id: condition_node}
                self.persona_expstrategy[persona_id] = bt.Tree(
                    exstrgy_node, _nodes)

    # store data from the use case
    def store(self, _key, _value):
        self.storage[_key] = _value

    # returns the values stored for a given key (and create a new entry when doesn't exist)
    def get(self, _key):
        res = self.storage.get(_key, None)

        # If the variable doesn't exist in the storage, it is created and set as False
        if (res == None):
            self.storage[_key] = False
            res = False

        return res

    def flatten_json(self, _json):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '.')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '.')
                    i += 1
            else:
                out[name[:-1]] = x
        flatten(_json)
        return out

    def get_personas(self):
        return self.personas

    def get_questions(self):
        _qs = {}
        if self.get("selected_persona") and self.persona_questions:
            p_id = self.get("selected_persona")
            _qs = self.persona_questions[p_id]
        return _qs

    def init_persona_strategy(self):
        None

    def modify_evaluation_strategy(self, _intent):
        if self.get("selected_persona") not in self.persona_evalstrategy:
            eval_strategy_node = node_factory.makeNode(
                "Sequence", "Sequence_evaluate", "Sequence_evaluate")
            eval_strategy_node.co = self.co

        else:
            eval_strategy_node = self.persona_evalstrategy[self.get("selected_persona")].root

        intent_case = [c for c in self.json if c["hasDescription"]["hasUserGroup"]["instance"] == self.get("selected_persona")
                           and c["hasDescription"]["hasUserGroup"]["hasIntent"]["instance"] == _intent]
        if len(intent_case) > 0:
            for q in intent_case[0]["hasOutcome"]["basedOn"]["questions"]:
                q_id = q["instance"]
                q_node = node_factory.makeNode("Multiple Choice Question", q_id, q_id)
                q_node.question = q["comment"]
                q_node.type = q["classes"][0]
                q_node.variable = q_id
                q_node.co = self.co
                # TODO get it from JSON
                q_node.options = {1: "I strongly disagree", 2: "I disagree",
                                    3: "I'm neutral", 4: "I agree", 5: "I strongly agree"}
                eval_strategy_node.children.append(q_node)

        self.persona_evalstrategy[self.get("selected_persona")] = bt.Tree(eval_strategy_node, None)            

    def get_persona_explanation_strategy(self):
        if self.get("selected_persona") and self.get("selected_persona") in self.persona_expstrategy:
            return self.persona_expstrategy[self.get("selected_persona")]
        return None

    def get_persona_evaluation_strategy(self):
        if self.get("selected_persona") and self.get("selected_persona") in self.persona_evalstrategy:
            return self.persona_evalstrategy[self.get("selected_persona")]
        return None

    def modify_intent(self):
        if self.get("selected_need"):
            q_id = self.get("selected_need")
            selected_intent = self.question_intent[q_id]
            current_intents = None
            if not self.get("selected_intents"):
                current_intents = set()
            else:
                current_intents = self.get("selected_intents")

            if selected_intent not in current_intents:
                current_intents.add(selected_intent)
                self.modify_evaluation_strategy(selected_intent)

            self.store("selected_intents", current_intents)

            # because explanation strategy navigate on intents, update world
            other_intents = filter(
                lambda i: i != selected_intent, self.persona_intents[self.get("selected_persona")])
            for o in other_intents:
                self.co.modify_world(o, False)
            self.co.modify_world(selected_intent, True)
