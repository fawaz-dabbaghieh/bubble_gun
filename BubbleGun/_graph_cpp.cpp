#include <Python.h>
#include <structmember.h>

#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>

typedef struct {
    PyObject_HEAD
    PyObject *id;
    PyObject *seq;
    long seq_len;
    PyObject *start;
    PyObject *end;
    int visited;
    PyObject *optional_info;
    long which_chain;
    long which_allele;
    long which_b;
    long which_sb;
} NodeObject;

static void Node_dealloc(NodeObject *self) {
    // Mirror BubbleGun.Node cleanup (decref Python-owned fields).
    Py_XDECREF(self->id);
    Py_XDECREF(self->seq);
    Py_XDECREF(self->start);
    Py_XDECREF(self->end);
    Py_XDECREF(self->optional_info);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static int Node_init(NodeObject *self, PyObject *args, PyObject *kwds) {
    // Equivalent to BubbleGun.Node.__init__: initialize fields and defaults.
    PyObject *identifier = nullptr;
    static char *kwlist[] = {const_cast<char *>("identifier"), nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &identifier)) {
        return -1;
    }
    PyObject *id_str = PyUnicode_FromObject(identifier);
    if (!id_str) {
        return -1;
    }
    self->id = id_str;
    self->seq = PyUnicode_FromString("");
    if (!self->seq) {
        return -1;
    }
    self->seq_len = 0;
    // Use list to match Python Node.start/end mutations across the codebase.
    self->start = PyList_New(0);
    self->end = PyList_New(0);
    if (!self->start || !self->end) {
        return -1;
    }
    self->visited = 0;
    self->optional_info = PyUnicode_FromString("");
    if (!self->optional_info) {
        return -1;
    }
    self->which_chain = 0;
    self->which_allele = -1;
    self->which_b = 0;
    self->which_sb = 0;
    return 0;
}

static PyObject *Node_neighbors(NodeObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Node.neighbors: return sorted neighbor ids from start/end.
    PyObject *neighbors = PyList_New(0);
    if (!neighbors) {
        return nullptr;
    }
    Py_ssize_t start_size = PyList_Size(self->start);
    for (Py_ssize_t i = 0; i < start_size; ++i) {
        PyObject *item = PyList_GetItem(self->start, i);
        if (!item || !PyTuple_Check(item)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(item, 0);
        if (neighbor_id) {
            PyList_Append(neighbors, neighbor_id);
        }
    }
    Py_ssize_t end_size = PyList_Size(self->end);
    for (Py_ssize_t i = 0; i < end_size; ++i) {
        PyObject *item = PyList_GetItem(self->end, i);
        if (!item || !PyTuple_Check(item)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(item, 0);
        if (neighbor_id) {
            PyList_Append(neighbors, neighbor_id);
        }
    }
    PyList_Sort(neighbors);
    return neighbors;
}

static PyObject *Node_in_direction(NodeObject *self, PyObject *args) {
    // Match BubbleGun.Node.in_direction: check neighbor in a given direction.
    PyObject *node = nullptr;
    int direction = 0;
    if (!PyArg_ParseTuple(args, "Oi", &node, &direction)) {
        return nullptr;
    }
    PyObject *edges = (direction == 0) ? self->start : self->end;
    Py_ssize_t size = PyList_Size(edges);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject *item = PyList_GetItem(edges, i);
        if (!item || !PyTuple_Check(item)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(item, 0);
        if (!neighbor_id) {
            continue;
        }
        int eq = PyObject_RichCompareBool(neighbor_id, node, Py_EQ);
        if (eq == 1) {
            Py_RETURN_TRUE;
        } else if (eq < 0) {
            return nullptr;
        }
    }
    Py_RETURN_FALSE;
}

static PyObject *Node_children(NodeObject *self, PyObject *args) {
    // Match BubbleGun.Node.children: list neighbors in a direction.
    int direction = 0;
    if (!PyArg_ParseTuple(args, "i", &direction)) {
        return nullptr;
    }
    if (direction != 0 && direction != 1) {
        PyErr_Format(PyExc_Exception, "Trying to access a wrong direction in node");
        return nullptr;
    }
    PyObject *edges = (direction == 0) ? self->start : self->end;
    PyObject *children = PyList_New(0);
    if (!children) {
        return nullptr;
    }
    Py_ssize_t size = PyList_Size(edges);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject *item = PyList_GetItem(edges, i);
        if (!item || !PyTuple_Check(item)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(item, 0);
        if (neighbor_id) {
            PyList_Append(children, neighbor_id);
        }
    }
    return children;
}

static PyMethodDef Node_methods[] = {
    {"neighbors", (PyCFunction)Node_neighbors, METH_NOARGS, nullptr},
    {"in_direction", (PyCFunction)Node_in_direction, METH_VARARGS, nullptr},
    {"children", (PyCFunction)Node_children, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyMemberDef Node_members[] = {
    {"id", T_OBJECT_EX, offsetof(NodeObject, id), 0, nullptr},
    {"seq", T_OBJECT_EX, offsetof(NodeObject, seq), 0, nullptr},
    {"seq_len", T_LONG, offsetof(NodeObject, seq_len), 0, nullptr},
    {"start", T_OBJECT_EX, offsetof(NodeObject, start), 0, nullptr},
    {"end", T_OBJECT_EX, offsetof(NodeObject, end), 0, nullptr},
    {"visited", T_INT, offsetof(NodeObject, visited), 0, nullptr},
    {"optional_info", T_OBJECT_EX, offsetof(NodeObject, optional_info), 0, nullptr},
    {"which_chain", T_LONG, offsetof(NodeObject, which_chain), 0, nullptr},
    {"which_allele", T_LONG, offsetof(NodeObject, which_allele), 0, nullptr},
    {"which_b", T_LONG, offsetof(NodeObject, which_b), 0, nullptr},
    {"which_sb", T_LONG, offsetof(NodeObject, which_sb), 0, nullptr},
    {nullptr, 0, 0, 0, nullptr}
};

static PyTypeObject NodeType = {
    PyVarObject_HEAD_INIT(nullptr, 0)
};

typedef struct {
    PyObject_HEAD
    PyObject *nodes;
    PyObject *b_chains;
    PyObject *bubbles;
    int compacted;
} GraphObject;

struct Edge {
    std::string from;
    std::string to;
    bool from_start;
    bool to_end;
    long overlap;
};

static void Graph_dealloc(GraphObject *self) {
    Py_XDECREF(self->nodes);
    Py_XDECREF(self->b_chains);
    Py_XDECREF(self->bubbles);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static std::vector<std::string> split_tabs(const std::string &line) {
    // Helper for read_gfa parity: split tab-delimited GFA fields.
    std::vector<std::string> parts;
    size_t start = 0;
    while (start <= line.size()) {
        size_t pos = line.find('\t', start);
        if (pos == std::string::npos) {
            parts.emplace_back(line.substr(start));
            break;
        }
        parts.emplace_back(line.substr(start, pos - start));
        start = pos + 1;
    }
    return parts;
}

static int add_edge_unique(PyObject *list_obj, PyObject *tuple_obj) {
    // Keep GFA edge inserts unique, matching graph_io.read_gfa behavior.
    int contains = PySequence_Contains(list_obj, tuple_obj);
    if (contains < 0) {
        return -1;
    }
    if (contains == 0) {
        if (PyList_Append(list_obj, tuple_obj) < 0) {
            return -1;
        }
    }
    return 0;
}

static PyObject *make_edge_tuple(PyObject *node_id, long direction, long overlap) {
    // Build the (neighbor_id, direction, overlap) tuple used in Node.start/end.
    PyObject *dir_obj = PyLong_FromLong(direction);
    PyObject *ov_obj = PyLong_FromLong(overlap);
    if (!dir_obj || !ov_obj) {
        Py_XDECREF(dir_obj);
        Py_XDECREF(ov_obj);
        return nullptr;
    }
    PyObject *tuple_obj = PyTuple_Pack(3, node_id, dir_obj, ov_obj);
    Py_DECREF(dir_obj);
    Py_DECREF(ov_obj);
    return tuple_obj;
}

static int remove_edge_from_list(PyObject *list_obj, PyObject *edge_tuple) {
    // Remove the first matching edge tuple (graph_io uses lists, not sets).
    // Linear scan keeps semantics consistent even if duplicates slip in.
    Py_ssize_t size = PyList_Size(list_obj);
    if (size < 0) {
        return -1;
    }
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject *item = PyList_GetItem(list_obj, i);
        if (!item) {
            return -1;
        }
        int eq = PyObject_RichCompareBool(item, edge_tuple, Py_EQ);
        if (eq < 0) {
            return -1;
        }
        if (eq == 1) {
            if (PySequence_DelItem(list_obj, i) < 0) {
                return -1;
            }
            break;
        }
    }
    return 0;
}

static int Graph_parse_gfa(GraphObject *self, const char *path, int low_memory) {
    // C++ equivalent of graph_io.read_gfa: parse S/L lines into Node objects.
    std::ifstream infile(path);
    if (!infile) {
        PyErr_Format(PyExc_SystemExit, "graph file %s does not exist", path);
        return -1;
    }

    std::vector<Edge> edges;
    std::unordered_map<std::string, PyObject *> node_map;

    std::string line;
    while (std::getline(infile, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty()) {
            continue;
        }
        if (line[0] == 'S' && (line.size() == 1 || line[1] == '\t')) {
            std::vector<std::string> parts = split_tabs(line);
            if (parts.size() < 3) {
                continue;
            }
            const std::string &node_id = parts[1];
            const std::string &seq = parts[2];

            PyObject *id_obj = PyUnicode_FromString(node_id.c_str());
            if (!id_obj) {
                return -1;
            }
            PyObject *node_obj = PyObject_CallFunction((PyObject *)&NodeType, "O", id_obj);
            if (!node_obj) {
                Py_DECREF(id_obj);
                return -1;
            }

            NodeObject *node = (NodeObject *)node_obj;
            // When low_memory is on, omit sequences to reduce RAM (Python parity).
            if (!low_memory) {
                PyObject *seq_obj = PyUnicode_FromString(seq.c_str());
                if (!seq_obj) {
                    Py_DECREF(id_obj);
                    Py_DECREF(node_obj);
                    return -1;
                }
                Py_DECREF(node->seq);
                node->seq = seq_obj;
                node->seq_len = static_cast<long>(seq.size());
            }
            if (parts.size() > 3) {
                std::string optional;
                for (size_t i = 3; i < parts.size(); ++i) {
                    if (i > 3) {
                        optional += "\t";
                    }
                    optional += parts[i];
                }
                PyObject *opt_obj = PyUnicode_FromString(optional.c_str());
                if (!opt_obj) {
                    Py_DECREF(id_obj);
                    Py_DECREF(node_obj);
                    return -1;
                }
                Py_DECREF(node->optional_info);
                node->optional_info = opt_obj;
            }

            if (PyDict_SetItem(self->nodes, id_obj, node_obj) < 0) {
                Py_DECREF(id_obj);
                Py_DECREF(node_obj);
                return -1;
            }
            node_map[node_id] = node_obj;
            Py_DECREF(id_obj);
            Py_DECREF(node_obj);
        } else if (line[0] == 'L' && (line.size() == 1 || line[1] == '\t')) {
            std::vector<std::string> parts = split_tabs(line);
            if (parts.size() < 6) {
                continue;
            }
            Edge edge;
            edge.from = parts[1];
            edge.to = parts[3];
            edge.from_start = (parts[2] == "-");
            edge.to_end = (parts[4] == "-");
            if (parts[5] == "*") {
                edge.overlap = 0;
            } else {
                std::string overlap = parts[5];
                if (!overlap.empty() && overlap.back() == 'M') {
                    overlap.pop_back();
                }
                edge.overlap = std::stol(overlap);
            }
            edges.push_back(edge);
        }
    }

    for (const auto &edge : edges) {
        auto from_it = node_map.find(edge.from);
        auto to_it = node_map.find(edge.to);
        if (from_it == node_map.end()) {
            PyErr_WarnFormat(PyExc_UserWarning, 1,
                             "an edge between %s and %s exists but a node record for %s does not exist in the file. Skipping",
                             edge.from.c_str(), edge.to.c_str(), edge.from.c_str());
            continue;
        }
        if (to_it == node_map.end()) {
            PyErr_WarnFormat(PyExc_UserWarning, 1,
                             "an edge between %s and %s exists but a node record for %s does not exist in the file. Skipping",
                             edge.from.c_str(), edge.to.c_str(), edge.to.c_str());
            continue;
        }

        NodeObject *from_node = (NodeObject *)from_it->second;
        NodeObject *to_node = (NodeObject *)to_it->second;

        PyObject *from_id = PyUnicode_FromString(edge.from.c_str());
        PyObject *to_id = PyUnicode_FromString(edge.to.c_str());
        if (!from_id || !to_id) {
            Py_XDECREF(from_id);
            Py_XDECREF(to_id);
            return -1;
        }

        // Edge direction mapping mirrors graph_io.read_gfa cases.
        if (edge.from_start && edge.to_end) {
            PyObject *t1 = make_edge_tuple(to_id, 1, edge.overlap);
            PyObject *t2 = make_edge_tuple(from_id, 0, edge.overlap);
            if (!t1 || !t2) {
                Py_XDECREF(t1);
                Py_XDECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            if (add_edge_unique(from_node->start, t1) < 0 || add_edge_unique(to_node->end, t2) < 0) {
                Py_DECREF(t1);
                Py_DECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            Py_DECREF(t1);
            Py_DECREF(t2);
        } else if (edge.from_start && !edge.to_end) {
            PyObject *t1 = make_edge_tuple(to_id, 0, edge.overlap);
            PyObject *t2 = make_edge_tuple(from_id, 0, edge.overlap);
            if (!t1 || !t2) {
                Py_XDECREF(t1);
                Py_XDECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            if (add_edge_unique(from_node->start, t1) < 0 || add_edge_unique(to_node->start, t2) < 0) {
                Py_DECREF(t1);
                Py_DECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            Py_DECREF(t1);
            Py_DECREF(t2);
        } else if (!edge.from_start && !edge.to_end) {
            PyObject *t1 = make_edge_tuple(to_id, 0, edge.overlap);
            PyObject *t2 = make_edge_tuple(from_id, 1, edge.overlap);
            if (!t1 || !t2) {
                Py_XDECREF(t1);
                Py_XDECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            if (add_edge_unique(from_node->end, t1) < 0 || add_edge_unique(to_node->start, t2) < 0) {
                Py_DECREF(t1);
                Py_DECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            Py_DECREF(t1);
            Py_DECREF(t2);
        } else if (!edge.from_start && edge.to_end) {
            PyObject *t1 = make_edge_tuple(to_id, 1, edge.overlap);
            PyObject *t2 = make_edge_tuple(from_id, 1, edge.overlap);
            if (!t1 || !t2) {
                Py_XDECREF(t1);
                Py_XDECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            if (add_edge_unique(from_node->end, t1) < 0 || add_edge_unique(to_node->end, t2) < 0) {
                Py_DECREF(t1);
                Py_DECREF(t2);
                Py_DECREF(from_id);
                Py_DECREF(to_id);
                return -1;
            }
            Py_DECREF(t1);
            Py_DECREF(t2);
        }
        Py_DECREF(from_id);
        Py_DECREF(to_id);
    }
    return 0;
}

static int Graph_init(GraphObject *self, PyObject *args, PyObject *kwds) {
    // Match BubbleGun.Graph.__init__: load nodes + initialize chain/bubble state.
    PyObject *graph_file = Py_None;
    int low_memory = 0;
    static char *kwlist[] = {const_cast<char *>("graph_file"), const_cast<char *>("low_memory"), nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Oi", kwlist, &graph_file, &low_memory)) {
        return -1;
    }

    self->nodes = PyDict_New();
    self->b_chains = PySet_New(nullptr);
    self->bubbles = PyDict_New();
    self->compacted = 0;
    if (!self->nodes || !self->b_chains || !self->bubbles) {
        return -1;
    }

    if (graph_file != Py_None) {
        PyObject *path_obj = PyUnicode_FromObject(graph_file);
        if (!path_obj) {
            return -1;
        }
        const char *path = PyUnicode_AsUTF8(path_obj);
        if (!path) {
            Py_DECREF(path_obj);
            return -1;
        }
        int parse_status = Graph_parse_gfa(self, path, low_memory);
        Py_DECREF(path_obj);
        if (parse_status < 0) {
            return -1;
        }
    }
    return 0;
}

static Py_ssize_t Graph_length(PyObject *self) {
    // Match BubbleGun.Graph.__len__.
    GraphObject *graph = (GraphObject *)self;
    return PyDict_Size(graph->nodes);
}

static PyObject *Graph_str(PyObject *self) {
    // Match BubbleGun.Graph.__str__.
    GraphObject *graph = (GraphObject *)self;
    Py_ssize_t nodes_count = PyDict_Size(graph->nodes);
    Py_ssize_t chains_count = PySet_Size(graph->b_chains);
    return PyUnicode_FromFormat("The graph has %zd Nodes and %zd chains", nodes_count, chains_count);
}

static PyObject *Graph_add_chain(GraphObject *self, PyObject *args) {
    // Match BubbleGun.Graph.add_chain: normalize and track bubble chains.
    PyObject *chain = nullptr;
    if (!PyArg_ParseTuple(args, "O", &chain)) {
        return nullptr;
    }
    PyObject *sorted = PyObject_GetAttrString(chain, "sorted");
    if (!sorted) {
        return nullptr;
    }
    Py_ssize_t sorted_len = PyObject_Length(sorted);
    Py_DECREF(sorted);
    if (sorted_len == 0) {
        PyObject *find_ends = PyObject_CallMethod(chain, "find_ends", nullptr);
        if (!find_ends) {
            return nullptr;
        }
        Py_DECREF(find_ends);
        PyObject *sort_call = PyObject_CallMethod(chain, "sort", nullptr);
        if (!sort_call) {
            return nullptr;
        }
        Py_DECREF(sort_call);
    }
    PyObject *ends = PyObject_GetAttrString(chain, "ends");
    if (!ends) {
        return nullptr;
    }
    Py_ssize_t ends_len = PyObject_Length(ends);
    Py_DECREF(ends);
    if (ends_len != 2) {
        PyObject *chain_list = PyObject_CallMethod(chain, "list_chain", nullptr);
        if (!chain_list) {
            return nullptr;
        }
        PyObject *nodes_set = PySet_New(chain_list);
        Py_DECREF(chain_list);
        if (!nodes_set) {
            return nullptr;
        }
        PyObject *output_name = PyUnicode_FromString("circular_and_other_problematic_chains.gfa");
        if (!output_name) {
            Py_DECREF(nodes_set);
            return nullptr;
        }
        PyObject *result = PyObject_CallMethod((PyObject *)self, "write_graph",
                                               "OOii",
                                               nodes_set,
                                               output_name,
                                               1,
                                               0);
        Py_DECREF(output_name);
        Py_DECREF(nodes_set);
        if (!result) {
            return nullptr;
        }
        Py_DECREF(result);
    } else {
        if (PySet_Add(self->b_chains, chain) < 0) {
            return nullptr;
        }
    }
    Py_RETURN_NONE;
}

static PyObject *Graph_total_seq_length(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.total_seq_length.
    long long total = 0;
    PyObject *key = nullptr;
    PyObject *value = nullptr;
    Py_ssize_t pos = 0;
    while (PyDict_Next(self->nodes, &pos, &key, &value)) {
        if (PyObject_TypeCheck(value, &NodeType)) {
            total += ((NodeObject *)value)->seq_len;
        } else {
            PyObject *seq_len_obj = PyObject_GetAttrString(value, "seq_len");
            if (!seq_len_obj) {
                return nullptr;
            }
            total += PyLong_AsLongLong(seq_len_obj);
            Py_DECREF(seq_len_obj);
        }
    }
    return PyLong_FromLongLong(total);
}

static PyObject *Graph_longest_chain_bubble(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.longest_chain_bubble.
    Py_ssize_t count = PySet_Size(self->b_chains);
    if (count == 0) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty sequence");
        return nullptr;
    }
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *best_chain = nullptr;
    Py_ssize_t best_len = -1;
    PyObject *item = nullptr;
    while ((item = PyIter_Next(iter)) != nullptr) {
        Py_ssize_t length = PyObject_Length(item);
        if (length > best_len) {
            Py_XDECREF(best_chain);
            best_chain = item;
            best_len = length;
        } else {
            Py_DECREF(item);
        }
    }
    Py_DECREF(iter);
    if (!best_chain) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty sequence");
        return nullptr;
    }
    return best_chain;
}

static PyObject *Graph_longest_chain_seq(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.longest_chain_seq.
    Py_ssize_t count = PySet_Size(self->b_chains);
    if (count == 0) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty sequence");
        return nullptr;
    }
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *best_chain = nullptr;
    long long best_len = -1;
    PyObject *item = nullptr;
    while ((item = PyIter_Next(iter)) != nullptr) {
        PyObject *length_obj = PyObject_CallMethod(item, "length_seq", nullptr);
        if (!length_obj) {
            Py_DECREF(item);
            Py_DECREF(iter);
            Py_XDECREF(best_chain);
            return nullptr;
        }
        long long length = PyLong_AsLongLong(length_obj);
        Py_DECREF(length_obj);
        if (length > best_len) {
            Py_XDECREF(best_chain);
            best_chain = item;
            best_len = length;
        } else {
            Py_DECREF(item);
        }
    }
    Py_DECREF(iter);
    if (!best_chain) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty sequence");
        return nullptr;
    }
    return best_chain;
}

static PyObject *Graph_nodes_in_chains(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.nodes_in_chains.
    PyObject *all_nodes = PySet_New(nullptr);
    if (!all_nodes) {
        return nullptr;
    }
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        Py_DECREF(all_nodes);
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        PyObject *chain_list = PyObject_CallMethod(chain, "list_chain", nullptr);
        Py_DECREF(chain);
        if (!chain_list) {
            Py_DECREF(iter);
            Py_DECREF(all_nodes);
            return nullptr;
        }
        Py_ssize_t size = PyList_Size(chain_list);
        for (Py_ssize_t i = 0; i < size; ++i) {
            PyObject *node_id = PyList_GetItem(chain_list, i);
            if (node_id) {
                PySet_Add(all_nodes, node_id);
            }
        }
        Py_DECREF(chain_list);
    }
    Py_DECREF(iter);
    return all_nodes;
}

static PyObject *Graph_seq_in_chains(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.seq_in_chains.
    long long total = 0;
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        PyObject *length_obj = PyObject_CallMethod(chain, "length_seq", nullptr);
        Py_DECREF(chain);
        if (!length_obj) {
            Py_DECREF(iter);
            return nullptr;
        }
        total += PyLong_AsLongLong(length_obj);
        Py_DECREF(length_obj);
    }
    Py_DECREF(iter);
    return PyLong_FromLongLong(total);
}

static PyObject *Graph_chain_cov_node(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.chain_cov_node.
    PyObject *nodes_set = Graph_nodes_in_chains(self, nullptr);
    if (!nodes_set) {
        return nullptr;
    }
    double cov = 0.0;
    Py_ssize_t nodes_count = PyDict_Size(self->nodes);
    if (nodes_count > 0) {
        cov = (PySet_Size(nodes_set) * 100.0) / static_cast<double>(nodes_count);
    }
    Py_DECREF(nodes_set);
    return PyFloat_FromDouble(cov);
}

static PyObject *Graph_chain_cov_seq(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.chain_cov_seq.
    PyObject *chain_nodes = PySet_New(nullptr);
    if (!chain_nodes) {
        return nullptr;
    }
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        Py_DECREF(chain_nodes);
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        PyObject *chain_list = PyObject_CallMethod(chain, "list_chain", nullptr);
        Py_DECREF(chain);
        if (!chain_list) {
            Py_DECREF(iter);
            Py_DECREF(chain_nodes);
            return nullptr;
        }
        Py_ssize_t size = PyList_Size(chain_list);
        for (Py_ssize_t i = 0; i < size; ++i) {
            PyObject *node_id = PyList_GetItem(chain_list, i);
            if (node_id) {
                PySet_Add(chain_nodes, node_id);
            }
        }
        Py_DECREF(chain_list);
    }
    Py_DECREF(iter);

    long long total_seq = 0;
    PyObject *node_iter = PyObject_GetIter(chain_nodes);
    if (!node_iter) {
        Py_DECREF(chain_nodes);
        return nullptr;
    }
    PyObject *node_id = nullptr;
    while ((node_id = PyIter_Next(node_iter)) != nullptr) {
        PyObject *node = PyDict_GetItem(self->nodes, node_id);
        if (node) {
            if (PyObject_TypeCheck(node, &NodeType)) {
                total_seq += ((NodeObject *)node)->seq_len;
            } else {
                PyObject *seq_len_obj = PyObject_GetAttrString(node, "seq_len");
                if (!seq_len_obj) {
                    Py_DECREF(node_id);
                    Py_DECREF(node_iter);
                    Py_DECREF(chain_nodes);
                    return nullptr;
                }
                total_seq += PyLong_AsLongLong(seq_len_obj);
                Py_DECREF(seq_len_obj);
            }
        }
        Py_DECREF(node_id);
    }
    Py_DECREF(node_iter);

    PyObject *total_graph_seq_obj = Graph_total_seq_length(self, nullptr);
    if (!total_graph_seq_obj) {
        Py_DECREF(chain_nodes);
        return nullptr;
    }
    double total_graph_seq = PyLong_AsDouble(total_graph_seq_obj);
    Py_DECREF(total_graph_seq_obj);
    Py_DECREF(chain_nodes);
    if (total_graph_seq == 0.0) {
        return PyFloat_FromDouble(0.0);
    }
    return PyFloat_FromDouble((total_seq * 100.0) / total_graph_seq);
}

static PyObject *Graph_num_single_bubbles(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.num_single_bubbles.
    long long count = 0;
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        Py_ssize_t length = PyObject_Length(chain);
        Py_DECREF(chain);
        if (length == 1) {
            count += 1;
        }
    }
    Py_DECREF(iter);
    return PyLong_FromLongLong(count);
}

static PyObject *Graph_reset_visited(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.reset_visited.
    PyObject *key = nullptr;
    PyObject *value = nullptr;
    Py_ssize_t pos = 0;
    while (PyDict_Next(self->nodes, &pos, &key, &value)) {
        if (PyObject_TypeCheck(value, &NodeType)) {
            ((NodeObject *)value)->visited = 0;
        } else {
            if (PyObject_SetAttrString(value, "visited", Py_False) < 0) {
                return nullptr;
            }
        }
    }
    Py_RETURN_NONE;
}

static PyObject *Graph_bubble_number(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.bubble_number.
    long long simple = 0;
    long long super = 0;
    long long insertion = 0;
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        PyObject *bubbles = PyObject_GetAttrString(chain, "bubbles");
        Py_DECREF(chain);
        if (!bubbles) {
            Py_DECREF(iter);
            return nullptr;
        }
        PyObject *b_iter = PyObject_GetIter(bubbles);
        Py_DECREF(bubbles);
        if (!b_iter) {
            Py_DECREF(iter);
            return nullptr;
        }
        PyObject *bubble = nullptr;
        while ((bubble = PyIter_Next(b_iter)) != nullptr) {
            PyObject *is_simple = PyObject_CallMethod(bubble, "is_simple", nullptr);
            if (!is_simple) {
                Py_DECREF(bubble);
                Py_DECREF(b_iter);
                Py_DECREF(iter);
                return nullptr;
            }
            int simple_res = PyObject_IsTrue(is_simple);
            Py_DECREF(is_simple);
            if (simple_res == 1) {
                simple += 1;
                Py_DECREF(bubble);
                continue;
            }
            PyObject *is_super = PyObject_CallMethod(bubble, "is_super", nullptr);
            if (!is_super) {
                Py_DECREF(bubble);
                Py_DECREF(b_iter);
                Py_DECREF(iter);
                return nullptr;
            }
            int super_res = PyObject_IsTrue(is_super);
            Py_DECREF(is_super);
            if (super_res == 1) {
                super += 1;
                Py_DECREF(bubble);
                continue;
            }
            PyObject *is_insertion = PyObject_CallMethod(bubble, "is_insertion", nullptr);
            if (!is_insertion) {
                Py_DECREF(bubble);
                Py_DECREF(b_iter);
                Py_DECREF(iter);
                return nullptr;
            }
            int ins_res = PyObject_IsTrue(is_insertion);
            Py_DECREF(is_insertion);
            if (ins_res == 1) {
                insertion += 1;
            }
            Py_DECREF(bubble);
        }
        Py_DECREF(b_iter);
    }
    Py_DECREF(iter);
    PyObject *result = PyList_New(3);
    if (!result) {
        return nullptr;
    }
    PyList_SetItem(result, 0, PyLong_FromLongLong(simple));
    PyList_SetItem(result, 1, PyLong_FromLongLong(super));
    PyList_SetItem(result, 2, PyLong_FromLongLong(insertion));
    return result;
}

static PyObject *Graph_remove_node(GraphObject *self, PyObject *args) {
    // Match BubbleGun.Graph.remove_node: remove node and its edges.
    PyObject *n_id = nullptr;
    if (!PyArg_ParseTuple(args, "O", &n_id)) {
        return nullptr;
    }
    PyObject *n_id_str = PyUnicode_FromObject(n_id);
    if (!n_id_str) {
        return nullptr;
    }
    PyObject *node_obj = PyDict_GetItem(self->nodes, n_id_str);
    if (!node_obj) {
        Py_DECREF(n_id_str);
        Py_RETURN_NONE;
    }
    if (!PyObject_TypeCheck(node_obj, &NodeType)) {
        Py_DECREF(n_id_str);
        Py_RETURN_NONE;
    }
    NodeObject *node = (NodeObject *)node_obj;

    PyObject *starts_copy = PySequence_List(node->start);
    if (!starts_copy) {
        Py_DECREF(n_id_str);
        return nullptr;
    }
    Py_ssize_t start_size = PyList_Size(starts_copy);
    for (Py_ssize_t i = 0; i < start_size; ++i) {
        PyObject *entry = PyList_GetItem(starts_copy, i);
        if (!entry || !PyTuple_Check(entry)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(entry, 0);
        long direction = PyLong_AsLong(PyTuple_GetItem(entry, 1));
        long overlap = PyLong_AsLong(PyTuple_GetItem(entry, 2));
        PyObject *neighbor_node_obj = PyDict_GetItem(self->nodes, neighbor_id);
        if (!neighbor_node_obj || !PyObject_TypeCheck(neighbor_node_obj, &NodeType)) {
            continue;
        }
        NodeObject *neighbor_node = (NodeObject *)neighbor_node_obj;
        PyObject *remove_tuple = make_edge_tuple(n_id_str, 0, overlap);
        if (!remove_tuple) {
            Py_DECREF(starts_copy);
            Py_DECREF(n_id_str);
            return nullptr;
        }
        PyObject *list_obj = (direction == 1) ? neighbor_node->end : neighbor_node->start;
        if (remove_edge_from_list(list_obj, remove_tuple) < 0) {
            Py_DECREF(starts_copy);
            Py_DECREF(n_id_str);
            Py_DECREF(remove_tuple);
            return nullptr;
        }
        Py_DECREF(remove_tuple);
    }
    Py_DECREF(starts_copy);

    PyObject *ends_copy = PySequence_List(node->end);
    if (!ends_copy) {
        Py_DECREF(n_id_str);
        return nullptr;
    }
    Py_ssize_t end_size = PyList_Size(ends_copy);
    for (Py_ssize_t i = 0; i < end_size; ++i) {
        PyObject *entry = PyList_GetItem(ends_copy, i);
        if (!entry || !PyTuple_Check(entry)) {
            continue;
        }
        PyObject *neighbor_id = PyTuple_GetItem(entry, 0);
        long direction = PyLong_AsLong(PyTuple_GetItem(entry, 1));
        long overlap = PyLong_AsLong(PyTuple_GetItem(entry, 2));
        PyObject *neighbor_node_obj = PyDict_GetItem(self->nodes, neighbor_id);
        if (!neighbor_node_obj || !PyObject_TypeCheck(neighbor_node_obj, &NodeType)) {
            continue;
        }
        NodeObject *neighbor_node = (NodeObject *)neighbor_node_obj;
        PyObject *remove_tuple = make_edge_tuple(n_id_str, 1, overlap);
        if (!remove_tuple) {
            Py_DECREF(ends_copy);
            Py_DECREF(n_id_str);
            return nullptr;
        }
        PyObject *list_obj = (direction == 1) ? neighbor_node->end : neighbor_node->start;
        if (remove_edge_from_list(list_obj, remove_tuple) < 0) {
            Py_DECREF(ends_copy);
            Py_DECREF(n_id_str);
            Py_DECREF(remove_tuple);
            return nullptr;
        }
        Py_DECREF(remove_tuple);
    }
    Py_DECREF(ends_copy);

    if (PyDict_DelItem(self->nodes, n_id_str) < 0) {
        Py_DECREF(n_id_str);
        return nullptr;
    }
    Py_DECREF(n_id_str);
    Py_RETURN_NONE;
}

static PyObject *Graph_remove_lonely_nodes(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.remove_lonely_nodes.
    PyObject *to_remove = PyList_New(0);
    if (!to_remove) {
        return nullptr;
    }
    PyObject *key = nullptr;
    PyObject *value = nullptr;
    Py_ssize_t pos = 0;
    while (PyDict_Next(self->nodes, &pos, &key, &value)) {
        PyObject *neighbors = PyObject_CallMethod(value, "neighbors", nullptr);
        if (!neighbors) {
            Py_DECREF(to_remove);
            return nullptr;
        }
        Py_ssize_t count = PyObject_Length(neighbors);
        Py_DECREF(neighbors);
        if (count == 0) {
            PyList_Append(to_remove, key);
        }
    }
    Py_ssize_t size = PyList_Size(to_remove);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject *node_id = PyList_GetItem(to_remove, i);
        PyObject *args = PyTuple_Pack(1, node_id);
        if (!args) {
            Py_DECREF(to_remove);
            return nullptr;
        }
        PyObject *result = Graph_remove_node(self, args);
        Py_DECREF(args);
        if (!result) {
            Py_DECREF(to_remove);
            return nullptr;
        }
        Py_DECREF(result);
    }
    Py_DECREF(to_remove);
    Py_RETURN_NONE;
}

static PyObject *Graph_compact(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Delegate to BubbleGun.compact_graph.compact_graph for shared logic.
    // Keeps graph mutation semantics identical to the Python implementation.
    PyObject *module = PyImport_ImportModule("BubbleGun.compact_graph");
    if (!module) {
        return nullptr;
    }
    PyObject *func = PyObject_GetAttrString(module, "compact_graph");
    Py_DECREF(module);
    if (!func) {
        return nullptr;
    }
    PyObject *result = PyObject_CallFunctionObjArgs(func, (PyObject *)self, nullptr);
    Py_DECREF(func);
    if (!result) {
        return nullptr;
    }
    Py_DECREF(result);
    self->compacted = 1;
    Py_RETURN_NONE;
}

static PyObject *Graph_write_graph(GraphObject *self, PyObject *args, PyObject *kwds) {
    // Delegate to BubbleGun.graph_io.write_gfa to keep output consistent.
    // The Python writer understands optional GFA fields and compacted graphs.
    PyObject *set_of_nodes = Py_None;
    PyObject *output_file = nullptr;
    int append = 0;
    int optional_info = 1;
    static char *kwlist[] = {const_cast<char *>("set_of_nodes"),
                             const_cast<char *>("output_file"),
                             const_cast<char *>("append"),
                             const_cast<char *>("optional_info"),
                             nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OOii", kwlist,
                                     &set_of_nodes, &output_file, &append, &optional_info)) {
        return nullptr;
    }
    if (!output_file || output_file == Py_None) {
        output_file = PyUnicode_FromString("output_graph.gfa");
    } else {
        Py_INCREF(output_file);
    }
    PyObject *output_str = PyUnicode_FromObject(output_file);
    Py_DECREF(output_file);
    if (!output_str) {
        return nullptr;
    }
    const char *output_cstr = PyUnicode_AsUTF8(output_str);
    if (!output_cstr) {
        Py_DECREF(output_str);
        return nullptr;
    }
    std::string output_path = output_cstr;
    if (output_path.size() < 4 || output_path.substr(output_path.size() - 4) != ".gfa") {
        output_path += ".gfa";
    }
    Py_DECREF(output_str);
    PyObject *output_obj = PyUnicode_FromString(output_path.c_str());
    if (!output_obj) {
        return nullptr;
    }

    PyObject *module = PyImport_ImportModule("BubbleGun.graph_io");
    if (!module) {
        Py_DECREF(output_obj);
        return nullptr;
    }
    PyObject *func = PyObject_GetAttrString(module, "write_gfa");
    Py_DECREF(module);
    if (!func) {
        Py_DECREF(output_obj);
        return nullptr;
    }
    PyObject *result = PyObject_CallFunctionObjArgs(
        func, (PyObject *)self,
        set_of_nodes == Py_None ? Py_None : set_of_nodes,
        output_obj,
        append ? Py_True : Py_False,
        optional_info ? Py_True : Py_False,
        nullptr);
    Py_DECREF(func);
    Py_DECREF(output_obj);
    if (!result) {
        return nullptr;
    }
    Py_DECREF(result);
    Py_RETURN_NONE;
}

static PyObject *Graph_write_b_chains(GraphObject *self, PyObject *args, PyObject *kwds) {
    // Delegate to BubbleGun.graph_io.write_chains to match Python output.
    PyObject *output_file = nullptr;
    static char *kwlist[] = {const_cast<char *>("output"), nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &output_file)) {
        return nullptr;
    }
    if (!output_file || output_file == Py_None) {
        output_file = PyUnicode_FromString("bubble_chains.gfa");
    } else {
        Py_INCREF(output_file);
    }
    PyObject *output_str = PyUnicode_FromObject(output_file);
    Py_DECREF(output_file);
    if (!output_str) {
        return nullptr;
    }
    const char *output_cstr = PyUnicode_AsUTF8(output_str);
    if (!output_cstr) {
        Py_DECREF(output_str);
        return nullptr;
    }
    std::string output_path = output_cstr;
    if (output_path.size() < 4 || output_path.substr(output_path.size() - 4) != ".gfa") {
        output_path += ".gfa";
    }
    Py_DECREF(output_str);
    PyObject *output_obj = PyUnicode_FromString(output_path.c_str());
    if (!output_obj) {
        return nullptr;
    }

    PyObject *module = PyImport_ImportModule("BubbleGun.graph_io");
    if (!module) {
        Py_DECREF(output_obj);
        return nullptr;
    }
    PyObject *func = PyObject_GetAttrString(module, "write_chains");
    Py_DECREF(module);
    if (!func) {
        Py_DECREF(output_obj);
        return nullptr;
    }
    int optional_info = self->compacted ? 0 : 1;
    PyObject *result = PyObject_CallFunctionObjArgs(
        func, (PyObject *)self,
        output_obj,
        optional_info ? Py_True : Py_False,
        nullptr);
    Py_DECREF(func);
    Py_DECREF(output_obj);
    if (!result) {
        return nullptr;
    }
    Py_DECREF(result);
    Py_RETURN_NONE;
}

