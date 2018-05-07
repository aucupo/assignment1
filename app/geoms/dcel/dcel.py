"""
A Doubly-Connected Edge List (DCEL) is a data structure originally designed to (1) planar subdivisions.
We will also use it for two more tasks:
(2) representation of geometries in 2-space, and (3) representation of geometries in 3-space.

A DCEL consists of interconnected faces, edges, and vertices.
    - A Vertex has a reference to Point object that define the location of the vertex in the space and a reference to
      any (arbitrary) of the outgoing edges.
    - An Edge consists of two half-edges oriented in opposite directions. So, it consists of a target vertex that the
      first half edge reaches, a reference to the face the first half-edge is adjacent to, a reference to the next
      edge on the face, a reference to the previous edge on the face, and a reference to the twin half-edge, i.e.,
      the half edge going in the opposite direction.
    - A Face consists of a list of (references to) isolated vertices and a list of (references to) adjacent edges.
      Isolated vertices are vertices that lie in the face and are not connected to any edge (used to represent points).
      The list of adjacent edges contains an edge for each edge-chain adjacent to the face (because, given an edge
      we can reconstruct the whole chain).
      Edge-chains can be
        - Open: only possible when the DCEL is used to represent a linear geometry.
        - Closed: if ordered CCW, denote the boundary of a face; otherwise, denote the boundary of a hole in the face
                  NOTE that in 3-space we would need an observation point to decide the orientation of a closed chain,
                  however, the only cases in which we have closed chains in 3-space is when we are representing either
                  a polygon or a polyhedron. When representing a polyhedron each face will be adjacent to another face
                  of the polyhedron and they will be constructed with the right orientation.
                  When representing a polygon in 3-space adopt the strategy or representing both sides of the polygon,
                  so twin of the edges representing the boundary of the polygon will be adjacent to a face that
                  represent the "back side" of another face of the polygon.
                  This means that the only case when we are interested in deciding the orientation of a closed chain
                  is when the DCEL is used to represent a planar subdivision. In this case we can safely assume the
                  observation point to be anywhere in the positive-z halfspace. Say, Point3(0,0,1).
        (NOTE: we only admit convex shapes).
      So, basically, the list of adjacent edges contains either of the following
        - n edges, each denoting an arbitrary edge of an open chain
        - n edges, each denoting an arbitrary edge of a CW closed chain
        - 1 edge denoting an arbitrary edge of a CCW closed chain

Given the interconnected nature of Vertex, Edge, and Face classes:
- a DCEL simply consists of one Face (from which all other faces, edges and vertices can be retrieved by traversing the
  connected structure)

NOTE: when using the DCEL to represent geometries it is important to determine when a face has only CW closed chains.
In this case, the face represent the empty space, so it must not be rendered.
"""

#from app.geoms.utils.basepoint import *


def _is_chain_open(edge_chain):
    return edge_chain[0].prev_edge is None


def _is_chain_closed(edge_chain):
    return not _is_chain_open(edge_chain)


class Vertex(object):
    def __init__(self, point):

        # print("Creating Vertex from point: " + str(point))

        # self.point = None
        from app.geoms.point import Point3
        if isinstance(point, Point3):
            self.point = point
        else:
            raise Exception("Vertex creation requires a Point3 object (or any derived class). "
                            "Given an  object of type: " + str(type(point)))

        self.outgoing_edge = None  # this stores an arbitrary outgoing edge
        # all others edges (both incoming and outgoing) can be computed from it

        # self._out_edges = list()

    def change_outgoing_edge(self):
        """tries to change the outgoing_edge with another one, if possible, otherwise set it to None"""
        old_out_edge = self.outgoing_edge

        if old_out_edge:
            out_edges = self.get_outgoing_edges()

            self.outgoing_edge = None

            for out_edge in out_edges:
                if out_edge != old_out_edge:
                    self.outgoing_edge = out_edge
                    break

    def get_outgoing_edges(self):
        """Traverses the part of the dcel structure connected to this vertex
        to build and return a list of of outgoing edges, ordered counterclockwise."""

        current_out_edge = self.outgoing_edge
        out_edges = []
        visited_edges = set()
        while current_out_edge and current_out_edge not in visited_edges:
            out_edges.append(current_out_edge)
            visited_edges.add(current_out_edge)

            current_in_edge = current_out_edge.getTwin()
            if current_in_edge:
                current_out_edge = current_in_edge.getNext()
            else:  # inconsistency
                raise Exception("Error while computing outgoing edges for vertex " + str(self) + ". " +
                                "\nMalformed DCEL: edge " + str(current_out_edge) + " has no twin!")
        return out_edges

    def get_incoming_edges(self):
        """Traverses the part of the dcel structure connected to this vertex
        to build and return a list of of ingoing edges, ordered counterclockwise."""

        current_out_edge = self.outgoing_edge
        current_in_edge = current_out_edge.getTwin()
        if not current_in_edge:  # inconsistency
            raise Exception("Error while computing outgoing edges for vertex " + str(self) + ". " +
                            "\nMalformed DCEL: edge " + str(current_out_edge) + " has no twin!")
        in_edges = []
        visited_edges = set()
        while current_in_edge and current_in_edge not in visited_edges:
            in_edges.append(current_in_edge)
            visited_edges.add(current_in_edge)

            current_out_edge = current_in_edge.getNext()
            current_in_edge = current_out_edge.getTwin()
            if not current_in_edge:  # inconsistency
                raise Exception("Error while computing outgoing edges for vertex " + str(self) + ". " +
                                "\nMalformed DCEL: edge " + str(current_in_edge) + " has no twin!")
        return in_edges

    def __hash__(self):
        """Allows for using a Vertex as a key of a set or a dictionary."""
        return hash(id(self))

    def __eq__(self, other):
        return self.point == other.point

    def __str__(self):
        return "Vertex" + repr(self.point)


