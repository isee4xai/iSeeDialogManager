from business.bt.nodes.action import ActionNode, Succeder, Failer, GreeterNode, InitialiserNode, KnowledgeQuestionNode
from business.bt.nodes.action import QuestionNode, NeedQuestionNode, PersonaQuestionNode, ExplainerNode
from business.bt.nodes.modifier import UsecaseModifierNode, WorldModifierNode
from business.bt.nodes.condition import ConditionNode, EqualNode
from business.bt.nodes.composite import SequenceNode, PriorityNode, StrategyNode
from business.bt.nodes.decorator import LimitActivationNode, RepeatNode, RepTillFailNode, RepTillSuccNode, InverterNode
from business.bt.nodes.node import Node


def makeNode(type, id, label):
    res = Node(0)

    if type == "Action":
        res = ActionNode(id)
    elif type == "World Modifier":
        res = WorldModifierNode(id)
    elif type == "Usecase Modifier":
        res = UsecaseModifierNode(id)
    elif type == "Failer":
        res = Failer(id)
    elif type == "Question":
        res = QuestionNode(id)
    elif type == "Succeeder":
        res = Succeder(id)
    elif type == "Explanation Method":
        res = ExplainerNode(id)
    elif type == "Need Question":
        res = NeedQuestionNode(id)
    elif type == "Knowledge Question":
        res = KnowledgeQuestionNode(id)
    elif type == "Persona Question":
        res = PersonaQuestionNode(id)
    elif type == "Initialiser":
        res = InitialiserNode(id)
    elif type == "Greeter":
        res = GreeterNode(id)

    elif type == "Condition":
        res = ConditionNode(id)
    elif type == "Equal":
        res = EqualNode(id)

    elif type == "Priority":
        res = PriorityNode(id)
    elif type == "Sequence":
        res = SequenceNode(id)
    elif type == "Strategy":
        res = StrategyNode(id)

    elif type == "RepeatUntilFailure":
        res = RepTillFailNode(id)
    elif type == "RepeatUntilSuccess":
        res = RepTillSuccNode(id)
    elif type == "Limiter":
        res = LimitActivationNode(id)
    elif type == "Inverter":
        res = InverterNode(id)
    elif type == "Repeater":
        res = RepeatNode(id)

    else:
        print(type, id, label)
        print("no type")

    return res