static PyObject *Graph_biggest_comp(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Delegate to BubbleGun.connected_components.all_components.
    PyObject *module = PyImport_ImportModule("BubbleGun.connected_components");
    if (!module) {
        return nullptr;
    }
    PyObject *func = PyObject_GetAttrString(module, "all_components");
    Py_DECREF(module);
    if (!func) {
        return nullptr;
    }
    PyObject *components = PyObject_CallFunctionObjArgs(func, (PyObject *)self, nullptr);
    Py_DECREF(func);
    if (!components) {
        return nullptr;
    }
    PyObject *iter = PyObject_GetIter(components);
    if (!iter) {
        Py_DECREF(components);
        return nullptr;
    }
    PyObject *best = nullptr;
    Py_ssize_t best_len = -1;
    PyObject *item = nullptr;
    while ((item = PyIter_Next(iter)) != nullptr) {
        Py_ssize_t length = PyObject_Length(item);
        if (length > best_len) {
            Py_XDECREF(best);
            best = item;
            best_len = length;
        } else {
            Py_DECREF(item);
        }
    }
    Py_DECREF(iter);
    Py_DECREF(components);
    if (!best) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty sequence");
        return nullptr;
    }
    return best;
}

static PyObject *Graph_bfs(GraphObject *self, PyObject *args) {
    // Delegate to BubbleGun.bfs.bfs for neighborhood extraction.
    // Avoids re-implementing traversal logic and keeps CLI behavior stable.
    PyObject *start = nullptr;
    long size = 0;
    if (!PyArg_ParseTuple(args, "Ol", &start, &size)) {
        return nullptr;
    }
    PyObject *module = PyImport_ImportModule("BubbleGun.bfs");
    if (!module) {
        return nullptr;
    }
    PyObject *func = PyObject_GetAttrString(module, "bfs");
    Py_DECREF(module);
    if (!func) {
        return nullptr;
    }
    PyObject *size_obj = PyLong_FromLong(size);
    if (!size_obj) {
        Py_DECREF(func);
        return nullptr;
    }
    PyObject *result = PyObject_CallFunctionObjArgs(func, (PyObject *)self, start, size_obj, nullptr);
    Py_DECREF(size_obj);
    Py_DECREF(func);
    if (!result) {
        return nullptr;
    }
    return result;
}

