import business.bt.tree_util as tg
import business.bt.nodes.factory as node_factory
import business.bt.bt as bt
from typing import List
from enum import Enum
import json


class ResponseType(Enum):
    RADIO = "Radio"
    CHECK = "Checkbox"
    LIKERT = "Likert"
    NUMBER = "Number"
    INFO = "Info"
    OPEN = "Free-Text"


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
    def __init__(self, co) -> None:
        self.storage = dict()
        self.co = co
        self.init()

    def init(self):
        temp = self.co.get_api("https://api-onto-dev.isee4xai.com/api/onto/cockpit/DialogFields", {});
        for key in temp:
            for item in temp[key]:
                self.store(item["key"], item["label"])

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
        self.json = self.co.get_secure_api("/casestructure", {})
        # {persona_id: properties{}}
        self.personas = {}
        # {persona_id: intents[]}
        self.persona_intents = {}
        # {persona_id: questions{}}
        self.persona_questions = {}
        # {persona_id: {intent_id, composite explanation strategy}}
        self.p_i_expstrategy = {}
        # {question_id: intent_id}
        self.question_intent = {}
        # {persona_id: composite evaluation strategy}
        self.persona_evalstrategy = {}

        self.set_personas()

    def set_personas(self):
        for case in self.json:
            self.store("usecase_name", " ".join(case["http://www.w3.org/2000/01/rdf-schema#comment"].split("_")))
            # self.store(
            #     "ai_model_id", case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasAIModel"]["hasModelId"]["value"])
           
            self.store(
                "ai_model_meta", case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasAIModel"]["http://www.w3id.org/iSeeOnto/aimodel#hasCaseStructureMetaData"]["value"])

            persona_id = case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["instance"]
            ai_knowledge = [item["http://www.w3id.org/iSeeOnto/user#levelOfKnowledge"]["instance"] for item in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]
                            ["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["https://purl.org/heals/eo#possess"] if item["classes"][0] == "http://www.w3id.org/iSeeOnto/user#AIMethodKnowledge"][0]
            domain_knowledge = [item["http://www.w3id.org/iSeeOnto/user#levelOfKnowledge"]["instance"] for item in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]
                            ["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["https://purl.org/heals/eo#possess"] if item["classes"][0] == "http://www.w3id.org/iSeeOnto/user#DomainKnowledge"][0]
            self.personas[persona_id] = {"Name": case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3.org/2000/01/rdf-schema#comment"],
                                         "AI Knowledge Level": self.co.check_ontology(ai_knowledge),
                                         "Domain Knowledge Level": self.co.check_ontology(domain_knowledge)}
            intent_id = case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3id.org/iSeeOnto/user#hasIntent"]["instance"]
            if persona_id in self.persona_intents:
                self.persona_intents[persona_id].append(
                    case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3id.org/iSeeOnto/user#hasIntent"]["instance"])
            else:
                self.persona_intents[persona_id] = [
                    case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3id.org/iSeeOnto/user#hasIntent"]["instance"]]
            if persona_id in self.persona_questions:
                self.persona_questions[persona_id].update(
                    {_q["instance"]: _q["http://semanticscience.org/resource/SIO_000300"] for _q in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["https://purl.org/heals/eo#asks"]})
            else:
                self.persona_questions[persona_id] = {
                    _q["instance"]: _q["http://semanticscience.org/resource/SIO_000300"] for _q in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["https://purl.org/heals/eo#asks"]}

            for q in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["https://purl.org/heals/eo#asks"]:
                self.question_intent[q["instance"]] = intent_id

            temp = [t for t in case["http://www.w3id.org/iSeeOnto/explanationexperience#hasSolution"]["trees"]
                    if t["id"] == case["http://www.w3id.org/iSeeOnto/explanationexperience#hasSolution"]['selectedTree']][0]
            # _intent_strategy_tree = tg.generate_tree_from_obj(temp, self.co)
            #TODO for testing composite strategies
            _intent_strategy_tree = tg.generate_tree_from_file('data/estrategy2.json', self.co)
            _intent = case["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3id.org/iSeeOnto/user#hasIntent"]["instance"]
            _tree = bt.Tree(_intent_strategy_tree.root.children[0], _intent_strategy_tree.nodes)       
            if persona_id in self.p_i_expstrategy:
                _i_strategy = self.p_i_expstrategy[persona_id]
            else:
                _i_strategy = {}
            _i_strategy[_intent] = _tree
            self.p_i_expstrategy[persona_id] = _i_strategy
                
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
            _qs_ = self.persona_questions[p_id]
            _is_ = self.get("selected_intents") 
            for _k, _v in _qs_.items():
                _i = self.question_intent[_k]
                if not _is_ or (_is_ and _i not in _is_):
                    _qs[_k] = _v
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

        intent_case = [c for c in self.json if c["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["instance"] == self.get("selected_persona")
                           and c["http://www.w3id.org/iSeeOnto/explanationexperience#hasDescription"]["http://www.w3id.org/iSeeOnto/explanationexperience#hasUserGroup"]["http://www.w3id.org/iSeeOnto/user#hasIntent"]["instance"] == _intent]
        if len(intent_case) > 0:
            for q in intent_case[0]["http://www.w3id.org/iSeeOnto/explanationexperience#hasOutcome"]["http://linkedu.eu/dedalo/explanationPattern.owl#isBasedOn"]:
                q_id = q["instance"]
                q_node = node_factory.makeNode("Multiple Choice Question", q_id, q_id)
                q_node.question = q["http://www.w3.org/2000/01/rdf-schema#comment"]
                q_node.type = q["classes"][0]
                q_node.variable = q_id
                q_node.co = self.co
                _options = q["http://www.w3id.org/iSeeOnto/userevaluation#hasResponseOptions"]["http://semanticscience.org/resource/SIO_000974"]
                # print(_options)
                q_node.options = {_o["https://www.w3id.org/iSeeOnto/BehaviourTree#pairKey"]:_o["https://www.w3id.org/iSeeOnto/BehaviourTree#pair_value_literal"] for _o in _options}
                eval_strategy_node.children.append(q_node)

        self.persona_evalstrategy[self.get("selected_persona")] = bt.Tree(eval_strategy_node, None)            

    def get_persona_intent_explanation_strategy(self):
        if self.get("selected_persona") and self.get("selected_persona") in self.p_i_expstrategy:
            _p_i_exs = self.p_i_expstrategy[self.get("selected_persona")]
            selected_intent = self.question_intent[self.get("selected_need")]
            if selected_intent and selected_intent in _p_i_exs:
                return _p_i_exs[selected_intent]
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