class Edge(object):
    def __init__(self,
                 target_vertex=None,
                 adjacent_face=None,
                 twin_edge=None, prev_edge=None, next_edge=None):

        self.target_vertex = target_vertex if isinstance(target_vertex, Vertex) else None
        self.adjacent_face = adjacent_face if isinstance(adjacent_face, Face) else None

        self.twin_edge = twin_edge if isinstance(twin_edge, Edge) else None
        self.prev_edge = prev_edge if isinstance(prev_edge, Edge) else None
        self.next_edge = next_edge if isinstance(next_edge, Edge) else None

    def is_complete(self):
        return self.target_vertex is not None and \
               self.adjacent_face is not None and \
               self.twin_edge is not None and \
               self.prev_edge is not None and \
               self.next_edge is not None

    def source_vertex(self):
        if not self.twin_edge:
            raise Exception("Error while computing source vertex for edge (obj_id " + str(id(self)) + ")." +
                            "\nMalformed DCEL: edge has no twin!" + " TARGET VERTEX:" + str(self.target_vertex))

        return self.twin_edge.target_vertex

    def get_chain(self):
        """
        :return: the chain of edges this edge belongs to
        """
        chain = list()
        visited = set()
        current_edge = self
        # assume the chain is closed, so we simply keep going forward until we get back to this edge
        closed = True
        while current_edge and current_edge not in visited:
            chain.append(current_edge)
            visited.add(current_edge)
            current_edge = current_edge.next_edge
            if not current_edge:
                closed = False

        # if the chain is not closed we need to check if there are other edges before this one
        if not closed:
            prev_chain = list()
            visited = set()
            current_edge = self.prev_edge
            while current_edge and current_edge not in visited:
                prev_chain.append(current_edge)
                visited.add(current_edge)
                current_edge = current_edge.prev_edge

            if len(prev_chain) > 0:
                chain = prev_chain.reverse() + chain

        return chain

    def __hash__(self):
        """Allows for using an Edge as a key of a set or a dictionary."""
        return hash(id(self))

    def __eq__(self, other):
        return self.source_vertex() == other.source_vertex() and self.target_vertex == other.target_vertex

    def __repr__(self):
        return "[" + str(self.source_vertex()) + " --> " + str(self.target_vertex) + "]"

    def __str__(self):
        return "Edge" + repr(self) + " - Incident Face: " + str(id(self.adjacent_face)) \
               + " - Twin: " + repr(self.twin_edge)


