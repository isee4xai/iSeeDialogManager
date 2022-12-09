import business.bt.nodes.node as node
from business.bt.nodes.type import State
import business.coordinator as c
import datetime
import json
import business.storage as s
import business.bt.nodes.html_format as html

class ActionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("ACTION "+str(self.status) + " " + str(self.id))

    async def tick(self):

        # do_action(self.action)
        # if(self.status == State.RUNNING):
        # 	if(not self.thread.is_alive()):
        # 		self.status = State.SUCCESS
        # else:
        # 	self.status = State.RUNNING
        # 	self.thread = threading.Thread(target=do_action, args=(self.action,))
        # 	self.thread.start()
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

        await self.co.send_and_receive(self.message)
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

        await self.co.send_and_receive(self.message)
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        self.status = State.FAIL


class QuestionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.question = None
        self.variable = None

    def toString(self):
        return ("QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):

        await self.co.send_and_receive(self.question, self.variable)
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
        q = s.Question(self.id, self.question, s.ResponseType.OPEN.value, True)
        q.responseOptions = None
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        await self.co.send_and_receive(_question, self.variable)
        confirm_response = json.loads(self.co.check_world(self.variable))

        #if self.sentiment.is_positive(evaluate_response.lower()):
        if confirm_response[0]["content"].lower() == "yes":
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
        # self.sentiment = SentimentAnalyser()

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

            q = s.Question(self.id, _question, s.ResponseType.OPEN.value, True)
            q.responseOptions = None
            # print(q.responseType)
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send_and_receive(_question, self.variable)

            proceed_response = json.loads(self.co.check_world(self.variable))
            # print(proceed_response)

            # while not self.sentiment.is_positive(proceed_response.lower()):
            while not proceed_response[0]["content"].lower() == "yes":
                _question = "Would you like to proceed?"
                q = s.Question(self.id, _question, s.ResponseType.OPEN.value, True)
                q.responseOptions = None
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
        # get end user name and use case they are attached to from login
        self.co.modify_world("end_user_name", "Major Lee Adama")
        self.co.modify_world("use_case_id", "63231e9432f3b8255c1b0346")

        # TODO use GET /usecases/:id
        # with open("data/63231e9432f3b8255c1b0346.json", 'r') as usecase_file:
        #     self.use_case = json.load(usecase_file)
        #     self.co.createUsecase(self.use_case)

        # TODO API call
        # self.co.createOntology()

        # init ML stuff - commented
        # SentimentAnalyser.get()

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

        # # TODO extracted knowledge level should go to use case storage, not user utterance
        # response = self.co.check_world(self.variable)
        # if response.lower() in data:
        #     self.co.modify_usecase(self.variable, response.lower())

        # TODO ask till appropriate user response
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
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        questions = self.co.get_questions()
        q.responseOptions = [s.Response(k, q) for k, q in questions.items()]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)
        # user response
        # TODO get question from user response
        _selected_question = json.loads(self.co.check_world(self.variable))
        # print(_selected_question)
        self.co.modify_usecase(self.variable, _selected_question["id"])
        self.co.modify_intent()
        self.co.modify_evaluation()
        self.status = State.SUCCESS
        return self.status

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
        # user response
        # TODO get persona from user response
        _selected_persona = json.loads(self.co.check_world(self.variable))
        # print(_selected_persona)
        self.co.modify_usecase(self.variable, _selected_persona["id"])
        self.co.modify_strategy()
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
        return ("SINGLE SELECT MULTIPLE CHOICE QUESTION "+str(self.status) + " " + str(self.id) + " " 
                + str(self.question) + " " + str(self.variable))

    async def tick(self):
        # print(self.options)
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
        return ("EXPLAINER "+str(self.status) + " " + str(self.id))

    async def tick(self):

        random_instance = self.co.get_secure_api("/sampleDataInstance", {})

        # TODO: Update LIME to be taken from the AI Meta
        explainer_query = {
            "instance":random_instance ,
            "method": "/Tabular/LIME",
            # "params": self.params -> TODO: Needs Validation
        }

        # make the call to LIME explainer
        explainer_result = self.co.get_secure_api_post("/explainerResponse", explainer_query)

        # print(explainer_result)
        output_description = ""

        for o in explainer_result["meta"]["output_description"]:
            output_description += "<strong>"+o+": </strong><br>"+explainer_result["meta"]["output_description"][o]

        build_response = '<p>Here is a sample explanation: <br> <a href="'+explainer_result["plot_png"]+'" target="_blank"><img src="'+explainer_result["plot_png"]+\
                         '" style=" width: 600px; "></a> </p>'+\
                         '<p>Output Description: <br> '+output_description+'</p>'

        q = s.Question(self.id,build_response , s.ResponseType.OPEN.value, True)
        q.responseOptions = None
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class EvaluationQuestionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.message = None

    def toString(self):
        return ("EVALUATION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        q = s.Question(self.id, self.question, s.ResponseType.OPEN.value, True)
        q.responseOptions = None
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        await self.co.send_and_receive(_question, self.variable)
        # evaluate_response = json.loads(self.co.check_world(self.variable))

        #if self.sentiment.is_positive(evaluate_response.lower()):
        # if evaluate_response[0]["content"].lower() == "yes":
        self.status = State.SUCCESS
        # else:
        #     self.status = State.FAILURE
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE