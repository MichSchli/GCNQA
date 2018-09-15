import time

import sys
from SPARQLWrapper import SPARQLWrapper, JSON


class VirtuosoGraphReader:

    suboptimal_rels = None

    def __init__(self, ):
        self.endpoint = "http://localhost:8890/sparql"
        self.prefix = "http://rdf.freebase.com/ns/"

    def start_new_entity(self):
        self.suboptimal_rels = None

    def get_names(self, entity):
        db_interface = self.initialize_sparql_interface()

        query_string = "PREFIX ns: <" + self.prefix + ">\n"
        query_string += "select * where {\n"
        query_string += "ns:" + entity.split("/ns/")[-1] + " ns:type.object.name ?o .\n"
        query_string += "filter ( "
        query_string += "\nlang(?o) = 'en'"
        query_string += " )\n"

        query_string += "}"
        results = self.execute_query(db_interface, query_string)

        return [r["o"]["value"] for r in results["results"]["bindings"]]

    def get_immediate_neighbors(self, entity, forward=True, hyperedges=False):
        results = self.query_virtuoso(entity, forward=forward, hyperedges=hyperedges)

        return_val = []
        for result in results["results"]["bindings"]:
            if forward:
                edge = result["r"]["value"]
                target = result["o"]["value"]
            else:
                edge = result["r"]["value"] + ".inverse"
                target = result["s"]["value"]

            names = []
            if target.startswith(self.prefix):
                names = self.get_names(target)

            if len(names) == 0:
                names = [target]

            for name in set(names):
                return_val.append([edge, name])

        return return_val

    def query_virtuoso(self, entity, forward=True, hyperedges=False):
        db_interface = self.initialize_sparql_interface()
        query_string = self.construct_neighbor_query(entity, hyperedges=hyperedges, forward=forward)
        results = self.execute_query(db_interface, query_string)
        return results

    def get_suboptimal_edges(self, entity, golds):
        return self.suboptimal_rels

    def compute_f1(self, predictions, targets):
        target = set(targets)
        predictions = set(predictions)

        tp = len(target & predictions)
        fp = len(predictions) - tp
        fn = len(target) - tp

        if tp > 0:
            precision = float(tp) / (tp + fp)
            recall = float(tp) / (tp + fn)

            return 2 * ((precision * recall) / (precision + recall))
        else:
            return 0

    def get_immediate_neighbor_dict(self, entity):
        forward_neighbors = self.get_immediate_neighbors(entity, forward=True)
        backward_neighbors = self.get_immediate_neighbors(entity, forward=False)

        return_d = {}
        for edge, target in forward_neighbors + backward_neighbors:
            if edge not in return_d:
                return_d[edge] = [target]
            else:
                return_d[edge].append(target)

        return return_d

    def get_neighbor_events(self, entity, forward=True):
        results = self.query_virtuoso(entity, forward=forward, hyperedges=True)

        return_val = []
        for result in results["results"]["bindings"]:
            if forward:
                edge = result["r"]["value"]
                target = result["o"]["value"]
            else:
                edge = result["r"]["value"] + ".inverse"
                target = result["s"]["value"]

            return_val.append([edge, target])

        return return_val

    def get_second_order_neighbors(self, entity):
        forward_events = self.get_neighbor_events(entity, forward=True)
        backward_events = self.get_neighbor_events(entity, forward=False)

        return_d = {}
        for edge_1, event in forward_events + backward_events:
            forward_neighbors = self.get_immediate_neighbors(event, forward=True, hyperedges=False)
            backward_neighbors = self.get_immediate_neighbors(event, forward=False, hyperedges=False)

            for edge_2, target in forward_neighbors + backward_neighbors:
                edge_combined = edge_1 + "\t" + edge_2
                if edge_combined not in return_d:
                    return_d[edge_combined] = [target]
                else:
                    return_d[edge_combined].append(target)

        return return_d

    def get_all_optimal_edges(self, entity, targets):
        nbd = self.get_immediate_neighbor_dict(entity)

        max_f1 = 0
        max_rels = []
        suboptimal_rels = []

        for relation, entities in nbd.items():
            f1 = self.compute_f1(entities, targets)
            processed_relation = self.process_direct_relation(relation)
            if max_f1 < f1:
                max_f1 = f1
                suboptimal_rels.extend(max_rels)
                max_rels = [processed_relation]
            elif max_f1 == f1:
                max_rels.append(processed_relation)
            else:
                suboptimal_rels.append(processed_relation)

        two_nbd = self.get_second_order_neighbors(entity)

        for relation, entities in two_nbd.items():
            f1 = self.compute_f1(entities, targets)
            if max_f1 < f1:
                max_f1 = f1
                suboptimal_rels.extend(max_rels)
                max_rels = [relation]
            elif max_f1 == f1:
                max_rels.append(relation)
            else:
                suboptimal_rels.append(relation)

        self.suboptimal_rels = suboptimal_rels

        return max_rels, max_f1

    def process_direct_relation(self, relation):
       if relation.endswith(".inverse"):
           r = relation[:-8]
           processed_relation = r + ".2\t" + r + ".1"
       else:
           r = relation
           processed_relation = r + ".1\t" + r + ".2"

       return processed_relation

    """
    Construct a query to retrieve all neighbors of a set of vertices.
    - hyperedges: If true, retrieve event neighbors. If false, retrieve entity neighbors.
    - forward: If true, retrieve edges where the centroids are the subject. If false, retrieve edges where the centroids are the object.
    """

    def construct_neighbor_query(self, entity, hyperedges=True, forward=True):
        center = "s" if forward else "o"
        other = "o" if forward else "s"

        query_string = "PREFIX ns: <" + self.prefix + ">\n"
        query_string += "select * where {\n"
        query_string += "?s ?r ?o .\n"
        query_string += "values ?" + center + " {" + "ns:" + entity.split("/ns/")[-1] + "}\n"
        query_string += "filter ( "

        if hyperedges:
            query_string += "( not exists { ?" + other + " ns:type.object.name ?name } && !isLiteral(?" + other + ") && strstarts(str(?" + other + "), \"" + self.prefix + "\") )"
        else:
            query_string += "( exists { ?" + other + " ns:type.object.name ?name } || isLiteral(?" + other + ") )"

        query_string += "\n&& (!isLiteral(?" + other + ") || lang(?" + other + ") = 'en' || datatype(?" + other + ") != xsd:string || datatype(?" + other + ") != rdf:langString )"
        # Take out all schemastaging for now. Might consider putting some parts back in later:
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/base.schemastaging\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/key/wikipedia\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/common.topic.topic_equivalent_webpage\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/common.topic.webpage\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/type.object.key\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/base.yupgrade.user.topics\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/common.topic.description\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/common.document.text\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/type.type.instance\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/type.object.type\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/type.object.name\" )"
        query_string += "\n&& !strstarts(str(?r), \"http://rdf.freebase.com/ns/type.object.alias\" )"
        query_string += " )\n"

        query_string += "}"

        return query_string

    def execute_query(self, db_interface, query_string):
        # print(query_string)
        db_interface.setQuery(query_string)
        retrieved = False
        trial_counter = 0
        while not retrieved:
            try:
                results = db_interface.query().convert()
                retrieved = True
            except:
                trial_counter += 1
                if trial_counter == 5:
                    return None

                #print("Query failed. Reattempting in 5 seconds...\n", file=sys.stderr)
                #print(query_string, file=sys.stderr)

                time.sleep(5)
        return results

    def initialize_sparql_interface(self):
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setReturnFormat(JSON)
        return sparql