static PyObject *Graph_fill_bubble_info(GraphObject *self, PyObject *Py_UNUSED(ignored)) {
    // Match BubbleGun.Graph.fill_bubble_info; updates which_* tags on nodes.
    long long b_counter = 0;
    long long chain_num = 0;
    PyObject *iter = PyObject_GetIter(self->b_chains);
    if (!iter) {
        return nullptr;
    }
    PyObject *chain = nullptr;
    while ((chain = PyIter_Next(iter)) != nullptr) {
        chain_num += 1;
        PyObject *sorted = PyObject_GetAttrString(chain, "sorted");
        if (!sorted) {
            Py_DECREF(chain);
            Py_DECREF(iter);
            return nullptr;
        }
        Py_ssize_t sorted_len = PyList_Size(sorted);
        for (Py_ssize_t i = 0; i < sorted_len; ++i) {
            PyObject *bubble = PyList_GetItem(sorted, i);
            if (!bubble) {
                continue;
            }
            b_counter += 1;
            PyObject *is_simple = PyObject_CallMethod(bubble, "is_simple", nullptr);
            if (!is_simple) {
                Py_DECREF(sorted);
                Py_DECREF(chain);
                Py_DECREF(iter);
                return nullptr;
            }
            int simple_res = PyObject_IsTrue(is_simple);
            Py_DECREF(is_simple);
            if (simple_res == 1) {
                PyObject *inside = PyObject_GetAttrString(bubble, "inside");
                if (!inside) {
                    Py_DECREF(sorted);
                    Py_DECREF(chain);
                    Py_DECREF(iter);
                    return nullptr;
                }
                Py_ssize_t inside_len = PyList_Size(inside);
                for (Py_ssize_t allele = 0; allele < inside_len; ++allele) {
                    PyObject *node = PyList_GetItem(inside, allele);
                    if (!node) {
                        continue;
                    }
                    PyObject *which_chain_obj = PyObject_GetAttrString(node, "which_chain");
                    if (!which_chain_obj) {
                        Py_DECREF(inside);
                        Py_DECREF(sorted);
                        Py_DECREF(chain);
                        Py_DECREF(iter);
                        return nullptr;
                    }
                    long which_chain = PyLong_AsLong(which_chain_obj);
                    Py_DECREF(which_chain_obj);
                    if (which_chain == 0) {
                        PyObject *allele_obj = PyLong_FromLong(allele);
                        PyObject *chain_obj = PyLong_FromLong(chain_num);
                        PyObject *b_obj = PyLong_FromLong(b_counter);
                        if (PyObject_SetAttrString(node, "which_allele", allele_obj) < 0 ||
                            PyObject_SetAttrString(node, "which_chain", chain_obj) < 0 ||
                            PyObject_SetAttrString(node, "which_b", b_obj) < 0) {
                            Py_DECREF(allele_obj);
                            Py_DECREF(chain_obj);
                            Py_DECREF(b_obj);
                            Py_DECREF(inside);
                            Py_DECREF(sorted);
                            Py_DECREF(chain);
                            Py_DECREF(iter);
                            return nullptr;
                        }
                        Py_DECREF(allele_obj);
                        Py_DECREF(chain_obj);
                        Py_DECREF(b_obj);
                    }
                }
                Py_DECREF(inside);
                PyObject *source = PyObject_GetAttrString(bubble, "source");
                PyObject *sink = PyObject_GetAttrString(bubble, "sink");
                if (!source || !sink) {
                    Py_XDECREF(source);
                    Py_XDECREF(sink);
                    Py_DECREF(sorted);
                    Py_DECREF(chain);
                    Py_DECREF(iter);
                    return nullptr;
                }
                PyObject *source_chain = PyObject_GetAttrString(source, "which_chain");
                if (source_chain && PyLong_AsLong(source_chain) == 0) {
                    PyObject *chain_obj = PyLong_FromLong(chain_num);
                    PyObject_SetAttrString(source, "which_chain", chain_obj);
                    Py_DECREF(chain_obj);
                }
                Py_XDECREF(source_chain);
                PyObject *sink_chain = PyObject_GetAttrString(sink, "which_chain");
                if (sink_chain && PyLong_AsLong(sink_chain) == 0) {
                    PyObject *chain_obj = PyLong_FromLong(chain_num);
                    PyObject_SetAttrString(sink, "which_chain", chain_obj);
                    Py_DECREF(chain_obj);
                }
                Py_XDECREF(sink_chain);
                Py_DECREF(source);
                Py_DECREF(sink);
            } else {
                PyObject *list_nodes = PyObject_CallMethod(bubble, "list_bubble", nullptr);
                if (!list_nodes) {
                    Py_DECREF(sorted);
                    Py_DECREF(chain);
                    Py_DECREF(iter);
                    return nullptr;
                }
                Py_ssize_t list_len = PyList_Size(list_nodes);
                for (Py_ssize_t idx = 0; idx < list_len; ++idx) {
                    PyObject *node_id = PyList_GetItem(list_nodes, idx);
                    PyObject *node = PyDict_GetItem(self->nodes, node_id);
                    if (!node) {
                        continue;
                    }
                    PyObject *zero = PyLong_FromLong(0);
                    PyObject *minus_one = PyLong_FromLong(-1);
                    PyObject *chain_obj = PyLong_FromLong(chain_num);
                    PyObject *sb_obj = PyLong_FromLong(b_counter);
                    PyObject_SetAttrString(node, "which_b", zero);
                    PyObject_SetAttrString(node, "which_allele", minus_one);
                    PyObject_SetAttrString(node, "which_sb", sb_obj);
                    PyObject_SetAttrString(node, "which_chain", chain_obj);
                    Py_DECREF(zero);
                    Py_DECREF(minus_one);
                    Py_DECREF(chain_obj);
                    Py_DECREF(sb_obj);
                }
                Py_DECREF(list_nodes);
            }
        }
        Py_DECREF(sorted);
        Py_DECREF(chain);
    }
    Py_DECREF(iter);
    Py_RETURN_NONE;
}

