import json
from typing import Dict
import data.parser as parser
import business.bt.nodes.node as node
import business.bt.nodes.factory as node_factory
import business.bt.bt as bt


def generate_tree_from_file(path, co):
    _parser = parser.TreeFileParser(path)
    return generate_tree(_parser, co)


def generate_tree_from_obj(obj, co):
    _parser = parser.TreeObjParser(obj)
    return generate_tree(_parser, co)


def generate_tree(parser, co):
    nodes: Dict[str, node.Node] = {}

    for node_id in parser.bt_nodes:

        type = parser.bt_nodes[node_id]["Concept"]
        id = parser.bt_nodes[node_id]["id"]
        label = parser.bt_nodes[node_id]["Instance"]
        # print(type, id, label)

        # create Node according to its type with factory
        currentNode = node_factory.makeNode(type, id, label)
        nodes[node_id] = currentNode

    # Do a second round to add the children now that every node is created
    for n in parser.bt_nodes:
        nodes.get(n).co = co
        if (parser.bt_nodes[n]["Concept"] == "Priority"
                or parser.bt_nodes[n]["Concept"] == "Sequence"
                or parser.bt_nodes[n]["Concept"] == "Strategy"):
            children = parser.bt_nodes[n]["firstChild"]
            while True:
                nodes.get(n).children.append(nodes.get(children["Id"]))
                children = children["Next"]
                if children is None:
                    break

        if (parser.bt_nodes[n]["Concept"] == "RepeatUntilSuccess"
                or parser.bt_nodes[n]["Concept"] == "RepeatUntilFailure"
                or parser.bt_nodes[n]["Concept"] == "Limiter"
                or parser.bt_nodes[n]["Concept"] == "Repeater"
                or parser.bt_nodes[n]["Concept"] == "Inverter"):
            children = parser.bt_nodes[n]["firstChild"]
            nodes.get(n).children = [nodes.get(children["Id"])]

        if (parser.bt_nodes[n]["Concept"] == "RepeatUntilSuccess"
                or parser.bt_nodes[n]["Concept"] == "RepeatUntilFailure"
                or parser.bt_nodes[n]["Concept"] == "Limiter"
                or parser.bt_nodes[n]["Concept"] == "Repeater"):
            nodes.get(n).limit = parser.bt_nodes[n]["properties"]["maxLoop"]

        if (parser.bt_nodes[n]["Concept"] == "Question"
                or parser.bt_nodes[n]["Concept"] == "Need Question"
                or parser.bt_nodes[n]["Concept"] == "Persona Question"):
            nodes.get(n).question = parser.bt_nodes[n]["properties"]["question"]
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

        if parser.bt_nodes[n]["Concept"] == "Knowledge Question":
            nodes.get(n).question = parser.bt_nodes[n]["properties"]["question"]
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]
            nodes.get(n).question_data = parser.bt_nodes[n]["properties"]["question_data"]

        if parser.bt_nodes[n]["Concept"] == "Greeter":
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

        if (parser.bt_nodes[n]["Concept"] == "Failer"
                or parser.bt_nodes[n]["Concept"] == "Succeeder"
                or parser.bt_nodes[n]["Concept"] == "Information"):
            nodes.get(n).message = parser.bt_nodes[n]["properties"]["message"]

        # only True or False values accepted; World need value, Usecase does not
        if (parser.bt_nodes[n]["Concept"] == "World Modifier"
                or parser.bt_nodes[n]["Concept"] == "Usecase Modifier"):
            if parser.bt_nodes[n]["properties"]:
                key = list(parser.bt_nodes[n]["properties"].keys())[0]
                nodes.get(n).variable = key
                val = parser.bt_nodes[n]["properties"][key]
                if val == "True" or val == "False":
                    nodes.get(n).value = bool(val if val == "True" else "")

        # set of conditions aggregated using AND
        if (parser.bt_nodes[n]["Concept"] == "Equal"
                or parser.bt_nodes[n]["Concept"] == "Condition"):
            nodes.get(n).variables = {key: bool(val if val == "True" else "")
                                      for key, val in parser.bt_nodes[n]["properties"].items()}

        if parser.bt_nodes[n]["Concept"] == "Explanation Method":
            nodes.get(n).params = parser.bt_nodes[n]["params"]

    root_id = parser.bt_root
    root = node.RootNode('0')
    root.children.append(nodes.get(root_id))

    return bt.Tree(root, nodes)


def printTree(root, level=0):
    print(" - " * level, root.toString())
    if (hasattr(root, "children")):
        for child in root.children:
            printTree(child, level + 1)
