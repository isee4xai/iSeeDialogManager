import business.bt.nodes.node as node
from business.bt.nodes.type import State,TargetType
import business.coordinator as c
from datetime import datetime
import json
import business.storage as s
import business.bt.nodes.html_format as html
import pandas as pd
import asyncio
class ActionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("ACTION "+str(self.status) + " " + str(self.id))

    async def tick(self):
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
        self.start = datetime.now()
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        await self.co.send_and_receive(_question, self.variable)
        confirm_response = json.loads(self.co.check_world(self.variable))

        if self.co.is_positive(confirm_response["content"].lower()):
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
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
        self.start = datetime.now()
        currentTime = datetime.now()
        time_of_day = 0 if currentTime.hour < 12 else 1 if 12 <= currentTime.hour < 18 else 2

        usecase_name = self.co.check_usecase("usecase_name")
        end_user_name = self.co.check_world("user_name")

        if self.co.check_world("initialise") and not self.co.check_world("proceed"):
            _question = self.greet_text[time_of_day] + " " + end_user_name + "!<br>"
            _question += "<p>I am the iSee Chatbot for the " + usecase_name + "</p>"
            _question += "<p>Before we begin, here are a few helpful reminders:</p>"
            _question += "<p>The iSee chatbot is a tool to <strong>help understand Loan Approval AI system decisions as if you were a loan applicant</strong>, through Explainability Techniques.</p> <p>The iSee Chatbot will guide you through your loan application, the AI decision, and provide explanations for your chosen questions. Towards the end, you will have the opportunity to answer a few questions and provide descriptive feedback. We refer to this interactive conversation as an <i>Explanation Experience.</i></p>"
            _question += "<p>Please remember to take your time reading and understanding the chatbot's messages. Each prompt influences the path of our conversation and impacts your overall experience. </p>"
            _question += "<p>This system is continuously being improved. Some responses may take a bit longer due to background algorithms running for explanations. If a response takes more than 60 seconds, please restart the conversation using the button in the top-right corner.</p>"
            _question += "<p>At the end of the conversation, you will be asked to provide feedback with a minimum of 100 words. Please ensure that your feedback is constructive in order to help improve this tool. We would like to hear detailed feedback about the features you found useful and suggestions for improvement. Your feedback will be manually reviewed by the researchers involved in the project.</p>"
            _question += "<p>Would you like to proceed?</p>"

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
            if usecase_name.lower() == 'loan approval system':
                _question += "Here is your Prolific Completion Code: C3IZV4R5." +"\n"
            _question += "See you again soon!"

            q = s.Question(self.id, _question, s.ResponseType.INFO.value, False)
            q.responseOptions = None
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send(_question)

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class InitialiserNode(ActionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variable = "prolific_id"

    def toString(self):
        return ("INITIALISER "+str(self.status) + " " + str(self.id))

    async def tick(self):
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
        self.start = datetime.now()
        questions = self.co.get_questions()
        if questions:
            no_more = [q for k, q in questions.items() if q=="I don't have any more questions"]
            if no_more:
                self.question = "<p>Would you like to ask another question you may have about the AI system's decision? Similar questions are grouped by colour for convenience. Once you have selected a question, we will use an explanation technique to provide you with insights. Please keep in mind that certain explanations may take around 20-30 seconds to complete.</p> <p>If you have any other questions that are not listed here, feel free to include it in your feedback for future improvements.</p>"
            else:
                self.question = "<p>Having reviewed both the loan application and the AI system's decision, we're eager to address any questions you may have about the AI system's decision. We have prepared a set of questions for you to choose from, designed to shed light on the decision-making process. Similar questions are grouped by colour for convenience. Once you have selected a question, we will use an explanation technique to provide you with insights. Please keep in mind that certain explanations may take around 20-30 seconds to complete.</p> <p>If you have any other questions that are not listed here, feel free to include it in your feedback for future improvements.</p>"
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
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
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
        self.start = datetime.now()
        self.question = "Let's set up your role for this conversation. In this session, you'll be taking on the persona of a loan applicant who isn't familiar with the loan approval process, artificial intelligence techniques, or explanations. This way, we can make sure our conversation is clear and easy to understand for you. Please choose and confirm this role to continue."
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        personas = self.co.get_personas()
        q.responseOptions = [s.Response(p, html.persona(personas[p])) for p in personas]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        _selected_persona = json.loads(self.co.check_world(self.variable))

        self.co.modify_usecase(self.variable, _selected_persona["id"])
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class EvaluationQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.options = {}
        self.type = None
        self.validators = dict()

    def toString(self):
        return ("EVALUATION QUESTION "+str(self.status) + " " + str(self.id) + " " 
                + str(self.question) + " " + str(self.type) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        responseType = None
        if self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Open_Question':
            responseType = s.ResponseType.OPEN.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Number_Question':
            responseType = s.ResponseType.NUMBER.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#MultipleChoiceNominalQuestion':
            responseType = s.ResponseType.CHECK.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Likert_Scale_Question':
            responseType = s.ResponseType.LIKERT.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#SingleChoiceNominalQuestion':
            responseType = s.ResponseType.RADIO.value            

        q = s.Question(self.id, self.question, responseType, True)
        if responseType == s.ResponseType.NUMBER.value:
            q.validators = self.validators
        elif responseType != s.ResponseType.OPEN.value: 
            q.responseOptions = [s.Response(k,v) for k,v in self.options.items()]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
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
        self.start = datetime.now()
        # random_instance = self.co.check_world("selected_target")
        # explainer_query = {
        #     "instance":random_instance['instance'],
        #     "type":random_instance['type'],
        #     "method": self.endpoint,
        #     # "params": self.params TODO
        # }
        random_instance = self.co.check_usecase("instance")['instance_json']
        explainer_query = {
            "instance":random_instance,
            "method": self.endpoint,
            "type":'dict'
        }
        # explainer_result = self.co.get_secure_api_usecase_post("/model/explain", explainer_query)
        if self.endpoint == '/Tabular/LIME':
            await asyncio.sleep(25)
            temp_ex = self.co.check_usecase("instance")['lime_ex']
            temp_desc = self.co.check_usecase("instance")['lime_desc']
            temp_type = 'image'
            temp_tech = "LIME Algorithm"
            temp_width = 1100
        elif self.endpoint == '/Tabular/KernelSHAPLocal':
            await asyncio.sleep(35)
            temp_ex = self.co.check_usecase("instance")['shap_ex']
            temp_desc = self.co.check_usecase("instance")['shap_desc']
            temp_type = 'image'
            temp_tech = "Kernel SHAP Algorithm"
            temp_width = 600
        elif self.endpoint == '/Misc/AIModelPerformance':
            await asyncio.sleep(5)
            temp_ex = self.co.check_usecase("instance")['perf_ex']
            temp_desc = self.co.check_usecase("instance")['perf_desc']
            temp_type = 'html'
            temp_tech = 'AI Model Performance'
        elif self.endpoint == '/Tabular/DisCERN':
            await asyncio.sleep(15)
            temp_ex = self.co.check_usecase("instance")['discern_ex']
            temp_desc = self.co.check_usecase("instance")['discern_desc']
            temp_type = 'html'
            temp_tech = 'DisCERN Counterfactual Algorithm'

        # for o in explainer_result["meta"]["output_description"]:
        #     output_description = explainer_result["meta"]["output_description"][o]
        if temp_type == 'image':
            explanation_base64 = temp_ex
            explanation = '<img src="data:image/png;base64,'+explanation_base64+'" style=" width: '+str(temp_width)+'px; "/>'
        if temp_type == 'html':
            explanation_html = temp_ex
            explanation = explanation_html

        # try:
        #     technique = ''.join(map(lambda x: x if x.islower() else " "+x, self.endpoint.split("/")[-1]))
        # except:
        #     technique = self.endpoint.split("/")[-1]

        # _question = '<p> '+temp_tech+' </p>'
        _question = explanation
        _question += '<p>'+temp_desc+'</p>'
        _question += "Once you are ready, please confirm to proceed."

        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("okay", "Okay")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable), selected_target=self.co.check_world("selected_target"))
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
        self.start = datetime.now()
        # select from data upload; data enter; and sampling
        dataset_type_image = self.co.check_dataset_type()
        is_sampling_response = json.loads(self.co.check_world("selected_target_type"))
        # if sampling an image
        if is_sampling_response["id"] == TargetType.SAMPLE.value and dataset_type_image:
            random_instance = self.co.get_secure_api_usecase("/dataset/randomInstance", {})

            ai_model_query = {
                "instance":random_instance['instance'],
                "top_classes": '1',
                "type":random_instance['type']
            }

            instance_base64 = random_instance['instance'] 
            instance = '<img width="400" src="data:image/png;base64,'+instance_base64+'"/>'
            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)

            _question = '<p>Here is your test instance:</p>'
            _question += instance
            _question += '<br><p>And here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("sampling_image_question", _question)

            # set selected target
            self.co.modify_world(self.variable, random_instance)
        # if sampling and not image
        elif is_sampling_response["id"] == TargetType.SAMPLE.value and not dataset_type_image:
            # random_instance = self.co.get_secure_api_usecase("/dataset/randomInstance", {})
            # ai_model_query = {
            #     "instance":random_instance['instance'],
            #     "top_classes": '1',
            #     "type":random_instance['type']
            # }
            # instance_json = random_instance['instance'] 
            random_instance = self.co.check_usecase("instance")['instance_json']
            ai_model_query = {
                "instance":random_instance,
                "top_classes": '1',
                "type":'dict'
            }

            instance_json = self.co.check_usecase("instance")['instance_view']
            instance =  html.table(instance_json)
            # ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            ai_model_result = self.co.check_usecase("instance")['ai_model_result']

            _question = '<p>Here is the loan application you will be working with in this session.</p>'
            _question += '<p>'+instance+'</p>'
            _question += '<p>'+self.co.check_usecase("instance")['instance_desc']+'</p>'
            _question += '<p>And here is the decision from the Loan Approval AI system:</p>'
            _question += '<p>'+html.table(ai_model_result)+'</p>'
            _question += '<p>'+self.co.check_usecase("instance")['ai_model_result_desc']+'</p>'
            _question += '<p> Once you are ready, please confirm to proceed. </p>'


            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("sampling_csv_question", _question)

            # set selected target
            self.co.modify_world(self.variable, random_instance)
        # upload image
        elif dataset_type_image:
            _question = "Please upload your data instance."
            q = s.Question(self.id, _question, s.ResponseType.FILE_IMAGE.value, True)
            q.responseOptions = []
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, "upload_instance_image")

            upload_instance_image = json.loads(self.co.check_world("upload_instance_image"))
            selected_instance = {}
            selected_instance['instance'] = upload_instance_image["content"].split("base64")[1]
            selected_instance['type'] = 'image'

            ai_model_query = {
                "instance":selected_instance['instance'],
                "top_classes": '1',
                "type":selected_instance['type']
            }

            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            _question = '<p>Here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("upload_image_question", _question)

            self.co.modify_world(self.variable, selected_instance)
        # upload csv
        else:
            _question = "Please upload your data instance."
            q = s.Question(self.id, _question, s.ResponseType.FILE_CSV.value, True)
            q.responseOptions = []
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, "upload_instance_csv")

            upload_instance_open = json.loads(self.co.check_world("upload_instance_csv"))
            selected_instance = {}
            selected_instance['instance'] = upload_instance_open["content"]
            selected_instance['type'] = 'dict'

            ai_model_query = {
                "instance":selected_instance['instance'],
                "top_classes": '1',
                "type":selected_instance['type']
            }

            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            _question = '<br><p>Here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("upload_csv_question", _question)

            self.co.modify_world(self.variable, selected_instance)
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status            

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class TargetTypeQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("TARGET TYPE"+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        # select from data upload; data enter; and sampling
        dataset_type_image = self.co.check_dataset_type()
        if dataset_type_image:
            _question = '<p>Would you like to upload a data instance (.jpg, .png) or use inbuilt sampling method to select a data instance for testing?</p>'
        else:
            _question = '<p>Would you like to upload a data instance (.csv) or use inbuilt sampling method to select a data instance for testing?</p>'
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("UPLOAD", "I would like to upload"), s.Response("SAMPLE", "I will use sampling")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        # await self.co.send_and_receive(_question, self.variable)
        # for user study always sample
        self.co.modify_world(self.variable, json.dumps({"id": "SAMPLE", "content": "I will use sampling"}))

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
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
        self.start = datetime.now()
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE   

class UserQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.params = None

    def toString(self):
        return ("USER QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        selected_q_id = self.co.check_usecase("selected_need")
        selected_q = self.co.get_question_by_id(selected_q_id)
        questions = [self.params["Question"].lower()] if ";" not in self.params["Question"].lower() else [f.lower() for f in self.params["Question"].lower().split(";")]
        match = selected_q.strip().lower() in questions

        content = {
            "content": selected_q,
            "id": selected_q_id,
            "match": match
        }
        if match:
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self, variable=content)
        return self.status

    def reset(self):
        self.status = State.FAILURE   