static PyMethodDef Graph_methods[] = {
    {"add_chain", (PyCFunction)Graph_add_chain, METH_VARARGS, nullptr},
    {"total_seq_length", (PyCFunction)Graph_total_seq_length, METH_NOARGS, nullptr},
    {"longest_chain_bubble", (PyCFunction)Graph_longest_chain_bubble, METH_NOARGS, nullptr},
    {"longest_chain_seq", (PyCFunction)Graph_longest_chain_seq, METH_NOARGS, nullptr},
    {"nodes_in_chains", (PyCFunction)Graph_nodes_in_chains, METH_NOARGS, nullptr},
    {"seq_in_chains", (PyCFunction)Graph_seq_in_chains, METH_NOARGS, nullptr},
    {"chain_cov_node", (PyCFunction)Graph_chain_cov_node, METH_NOARGS, nullptr},
    {"chain_cov_seq", (PyCFunction)Graph_chain_cov_seq, METH_NOARGS, nullptr},
    {"num_single_bubbles", (PyCFunction)Graph_num_single_bubbles, METH_NOARGS, nullptr},
    {"reset_visited", (PyCFunction)Graph_reset_visited, METH_NOARGS, nullptr},
    {"bubble_number", (PyCFunction)Graph_bubble_number, METH_NOARGS, nullptr},
    {"remove_node", (PyCFunction)Graph_remove_node, METH_VARARGS, nullptr},
    {"remove_lonely_nodes", (PyCFunction)Graph_remove_lonely_nodes, METH_NOARGS, nullptr},
    {"compact", (PyCFunction)Graph_compact, METH_NOARGS, nullptr},
    {"write_graph", (PyCFunction)Graph_write_graph, METH_VARARGS | METH_KEYWORDS, nullptr},
    {"write_b_chains", (PyCFunction)Graph_write_b_chains, METH_VARARGS | METH_KEYWORDS, nullptr},
    {"biggest_comp", (PyCFunction)Graph_biggest_comp, METH_NOARGS, nullptr},
    {"bfs", (PyCFunction)Graph_bfs, METH_VARARGS, nullptr},
    {"fill_bubble_info", (PyCFunction)Graph_fill_bubble_info, METH_NOARGS, nullptr},
    {nullptr, nullptr, 0, nullptr}
};

