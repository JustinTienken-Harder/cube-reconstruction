from validators.symmetries import Symmetries


class CornerValidate:
    """
    This class is used to validate the corner pieces of the cube string:

    The weirdness of the code is due to checking relitive to arbitrary coloring schemes
    """
    FACES = "URFDLB"
    CORNERS = ['URF', 'UFL', 'ULB', 'UBR', 'DFR', 'DLF', 'DBL', 'DRB']
    @staticmethod
    def get_valid_corners(self, state_string):
        """This method extracts the valid corner pieces from the cube string. 
        Compares this to the corners in the string"""
        centers = state_string[4:54:9]
        center_map = {letter: i for i, letter in enumerate(CornerValidate.FACES)}
        center_index = {x: [center_map[letter] for letter in x] for x in CornerValidate.CORNERS}
        # Get the possible corners from the centers of the cube string
        corners = [[centers[i] for i in center_index[x]] for x in CornerValidate.CORNERS]
        return corners


    @staticmethod
    def get_corners(state_string):
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
        multiplier = {letter: i for i, letter in enumerate(CornerValidate.FACES)}
        # Solver for the location + face to a single number (exact location in string)
        def s(location, face):
            return location + multiplier[face]*9
        # Requires the corners to be listed in clockwise order. This allows for easy orientation check and permutation checks.
        corner_index = {
            'URF': [s(8, u), s(0, r), s(2, f)],
            'UFL': [s(6, u), s(0, f), s(2, l)],
            'ULB': [s(0, u), s(0, l), s(2, b)],
            'UBR': [s(2, u), s(0, b), s(2, r)],
            'DFR': [s(2, d), s(8, r), s(6, f)],
            'DLF': [s(0, d), s(8, l), s(6, f)],
            'DBL': [s(6, d), s(8, b), s(6, l)],
            'DRB': [s(8, d), s(8, r), s(6, b)],
        }
        # Get the actual corners from the cube string
        corners = {x: "".join([state_string[i] for i in index_list]) for x, index_list in corner_index.items()}
        return corners

    @staticmethod
    def corner_orientation(corners, state_string):
        """
        This method checks the orientation of the corners.
        It returns a dictionary of location and it's orientation
        """
        centers = state_string[4:54:9]
        top, bottom = centers[0], centers[3]
        corners = corners.copy()
        #Could do this as a dictionary comprehension, but invalid corners will fail. 
        orientations = {}
        for location, corner in corners.items():
            if top in corner:
                orientations[location] = None if corner.count(top) > 1 else corner.index(top)
            elif bottom in corner:
                orientations[location] = None if corner.count(bottom) > 1 else corner.index(bottom)
            else:
                orientations[location] = None
        return orientations
    
    def corner_permutation(self, corners):
        """
        This method checks the permutation of the corners.
        It returns a dictionary of location and it's orientation
        """
        valid_location_to_corner_color = self.get_valid_corners(corners)
        if len(valid_location_to_corner_color) != len(valid_location_to_corner_color.values()):
            #we need to utilize absolute locations
            #Because some of the corners are invalid
            use_absolute = True
            valid_corner_color_to_location = {}
            #build it best we can:
            for x, y in valid_location_to_corner_color.items():
                if x in valid_corner_color_to_location:
                    pass
                else: 
                    valid_corner_color_to_location[y] = x
        else:
            valid_corner_color_to_location = {y:x for x, y in enumerate(valid_location_to_corner_color)}
        centers = corners[4:54:9]
        def orient_corners(corners):
            orienations = CornerValidate.corner_orientation(corners, centers)
            corners = corners.copy()
            for location, orientation in orienations.items():
                if orientation is not None:
                    if orientation == 0:
                        corners[location] = corners[location]
                    elif orientation == 1: #counterclockwise twist cubie
                       corners[location] = corners[location][1:] + corners[location][0]
                    elif orientation == 2: #clockwise twist cubie
                        corners[location] = corners[location][-1] + corners[location][:-1]
                    else:
                        raise ValueError("Invalid orientation")
                else:
                    corners[location] = corners[location]
            return corners 
        location_to_oriented_corner = orient_corners(corners)
        permutation = {}
        for location, corner in location_to_oriented_corner.items():
            if use_absolute: #must use absolute locations to define the permutation
                if corner in None:
                    pass
                else:
                    pass
            else:
                if corner in valid_corner_color_to_location:
                    permutation[corner] = location_to_oriented_corner[valid_corner_color_to_location[corner]]    
                else:
                    permutation[corner] = location_to_oriented_corner[location]        
        return permutation

    @staticmethod
    def corner_permutation_parity(corner_permutation):
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

    
    def get_total_orientation(self, corners, state_string):
        """
        This method checks the orientation of the corners.
        It returns a dictionary of location and it's orientation
        """
        orientations = self.corner_orientation(corners, state_string)
        sum = 0
        for orientation in orientations.values():
            if orientation is None:
                return 10
            else:
                sum += orientation
        return sum % 3
    
    def get_cubie_parity():
        pass

class CornerSingleLoss:
    def corner_orientation_loss(self, string):
        corners = CornerValidate.get_corners(string)
        orientations = CornerValidate.corner_orientation(corners, string)


class CornerPairLoss:
    def corner_loss(self, s1, s2):
        c1 = CornerValidate.get_corners(s1)
        c2 = CornerValidate.get_corners(s2)
        o1 = CornerValidate.corner_orientation(c1, s1)
        o2 = CornerValidate.corner_orientation(c2, s2)
        sum = 0
        for location, orientation in o1.items():
            if o2[location] != orientation:
                sum += 1
        return sum 
    
    def corner_orientation_single_loss(self, s1):
        pass


        
            


    def corner_permutation(self, s):
        pass

class ValidateState:
    """
    This class is used to validate the state of the cube string:
    """

    def corner_orientation(self, s):
        pass