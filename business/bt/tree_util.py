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

        # create Node according to its type with factory
        currentNode = node_factory.makeNode(type, id, label)
        nodes[node_id] = currentNode

    # Do a second round to add the children now that every node is created
    for n in parser.bt_nodes:
        nodes.get(n).co = co
        if (parser.bt_nodes[n]["Concept"] == "Priority"
                or parser.bt_nodes[n]["Concept"] == "Sequence"):
            children = parser.bt_nodes[n]["firstChild"]
            while True:
                nodes.get(n).children.append(nodes.get(children["Id"]))
                children = children["Next"]
                if children is None:
                    break
                
        if (parser.bt_nodes[n]["Concept"] == "Replacement"
                or parser.bt_nodes[n]["Concept"] == "Variant"
                or parser.bt_nodes[n]["Concept"] == "Complement"
                or parser.bt_nodes[n]["Concept"] == "Supplement"):
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
                or parser.bt_nodes[n]["Concept"] == "Persona Question"
                or parser.bt_nodes[n]["Concept"] == "Knowledge Question"
                or parser.bt_nodes[n]["Concept"] == "Confirm Question"
                or parser.bt_nodes[n]["Concept"] == "Target Question"):
            nodes.get(n).question = parser.bt_nodes[n]["properties"]["question"]
            nodes.get(n).variable = parser.bt_nodes[n]["properties"]["variable"]

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
            nodes.get(n).params = parser.bt_nodes[n]["params"] if "params" in parser.bt_nodes[n] else {}
            nodes.get(n).endpoint = parser.bt_nodes[n]["Instance"]

    root_id = parser.bt_root
    root = node.RootNode('0')
    root.children.append(nodes.get(root_id))

    return bt.Tree(root, nodes)


def printTree(root, level=0):
    print(" - " * level, root.toString())
    if (hasattr(root, "children")):
        for child in root.children:
            printTree(child, level + 1)