class Face(object):
    def __init__(self, adjacent_edges=None, isolated_vertices=None):

        # set the adjacent_edges or raise an error
        if isinstance(adjacent_edges, Edge):
            self.adjacent_edges = [adjacent_edges]
        elif isinstance(adjacent_edges, list) and all(isinstance(e, Edge) for e in adjacent_edges):
            self.adjacent_edges = adjacent_edges
        elif adjacent_edges is None:
            self.adjacent_edges = list()
        else:
            raise TypeError("Face.__init__ requires an Edge object or a list of Edge objects as input parameter")

        # set the isolated_vertices or raise an error
        if isinstance(isolated_vertices, Vertex):
            self.isolated_vertices = [isolated_vertices]
        elif isinstance(isolated_vertices, list) and all(isinstance(v, Vertex) for v in isolated_vertices):
            self.isolated_vertices = isolated_vertices
        elif isolated_vertices is None:
            self.isolated_vertices = list()
        else:
            raise TypeError("Face.__init__ requires a Vertex object or a list of Vertex objects as input parameter")

        # TODO: mi servono? se si, meglio spostarle in DCEL?
        # # let us also define two handy lists
        # # these lists turn helpful when using the DCEL to represent geometries
        # self.open_chains = list()
        # self.closed_chains = list()
        # for e in self.adjacent_edges:
        #     chain = e.get_chain()
        #     if _is_chain_closed(chain):
        #         self.closed_chains.append(e)
        #     else:
        #         self.open_chains.append(e)

    def get_adjacent_faces(self):
        adjacent_faces = set()
        for ae in self.adjacent_edges:
            edge_chain = ae.get_chain()
            # print(str(edge_chain))
            for e in edge_chain:
                adjacent_faces.add(e.twin_edge.adjacent_face)

        return list(adjacent_faces)

    def __hash__(self):
        """Allows for using a Face as a key of a set or a dictionary."""
        return hash(id(self))

    def __str__(self):
        ret_str = self.__class__.__name__ + " (obj_id: " + str(id(self)) + ") {"

        for i, e in enumerate(self.adjacent_edges):
            chain = e.get_chain()
            ret_str += "\n\tedge chain " + str(i) + ":\n\t\t" + "\n\t\t".join([str(c) for c in chain])

        for i, v in enumerate(self.isolated_vertices):
            ret_str += "\n\tisolated vertex " + str(i) + ": " + str(v.point)

        ret_str += "\n}"

        return ret_str


