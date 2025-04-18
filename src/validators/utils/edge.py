class EdgeValidate:
    """This class is used to validate the edges of a cube string:
    """
    FACES = "UFRDLB" # Standard cube faces
    EDGES = ["UR", "UF", "UL", "UB", "FR", "FL", "DR", "DF", "DL", "DB", "BR", "BL"]
    @staticmethod
    def get_valid(state_string):
        centers = state_string[4:54:9]
        center_map = {letter: i for i, letter in enumerate(EdgeValidate.FACES)}
        center_index = {x: [center_map[letter] for letter in x] for x in EdgeValidate.EDGES}
        # Get the possible edges from the centers of the cube string
        edges = [[centers[i] for i in center_index[x]] for x in EdgeValidate.EDGES]
        return edges
    
    @staticmethod
    def get(state_string):
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
    
    @staticmethod
    def orientation(edges, state_string):
        centers = state_string[4:54:9]
        top, bottom, front, back = centers[0], centers[3], centers[2], centers[5]
        edges = edges.copy()
        orientations = {}
        for location, edge in edges.items():
            if top in edge:
                orientations[location] = None if edge.count(top) > 1 or bottom in edge else edge.index(top)
            elif bottom in edge:
                orientations[location] = None if edge.count(bottom) > 1 or top in edge else edge.index(bottom)
            elif front in edge:
                orientations[location] = None if edge.count(front) > 1 or back in edge else edge.index(front)
            elif back in edge:
                orientations[location] = None if edge.count(back) > 1 or front in edge else edge.index(back)
            else:
                orientations[location] = None
        return orientations
    
    @staticmethod
    def orient(edges, state_string):
        """
        This method checks the orientation of the edges.
        It returns a dictionary of location and it's orientation
        """
        orientations = EdgeValidate.orientation(edges, state_string)
        edges = edges.copy()
        for location, edge in edges.items():
            if orientations[location] is not None:
                edge = edge[orientations[location]:] + edge[:orientations[location]]
                edges[location] = edge
            else:
                edges[location] = edge
        return edges
    
    @staticmethod
    def permutation(edges, state_string):
        """
        Calculate the corner permutation by mapping where each corner currently is
        to where it should be in a solved cube.
        
        Args:
            corners: Dictionary mapping position names to corner cubies at those positions
            state_string: Full cube state string
            
        Returns:
            Dictionary describing corner permutation cycles
        """
        # Get the valid corner colors for each position
        valid_edges = EdgeValidate.get_valid(state_string)
        
        # Map position names to their respective valid corner colors
        position_to_valid_colors = {
            EdgeValidate.EDGES[i]: ''.join(sorted(valid_edges[i])) 
            for i in range(len(EdgeValidate.EDGES))
        }
        
        # Orient the corners to normalize comparisons
        oriented_edges = EdgeValidate.orient(edges, state_string)
        
        # Map each oriented corner's sorted colors to its position
        oriented_colors_to_position = {}
        for position, edge in oriented_edges.items():
            sorted_colors = ''.join(sorted(edge))
            oriented_colors_to_position[sorted_colors] = position
        
        # Build the permutation map: current position → should be position
        permutation = {}
        
        # For each corner position
        for position, edge in oriented_edges.items():
            # Sort colors for comparison
            sorted_colors = ''.join(sorted(edge))
            
            # Try to find where this corner should be
            for valid_pos, valid_colors in position_to_valid_colors.items():
                if sorted_colors == valid_colors:
                    # This corner should be at valid_pos
                    permutation[position] = valid_pos
                    break
        
        return permutation
    
    @staticmethod
    def parity(corner_permutation):
        """
        Determine the parity of a corner permutation.
        
        In a permutation, each cycle of length k requires (k-1) transpositions.
        Even-length cycles contribute odd parity, odd-length cycles contribute even parity.
        
        Returns:
            0 for even parity (valid), 1 for odd parity (invalid)
        """
        # Track visited corners to identify cycles
        visited = set()
        parity = 0
        
        # Process each corner that hasn't been visited
        for start in corner_permutation.keys():
            if start in visited:
                continue
                
            # Start a new cycle
            current = start
            cycle_length = 0
            
            # Follow the cycle until we return to the start
            while True:
                visited.add(current)
                cycle_length += 1
                
                # Move to the next corner in the cycle
                if current not in corner_permutation:
                    # Incomplete mapping - break the cycle
                    break
                    
                current = corner_permutation[current]
                
                # Check if we've completed the cycle or reached a corner not in the mapping
                if current == start or current not in corner_permutation:
                    break
            
            # Each cycle of length k contributes (k-1) to the parity count
            parity += (cycle_length - 1)
        
        # Return 0 for even parity, 1 for odd parity
        return parity % 2
    
    def get_total_orientation(self, edges, state_string):
        """
        This method checks the orientation of the corners.
        It returns a dictionary of location and it's orientation
        """
        orientations = self.orientation(edges, state_string)
        sum = 0
        for orientation in orientations.values():
            if orientation is None:
                return 10
            else:
                sum += orientation
        return sum % 3