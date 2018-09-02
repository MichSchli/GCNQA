class GraphReader:

    def __init__(self, filename):
        self.edges = []
        with open(filename, 'r') as g_file:
            for line in g_file:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    self.add_edge(parts[0], parts[1], parts[2])

    def add_edge(self, subject, relation, object):
        self.edges.append([subject, relation, object])

    def query(self, entity, rel_1, rel_2):
        targets = []
        if rel_1.endswith(".1") and rel_2.endswith(".2") and rel_1[:-2] == rel_2[:-2]:
            for edge in self.edges:
                if edge[0] == entity and edge[1] == rel_1[:-2]:
                    targets.append(edge[2])
        elif rel_2.endswith(".1") and rel_1.endswith(".2") and rel_1[:-2] == rel_2[:-2]:
            for edge in self.edges:
                if edge[2] == entity and edge[1] == rel_1[:-2]:
                    targets.append(edge[0])
        else:
            intermediates = []
            inv = rel_1.endswith(".inverse")
            if inv:
                rel_1 = rel_1[:-8]
            for edge in self.edges:
                if not inv and edge[0] == entity and edge[1] == rel_1:
                    intermediates.append(edge[2])
                elif inv and edge[2] == entity and edge[1] == rel_1:
                    intermediates.append(edge[0])

            inv = rel_2.endswith(".inverse")
            if inv:
                rel_2 = rel_2[:-8]

            for edge in self.edges:
                if not inv and edge[0] in intermediates and edge[1] == rel_2:
                    targets.append(edge[2])
                elif inv and edge[2] in intermediates and edge[1] == rel_2:
                    targets.append(edge[0])

        return list(set(targets))

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

    def get_optimal_edge(self, entity, targets):
        nbd = self.get_immediate_neighbor_dict(entity)

        max_f1 = 0
        max_rel = None

        for relation, entities in nbd.items():
            f1 = self.compute_f1(entities, targets)
            if max_f1 < f1:
                max_f1 = f1
                max_rel = relation

        if max_rel is not None:
            if max_rel.endswith(".inverse"):
                r = max_rel[:-8]
                max_rel = r + ".2\t" + r + ".1"
            else:
                r = max_rel
                max_rel = r + ".1\t" + r + ".2"

        if max_f1 == 1.0:
            return max_rel, max_f1

        two_nbd = self.get_second_order_neighbors(nbd)

        for relation, entities in two_nbd.items():
            f1 = self.compute_f1(entities, targets)
            if max_f1 < f1:
                max_f1 = f1
                max_rel = relation

        if max_rel is None:
            return "UNK", max_f1

        return max_rel, max_f1

    def get_all_optimal_edges(self, entity, targets):
        nbd = self.get_immediate_neighbor_dict(entity)

        max_f1 = 0
        max_rels = []

        for relation, entities in nbd.items():
            f1 = self.compute_f1(entities, targets)
            processed_relation = self.process_direct_relation(relation)
            if max_f1 < f1:
                max_f1 = f1
                max_rels = [processed_relation]
            elif max_f1 == f1:
                max_rels.append(processed_relation)

        two_nbd = self.get_second_order_neighbors(nbd)

        for relation, entities in two_nbd.items():
            f1 = self.compute_f1(entities, targets)
            if max_f1 < f1:
                max_f1 = f1
                max_rels = [relation]
            elif max_f1 == f1:
                max_rels.append(relation)

        return max_rels, max_f1

    def process_direct_relation(self, relation):
       if relation.endswith(".inverse"):
           r = relation[:-8]
           processed_relation = r + ".2\t" + r + ".1"
       else:
           r = relation
           processed_relation = r + ".1\t" + r + ".2"

       return processed_relation

    def get_suboptimal_edges(self, entity, targets):
        nbd = self.get_immediate_neighbor_dict(entity)

        max_f1 = 0
        max_rels = []
        suboptimal_edges = []

        for relation, entities in nbd.items():
            f1 = self.compute_f1(entities, targets)
            processed_relation = self.process_direct_relation(relation)
            if max_f1 < f1:
                max_f1 = f1
                suboptimal_edges.extend(max_rels)
                max_rels = [processed_relation]
            elif max_f1 == f1:
                max_rels.append(processed_relation)
            else:
                suboptimal_edges.append(processed_relation)

        two_nbd = self.get_second_order_neighbors(nbd)

        for relation, entities in two_nbd.items():
            f1 = self.compute_f1(entities, targets)
            if max_f1 < f1:
                max_f1 = f1
                suboptimal_edges.extend(max_rels)
                max_rels = [relation]
            elif max_f1 == f1:
                max_rels.append(relation)
            else:
                suboptimal_edges.append(relation)

        return suboptimal_edges

    def get_immediate_neighbor_dict(self, entity):
        d = {}

        for s,r,o in self.edges:
            if s == entity:
                r_keyword = r
                if r_keyword not in d:
                    d[r_keyword] = []
                d[r_keyword].append(o)

            elif o == entity:
                r_keyword = r + ".inverse"
                if r_keyword not in d:
                    d[r_keyword] = []
                d[r_keyword].append(s)

        return d

    def get_second_order_neighbors(self, nbd):
        d = {}

        for rel_1, o_list in nbd.items():
            for o in o_list:
                if not o.startswith("e_"):
                    continue

                nb_2 = self.get_immediate_neighbor_dict(o)
                for rel_2, t_list in nb_2.items():
                    key = rel_1 + "\t" + rel_2
                    if key not in d:
                        d[key] = []

                    d[key].extend(t_list)
                    d[key] = list(set(d[key]))

        return d