class DCEL(object):
    def __init__(self):
        self.exterior_face = Face()  # initially only one face representing the whole plane

        # TODO: edges and renderable_vertex_array are not needed?
        self.edges = list()  # list of edges of this DCEL
        self.vertices = list()  # list of renderable_vertex_array of this DCEL

    def reset(self):
        del self.exterior_face
        self.exterior_face = Face()

    def make_from_points(self, *points):
        # for each point, simply add a Vertex (corresponding to point) to the exterior_face

        self.reset()  # first reset the DCEL

        for p in points:
            self.exterior_face.isolated_vertices.append(Vertex(p))

    def make_from_line(self, line):
        # line is a linear entity consisting of a list of renderable_vertex_array

        # print("Making DCEL for line with " + str(len(line.vertices)) + " vertices")
        self.reset()  # first reset the DCEL

        if len(line.vertices) < 2:
            self.make_from_points(line.vertices)
        else:
            last_e = None
            last_t_e = None
            source_vertex = Vertex(line.vertices[0])

            for i in range(1, len(line.vertices)):

                target_vertex = Vertex(line.vertices[i])

                e = Edge(target_vertex, self.exterior_face)  # edge
                t_e = Edge(source_vertex, self.exterior_face)  # twin edge

                # set the references for the edge
                e.twin_edge = t_e
                if last_e:
                    e.prev_edge = last_e
                    last_e.next_edge = e

                # set the references for the twin edge
                t_e.twin_edge = e
                if last_t_e:
                    t_e.next_edge = last_t_e
                    last_t_e.prev_edge = t_e

                # if this is the first edge being generated append it to the face
                if i == 1:
                    self.exterior_face.adjacent_edges.append(e)

                source_vertex = target_vertex
                last_e, last_t_e = e, t_e

    def make_from_polygon(self, polygon):

        # REMEMBER:
        #  1. polygons are represented by a set of triangular faces
        #  2. polygons have faces for both sides of the polygon (front and back)
        #  3. we treat only convex polygons without holes,
        #     so can be trivially triangulated connecting the first vertex to all others

        self.reset()  # first reset the DCEL

        if len(polygon) > 2:
            v0, v1 = Vertex(polygon.boundary[0]), Vertex(polygon.boundary[1])
            last_e2 = None
            last_t_e2 = None

            first, last = 2, len(polygon)
            for i in range(first, last):

                v2 = Vertex(polygon.boundary[i])
                # print("CONSIDERING VERTICES: v0: " + str(v0) + " v1: " + str(v1) + " v2: " + str(v2))

                # -------------------------------
                # first do the front face

                # decide if the front face is the exterior face or a new one
                front_face = self.exterior_face if i == first else Face()

                # create the edges
                e0 = Edge(v1, front_face)
                e1 = Edge(v2, front_face)
                e2 = Edge(v0, front_face)

                # append one of these edges to the face
                front_face.adjacent_edges.append(e0)

                # set prev and next edges for each edge
                e0.prev_edge = e2
                e0.next_edge = e1

                e1.prev_edge = e0
                e1.next_edge = e2

                e2.prev_edge = e1
                e2.next_edge = e0

                # -------------------------------
                # do the back face

                # the back face is always a new face
                back_face = Face()

                # create the twin edges
                t_e0 = Edge(v0, back_face)
                t_e1 = Edge(v1, back_face)
                t_e2 = Edge(v2, back_face)

                # append one of these edges to the face
                back_face.adjacent_edges.append(t_e0)

                # set the prev and next edges for each twin_edge
                t_e0.prev_edge = t_e1
                t_e0.next_edge = t_e2

                t_e1.prev_edge = t_e2
                t_e1.next_edge = t_e0

                t_e2.prev_edge = t_e0
                t_e2.next_edge = t_e1

                # -------------------------------
                # now set the twin references

                if i == first:
                    # if this is the first triangle e0 is an external edge, so its twin is t_e0
                    e0.twin_edge = t_e0
                    t_e0.twin_edge = e0
                else:
                    # otherwise the twin of e0 is the last_e2 (which, by now, must be set)
                    e0.twin_edge = last_e2
                    last_e2.twin_edge = e0
                    # and the twin of t_e0 is the last_t_e2 (which, by now, must be set)
                    t_e0.twin_edge = last_t_e2
                    last_t_e2.twin_edge = t_e0

                # for each triangle, e1 is always an external edge, so its twin is t_e1
                e1.twin_edge = t_e1
                t_e1.twin_edge = e1

                if i == last-1:
                    # if this is the last triangle e2 is an external edge, so its twin is t_e2
                    e2.twin_edge = t_e2
                    t_e2.twin_edge = e2
                else:
                    # otherwise, the twin of e2 does not exists yet (will be e0 in the next triangle)
                    # it will be set when processing the next triangle
                    pass

                # -------------------------------
                # finally, advance the references
                v1 = v2
                last_e2 = e2
                last_t_e2 = t_e2

        #TODO: settare l'outgoing_edge per i vertici + evitare di creare lo stesso vertice piu volte

    def make_from_solid(self, solid):
        """
        a solid Must have a vertex array and an element array.
        The DCEL is generated straightworwardly from those.
        REMEMBER: by design the element array defines triplets of vertices (triangles)
        :param solid: a Solid object
        :return: fills the DCEL
        """

        from app.geoms.point import Point3

        self.reset()  # first reset the DCEL

        vertices = solid.renderable_vertex_array['coords'].tolist()
        elements = solid.renderable_element_array.tolist()

        # prepare a new list of triplets with each triplet denoting a triangular face
        faces_elements = [tuple(elements[i:i+3]) for i in range(0, len(elements), 3)]

        # In the following structure we keep a reference to incomplete hedges.
        # Namely, these hedges will only have a reference to the twin hedge and to the target vertex
        # An edge will be removed from here when all its references are set.
        # Namely, also the references next_edge, prev_edge, and adjacent_face
        incomplete_edges_by_source_and_target = dict()  # key, value = (source element id, target element id), edge

        # In here we store the Vertex objects we created,
        # in order not to create several Vertex objects for the same point
        created_vertices_by_element = dict()  # key, value = element, Vertex

        first_face = True
        # until there are element faces to be analyzed
        while faces_elements:
            # pop an element_face to be analyzed
            face_elements = faces_elements.pop(0)
            # print("\n\n------------------\n\nanalyzing face: " + str(face_elements))

            # we are analyzing a new face, so create a new Face object, unless this is the first face
            # being analyzed, in which case, take the exterior face of the DCEL
            face = self.exterior_face if first_face else Face()
            first_face = False
            # print("Face id: " + str(id(face)))

            # we assumed that we only deal with triangular faces, so each face will have exactly 3 edges
            # we put them in a list
            edges = list()

            # construct three edges (e0, e1, e2) for this face such that e0 = (v0, v1), e1 = (v1, v2), e2 = (v2, v0)
            # or retrieve the corresponding partially constructed edges (if they exist)
            for i, element in enumerate(face_elements):
                source_element, target_element = element, face_elements[(i+1) % len(face_elements)]
                # print("\n\nanalyzing edge: " + str((source_element, target_element)))
                # print("list of incomplete Edge: " + str(incomplete_edges_by_source_and_target))
                # print("list of generated Vertex: " + str(created_vertices_by_element))

                # if this edge was previously generated as the twin of an edge of another face, get it from
                # the list of incomplete edges
                edge = incomplete_edges_by_source_and_target.pop((source_element, target_element), None)

                # create the Vertex objects (source and target) of this edge or retrieve them if they already exist
                target_vertex = created_vertices_by_element.get(target_element,
                                                                Vertex(Point3(*vertices[target_element])))

                source_vertex = created_vertices_by_element.get(source_element,
                                                                Vertex(Point3(*vertices[source_element])))

                # if the edge we looked for exists, get its
                # - target Vertex
                # - source Vertex and
                # - twin_edge Edge
                if isinstance(edge, Edge):
                    # get the twin of this edge
                    twin_edge = edge.twin_edge
                else:
                    # prepare two new Edge objects for the edge and its twin
                    edge, twin_edge = Edge(), Edge()

                # complete the vertex by setting (or overwriting) the outgoing_edge
                target_vertex.outgoing_edge = twin_edge
                source_vertex.outgoing_edge = edge

                # put the vertices in the created_vertices dictionary
                # (or overwrite them if they were already in)
                created_vertices_by_element[target_element] = target_vertex
                created_vertices_by_element[source_element] = source_vertex

                # set the face of this edge
                edge.adjacent_face = face

                # set the target vertices
                edge.target_vertex = target_vertex
                twin_edge.target_vertex = source_vertex

                # link the twins
                edge.twin_edge = twin_edge
                twin_edge.twin_edge = edge

                # if the twin is not yet completed (which would be the case if it was generated as an edge of
                # a face analyzed previously) it will not be completed during the analysis of this face,
                # so place it in the incomplete_edges list
                if not twin_edge.is_complete():
                    incomplete_edges_by_source_and_target[(target_element, source_element)] = twin_edge

                # complete the edge
                if i > 0:
                    edge.prev_edge = edges[i-1]
                    edges[i-1].next_edge = edge

                # put the edge in the edges list of this face
                edges.append(edge)

            # the last and first edges are not yet linked to each other, link them
            edges[0].prev_edge = edges[-1]
            edges[-1].next_edge = edges[0]

            # finally, assign one of the edges of this face to the Face object
            face.adjacent_edges.append(edges[0])


        # print("make_dcel_from_solid FINISHED. The generated dcel is \n" )
        # print(str(self))


    def __str__(self):
        ret_str = "\n------------------------------------\n"
        ret_str += "DCEL (obj_id " + str(id(self)) + ")<\n"

        visited_faces = set()

        faces_to_visit = set()
        faces_to_visit.add(self.exterior_face)

        while len(faces_to_visit) > 0:
            face = faces_to_visit.pop()
            if face not in visited_faces:
                adj_faces = face.get_adjacent_faces()
                faces_to_visit.update(adj_faces)

                ret_str += str(face) + "\n"

                visited_faces.add(face)

        ret_str += ">"
        ret_str += "\n------------------------------------\n"

        return ret_str

    def get_renderable_arrays(self):
        """
        traverse the DCEL structure and return a list of vertices and a list of elements for the rendering of the DCEL
        :return: vertices: a list of verices [a, b, c, ...],
        elements: a list of indices [idx_1, idx_2, idx_3, ...] from the list vertices.
         if the DCEL represents a set of point, each index refers a point to be rendered
         if the DCEL represents a linear entity, each pair of indices forms a segment to be rendered
         if the DCEL represents a polygon or a polyhedron, each triplet of indices form a face to be rendered
        """

        from app.geoms.point import Point3
        vertices = list()
        elements = list()
        outline_elements = list()

        if self.exterior_face.isolated_vertices:
            # if there are isolated vertices it means this DCEL represents a set of points (and nothing more)
            for v in self.exterior_face.isolated_vertices:
                elements.append(len(vertices))
                vertices.append(v)
        else:
            # otherwise we are treating either a linear geometry, a polygon, or a polyhedron
            visited_faces = set()

            faces_to_visit = set()
            faces_to_visit.add(self.exterior_face)

            while faces_to_visit:
                face = faces_to_visit.pop()
                if face not in visited_faces:

                    for ae in face.adjacent_edges:
                        edge_chain = ae.get_chain()

                        # if the first edge in the chain has no prev_edge the chain is open
                        open_chain = True if _is_chain_open(edge_chain) else False

                        v1_idx = None
                        first_edge, last_edge = 0, len(edge_chain)-1
                        # for i, edge in enumerate(reversed(edge_chain)):
                        #     # NOTE: OpenGL requires vertices of faces to be given in CW order, but our polygons
                        #     # have been constructed specifying vertices in CCW order, so we need to traverse
                        #     # the edge_chain in reverse order to create CW ordered vertices and elements
                        for i, edge in enumerate(edge_chain):
                            if edge.twin_edge.adjacent_face not in visited_faces and \
                                            edge.twin_edge.adjacent_face is not face:
                                faces_to_visit.add(edge.twin_edge.adjacent_face)

                            if i == first_edge:
                                v1 = edge.source_vertex()
                                if v1 in vertices:
                                    v1_idx = vertices.index(v1)
                                else:
                                    v1_idx = len(vertices)
                                    vertices.append(v1)

                            v2 = edge.target_vertex
                            if v2 in vertices:
                                v2_idx = vertices.index(v2)
                            else:
                                v2_idx = len(vertices)
                                vertices.append(v2)

                            if open_chain:
                                # if we are treating an open chain it means we are treating a linear entity
                                # so the elements must be given pair-wise. Each pair denotes the start and the
                                # end of the i-th segment making the linear entity
                                elements.extend([v1_idx, v2_idx])
                            else:
                                # otherwise we are treating a face. Faces can be only triangles (we assumed this before)
                                if i == first_edge:
                                    elements.append(v1_idx)

                                # the last vertex of the last edge is the first vertex of the first edge,
                                # so it was already treated
                                if i != last_edge:
                                    elements.append(v2_idx)

                                # treat the outline
                                # take the neighbor face (adjacent to the twin of this edge)
                                # access vertex opposite to the twin (REMEMBER: each face is a triangle)
                                # check if such a vertex is COPLANAR with

                                # get the face adjacent to this face through this edge
                                neighbor_face = edge.twin_edge.adjacent_face

                                # we proceed only if the neighbor face has been visited already
                                # in this way we avoid to add more than once the same part of the outline
                                if neighbor_face in visited_faces:
                                    # get the vertex opposite to this edge in the
                                    # face adjacent to this face through the current edge
                                    other_face_vertex = edge.twin_edge.next_edge.target_vertex

                                    # get the three vertices defining the face the current edge belongs to
                                    v3 = edge_chain[(i+1) % len(edge_chain)].target_vertex

                                    if not Point3.are_coplanar(v1.point, v2.point,
                                                                   v3.point, other_face_vertex.point):
                                        outline_elements.extend([v1_idx, v2_idx])

                            v1, v1_idx = v2, v2_idx  # advance the first vertex

                    visited_faces.add(face)

        return vertices, elements, outline_elements