static PyMemberDef Graph_members[] = {
    {"nodes", T_OBJECT_EX, offsetof(GraphObject, nodes), 0, nullptr},
    {"b_chains", T_OBJECT_EX, offsetof(GraphObject, b_chains), 0, nullptr},
    {"bubbles", T_OBJECT_EX, offsetof(GraphObject, bubbles), 0, nullptr},
    {"compacted", T_INT, offsetof(GraphObject, compacted), 0, nullptr},
    {nullptr, 0, 0, 0, nullptr}
};

static PySequenceMethods Graph_sequence = {
    Graph_length,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
};

static PyTypeObject GraphType = {
    PyVarObject_HEAD_INIT(nullptr, 0)
};

static PyModuleDef graph_module = {
    PyModuleDef_HEAD_INIT,
    "_graph_cpp",
    nullptr,
    -1,
    nullptr,
    nullptr,
    nullptr,
    nullptr,
    nullptr
};

PyMODINIT_FUNC PyInit__graph_cpp(void) {
    NodeType.tp_name = "BubbleGun._graph_cpp.Node";
    NodeType.tp_basicsize = sizeof(NodeObject);
    NodeType.tp_dealloc = (destructor)Node_dealloc;
    NodeType.tp_flags = Py_TPFLAGS_DEFAULT;
    NodeType.tp_methods = Node_methods;
    NodeType.tp_members = Node_members;
    NodeType.tp_init = (initproc)Node_init;
    NodeType.tp_new = PyType_GenericNew;

    GraphType.tp_name = "BubbleGun._graph_cpp.Graph";
    GraphType.tp_basicsize = sizeof(GraphObject);
    GraphType.tp_dealloc = (destructor)Graph_dealloc;
    GraphType.tp_flags = Py_TPFLAGS_DEFAULT;
    GraphType.tp_methods = Graph_methods;
    GraphType.tp_members = Graph_members;
    GraphType.tp_init = (initproc)Graph_init;
    GraphType.tp_new = PyType_GenericNew;
    GraphType.tp_str = Graph_str;
    GraphType.tp_repr = Graph_str;
    GraphType.tp_as_sequence = &Graph_sequence;

    if (PyType_Ready(&NodeType) < 0) {
        return nullptr;
    }
    if (PyType_Ready(&GraphType) < 0) {
        return nullptr;
    }
    PyObject *module = PyModule_Create(&graph_module);
    if (!module) {
        return nullptr;
    }
    Py_INCREF(&NodeType);
    Py_INCREF(&GraphType);
    PyModule_AddObject(module, "Node", (PyObject *)&NodeType);
    PyModule_AddObject(module, "Graph", (PyObject *)&GraphType);
    return module;
}
