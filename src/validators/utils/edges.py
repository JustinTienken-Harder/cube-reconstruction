class EdgeValidate:
    """This class is used to validate the edges of a cube string:
    """
    FACES = "UFRDLB" # Standard cube faces
    EDGES = ["UR", "UF", "UL", "UB", "FR", "FL", "DR", "DF", "DL", "DB", "BR", "BL"]
    @staticmethod
    def get_valid_edges(state_string):
        centers = state_string[4:54:9]
        center_map = {letter: i for i, letter in enumerate(EdgeValidate.FACES)}
        center_index = {x: [center_map[letter] for letter in x] for x in EdgeValidate.EDGES}
        # Get the possible edges from the centers of the cube string
        edges = [[centers[i] for i in center_index[x]] for x in EdgeValidate.EDGES]
        return edges
    
    @staticmethod
    def get_edges(state_string):
        """
        This method extracts the corner pieces from the cube string.
        It returns a dictionary of location and the corner piece.
        """
        u = "U"
        r = "R"
        f = "F"
        d = "D"
        l = "L"
        b = "B"
        # Multiplier for each face
        multiplier = {letter: i for i, letter in enumerate(EdgeValidate.FACES)}
        # Solver for the location + face to a single number (exact location in string)
        def s(location, face):
            return location + multiplier[face]*9
        # Requires the edges to be listed in clockwise order. This allows for easy orientation check and permutation checks.
        edge_index = {
            'UR': [s(5, u), s(1, r)],
            'UF': [s(7, u), s(1, f)],
            'UL': [s(3, u), s(1, l)],
            'UB': [s(1, u), s(1, b)],
            "FR": [s(5, f), s(3, r)],
            "FL": [s(3, f), s(5, l)],
            "BR": [s(3, b), s(5, r)],
            "BL": [s(5, b), s(3, l)],
            "DR": [s(5, d), s(7, r)],
            "DF": [s(1, d), s(7, f)],
            "DL": [s(3, d), s(7, l)],
            "DB": [s(7, d), s(7, b)],
        }
        # Get the actual edges from the cube string
        edges = {x: "".join([state_string[i] for i in index_list]) for x, index_list in edge_index.items()}
        return edges