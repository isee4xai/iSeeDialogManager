import business.bt.nodes.node as node
from business.bt.nodes.type import State
import business.coordinator as c


class PriorityNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("PRIORITY "+str(self.status) + " " + str(self.id))

    async def tick(self):

        for child in self.children:
            if (await child.tick() == State.SUCCESS):
                self.status = State.SUCCESS
                break

        return self.status
        # back to parents node

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()


class SequenceNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("SEQUENCE "+str(self.status) + " " + str(self.id))

    async def tick(self):

        self.status = State.SUCCESS
        for child in self.children:
            if (await child.tick() == State.FAILURE):
                self.status = State.FAILURE
                break

        # back to parents node
        return self.status

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()


class EvaluationStrategyNode(SequenceNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "EVALUATION STRATEGY " + str(self.status) + " " + str(self.id)

    async def tick(self):

        self.status = State.SUCCESS
        for child in self.children:
            if (await child.tick() == State.FAILURE):
                # self.status = State.FAILURE
                break

        # back to parents node
        return self.status


class ExplanationStrategyNode(SequenceNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "EXPLANATION STRATEGY " + str(self.status) + " " + str(self.id)

    async def tick(self):

        self.status = State.SUCCESS
        for child in self.children:
            if (await child.tick() == State.FAILURE):
                self.status = State.FAILURE
                break

        # back to parents node
        return self.status