# ps = [Point3(2, 1), Point3(7, 1), Point3(9, 5), Point3(7, 9), Point3(2, 9), Point3(0, 5)]
#
# dc = DCEL()
# dc.make_from_points(*ps)
#
# print(str(dc))
#
# renderable_vertex_array, renderable_element_array = dc.get_renderable_arrays()
# for v in renderable_vertex_array:
#     print(str(v))
# print(str(renderable_element_array))


# from app.geoms.polygon import *

# p = Polyline([Point3(2, 1), Point3(7, 1), Point3(9, 5), Point3(7, 9), Point3(2, 9), Point3(0, 5)])
#
# dc = DCEL()
# dc.make_from_line(p)
# #
# # print(str(dc))
# #
# renderable_vertex_array, renderable_element_array = dc.get_renderable_arrays()
# for v in renderable_vertex_array:
#     print(str(v))
# print(str(renderable_element_array))


# from app.geoms.polygon import *
# p = Polygon([Point3(2, 1), Point3(7, 1), Point3(9, 5), Point3(7, 9), Point3(2, 9), Point3(0, 5)])
#
# dc = DCEL()
# dc.make_from_polygon(p)
#
# # print(str(dc))
#
# renderable_vertex_array, renderable_element_array = dc.get_renderable_arrays()
# for v in renderable_vertex_array:
#     print(str(v))
# print(str(renderable_element_array))
