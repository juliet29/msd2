from typing import NamedTuple, Any
from cyclopts import App
from loguru import logger
from utils4plans.logconfig import logset
import networkx as nx

quick_studies_app = App()


# def test_nx_types():
#     G:tuple[str, dict[str, int]] = nx.Graph()
#     G.add_node("one", data=1)
#     pass


class MyNode(NamedTuple):
    name: str
    num: int


class MyGraph(nx.Graph):
    def add_node(
        self, node_for_adding: str, data: MyData, **attr: Any
    ) -> None: ...  # attr: Set or change node attributes using key=value

    # def nodes(self) -> nx.classes.reportviews.NodeView[MyNode]: ...


# def expect_graph(G: Graph[tuple[str, dict[str, int]]]):
def expect_graph(G: MyGraph):
    G.add_node("node1", data=MyData("h", 1))
    # G.add_node("hei")
    # G.add_node(("one", {"data": 1}))
    return G


@quick_studies_app.command()
def test():
    G = nx.Graph()
    new_G = expect_graph(G)
    nodes: list[str] = [i for i in G.nodes]
    logger.debug(new_G)

    logger.debug(nodes)
    nodes2: list[tuple[str, dict["data", MyData]]] = [
        (i, j) for i, j in G.nodes(data=True)
    ]
    logger.debug(nodes2)


def main():
    logset()
    quick_studies_app()


if __name__ == "__main__":
    main()
