import business.bt.nodes.node as node
from business.bt.nodes.type import State
from business.bt.nodes.action import QuestionNode
import business.storage as s
import json

class ReplacementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("REPLACEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break

        return self.status
        # back to parents node

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Do you think we answered your question?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No, I wanted something completely different.")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if self.co.is_positive(confirm_response["content"].lower()):
            return State.SUCCESS
        return State.FAILURE


class VariantNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("VARIANT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Do you think we answered your question?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No, I need clarification")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if self.co.is_positive(confirm_response["content"].lower()):
            return State.SUCCESS
        return State.FAILURE


class ComplementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("COMPLEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Do you think we answered your question?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "I would like another explanation.")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if self.co.is_positive(confirm_response["content"].lower()):
            return State.SUCCESS
        return State.FAILURE


class SupplementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("SUPPLEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Do you think we answered your question?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "I would like more information.")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if self.co.is_positive(confirm_response["content"].lower()):
            return State.SUCCESS
        return State.FAILURE
