import business.bt.nodes.node as node
from business.bt.nodes.type import State
import business.coordinator as c
import datetime
import json
import business.storage as s
import business.bt.nodes.html_format as html
import pandas as pd

class ActionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("ACTION "+str(self.status) + " " + str(self.id))

    async def tick(self):

        # do_action()

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class Failer(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.message = None

    def toString(self):
        return ("FAILER "+str(self.status) + " " + str(self.id) + " " + str(self.message))

    async def tick(self):

        # do something
        self.status = State.FAILURE
        return self.status

    def reset(self):
        self.status = State.FAILURE


class Succeder(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.message = None

    def toString(self):
        return ("SUCCEDER "+str(self.status) + " " + str(self.id) + " " + str(self.message))

    async def tick(self):

        # do something
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        self.status = State.FAILURE


class QuestionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.question = None
        self.variable = None

    def toString(self):
        return ("QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        # ask question
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class ConfirmNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("CONFIRM "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        await self.co.send_and_receive(_question, self.variable)
        confirm_response = json.loads(self.co.check_world(self.variable))

        if self.co.is_positive(confirm_response["content"].lower()):
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class GreeterNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.greet_text = {0: "Good Morning ☀️",
                           1: "Good Afternoon",
                           2: "Good Evening"}

    def toString(self):
        return "GREETER " + str(self.status) + " " + str(self.id) + " " + str(self.variable)

    async def tick(self):
        currentTime = datetime.datetime.now()
        time_of_day = 0 if currentTime.hour < 12 else 1 if 12 <= currentTime.hour < 18 else 2

        end_user_name = self.co.check_world("user_name")
        usecase_name = self.co.check_usecase("usecase_name")

        
        if self.co.check_world("initialise") and not self.co.check_world("proceed"):
            _question = self.greet_text[time_of_day] + " " + end_user_name + "!<br>"
            _question = _question + "I am the iSee Chatbot for the " + usecase_name + ", "
            _question = _question + "Would you like to proceed?"

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send_and_receive(_question, self.variable)

            proceed_response = json.loads(self.co.check_world(self.variable))

            while not self.co.is_positive(proceed_response["content"].lower()):
                _question = "Would you like to proceed?"
                q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
                q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
                _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
                await self.co.send_and_receive(_question, self.variable)
                proceed_response = json.loads(self.co.check_world(self.variable))
        else:
            _question = "Thank you for using iSee!" +"\n"
            _question = _question + "See you again soon!"

            q = s.Question(self.id, _question, s.ResponseType.INFO.value, False)
            q.responseOptions = None
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send(_question)

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class InitialiserNode(ActionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.use_case = None

    def toString(self):
        return ("INITIALISER "+str(self.status) + " " + str(self.id))

    async def tick(self):

        # not used 
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class KnowledgeQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("KNOWLEDGE QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " "
                + str(self.variable))

    async def tick(self):
        # data = self.co.check_ontology(self.question_data)
        # if data:
        #     _question = self.question + "\n" + \
        #         "Please select from "+", ".join(data)+"."
        #     await self.co.send_and_receive(_question, self.variable)
        # else:
        #     await self.co.send_and_receive(self.question, self.variable)

        # response = self.co.check_world(self.variable)
        # if response.lower() in data:
        #     self.co.modify_usecase(self.variable, response.lower())

        self.status = State.SUCCESS

        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class NeedQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.question_data = []

    def toString(self):
        return ("NEED QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " "
                + str(self.variable) + " " + str(self.question_data))

    async def tick(self):
        questions = self.co.get_questions()
        if questions:
            q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response(k, q) for k, q in questions.items()]

            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)

            _selected_question = json.loads(self.co.check_world(self.variable))
        
            self.co.modify_usecase(self.variable, _selected_question["id"])
            self.co.modify_intent()
            self.co.modify_strategy()
            self.co.modify_evaluation()
            self.status = State.SUCCESS
            return self.status
        # allow free-text questions?
        # else:
        #     q = s.Question(self.id, self.question, s.ResponseType.OPEN.value, True)
        #     q.responseOptions = None

        #     _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        #     await self.co.send_and_receive(_question, self.variable)

        #     _selected_question = json.loads(self.co.check_world(self.variable))

        #     predict intent based on the free-text question and do modifications


    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class PersonaQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "PERSONA " + str(self.status) + " " + str(self.id) + " " + str(self.question)

    async def tick(self):
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        personas = self.co.get_personas()
        q.responseOptions = [s.Response(p, html.persona(personas[p])) for p in personas]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        _selected_persona = json.loads(self.co.check_world(self.variable))

        self.co.modify_usecase(self.variable, _selected_persona["id"])
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class MultipleChoiceQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.options = {}
        self.type = None

    def toString(self):
        return ("MULTIPLE CHOICE QUESTION "+str(self.status) + " " + str(self.id) + " " 
                + str(self.question) + " " + str(self.variable))

    async def tick(self):
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response(k,v) for k,v in self.options.items()]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class ExplainerNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.params = None
        self.endpoint = None
        self.variable = None

    def toString(self):
        return ("EXPLAINER "+ str(self.status) + " " + str(self.id) + " " + str(self.endpoint) + " " + str(self.co))

    async def tick(self):

        random_instance = self.co.check_world("selected_target")
        explainer_query = {
            "instance":random_instance['instance'],
            "type":random_instance['type'],
            "method": self.endpoint,
            # "params": self.params TODO
        }
        explainer_result = self.co.get_secure_api_post("/model/explain", explainer_query)
        
        for o in explainer_result["meta"]["output_description"]:
            output_description = explainer_result["meta"]["output_description"][o]
        if explainer_result["type"] == 'image':
            explanation_base64 = explainer_result["explanation"]
            explanation = '<img width="700" src="data:image/png;base64,'+explanation_base64+'"/>'
        if explainer_result["type"] == 'html':
            explanation_html = explainer_result["explanation"]
            explanation = explanation_html

        try:
            technique = ''.join(map(lambda x: x if x.islower() else " "+x, self.endpoint.split("/")[-1]))
        except:
            technique = self.endpoint.split("/")[-1]

        _question = '<p>Here is an explanation from '+technique+' Technique</p>'
        _question += explanation
        _question += '<br><p><strong>Explanation Description:</strong> <br>'+output_description+'</p>'

        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("okay", "Okay")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class TargetQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("TARGET "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        random_instance = self.co.get_secure_api("/dataset/randomInstance", {})

        ai_model_query = {
            "instance":random_instance['instance'],
            "top_classes": '1',
            "type":random_instance['type']
        }

        instance_base64 = random_instance['instance'] 
        instance = '<img width="200" src="data:image/png;base64,'+instance_base64+'"/>'
        ai_model_result = self.co.get_secure_api_post("/model/predict", ai_model_query)

        _question = '<p>Here is your test instance:</p>'
        _question += instance
        _question += '<br><p>And here is the outcome from the AI system:</p>'
        _question += '<p>Probability of fracture is '+str(round(float(ai_model_result[list(ai_model_result.keys())[0]])*100, 2))+'%.</p>'

        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("okay", "Okay")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        # set selected target
        self.co.modify_world(self.variable, random_instance)
        
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class CompleteNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("COMPLETE "+str(self.status) + " " + str(self.id))

    async def tick(self):

        self.co.save_conversation()
        
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        self.status = State.FAILURE   