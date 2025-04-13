# General Symmetries of the cube. 
# This module helps find simple symmetries to incorporate as hard-coded rules.
from validators.string_tools import StringManipulate

class Symmetries:
    """Holds base rotational symmetries of the cube.
    Starting from UF, these strings define alternative orientations of the cube.
    There are 24 orientations of the cube, so RF corresponds to U side becoming R and F side staying the same.
    The values correspond to rotations of the cube from UF standard to the other orientations.
    Rotations will be remapped to side recolors. Allows for rotating a scrambled cube to check for equivalence.
    """
    ORIENTATIONS = {
        'UR':'y',
        'UF':"",
        'UL':"y'",
        'UB':"y2",
        'RU':"x' z'",
        'RF':"z'",
        'RD':"x z'",
        'RB':"z' y2",
        'FU':"y z2",
        'FR':"x y",
        'FD':"x",
        'FL':"x y'",
        'DR':"x2 y",
        'DF':"z2",
        'DL':"x2 y'",
        'DB':"x2",
        'LU':"x' z",
        'LF':"z",
        'LD':"x z",
        'LB':"x2 z",
        'BU':"x'",
        'BR':"x' y",
        'BD':"x' y2",
        'BL':"x' y'",
    }
    BASE_ROTATIONS = ["x", "y", "z"]
    SINGLE_ROTATIONS = BASE_ROTATIONS + [x+"'" for x in BASE_ROTATIONS] + [x+"2" for x in BASE_ROTATIONS]
    ORIENTATION_MAPS = {'UR': {'U': 'U', 'F': 'R', 'L': 'F', 'D': 'D', 'B': 'L', 'R': 'B'}, 
                        'UF': {'U': 'U', 'R': 'R', 'F': 'F', 'D': 'D', 'L': 'L', 'B': 'B'}, 
                        'UL': {'U': 'U', 'B': 'R', 'R': 'F', 'D': 'D', 'F': 'L', 'L': 'B'}, 
                        'UB': {'U': 'U', 'L': 'R', 'B': 'F', 'D': 'D', 'R': 'L', 'F': 'B'}, 
                        'RU': {'F': 'U', 'U': 'R', 'R': 'F', 'B': 'D', 'D': 'L', 'L': 'B'}, 
                        'RF': {'L': 'U', 'U': 'R', 'F': 'F', 'R': 'D', 'D': 'L', 'B': 'B'}, 
                        'RD': {'B': 'U', 'U': 'R', 'L': 'F', 'F': 'D', 'D': 'L', 'R': 'B'}, 
                        'RB': {'R': 'U', 'U': 'R', 'B': 'F', 'L': 'D', 'D': 'L', 'F': 'B'}, 
                        'FU': {'D': 'U', 'F': 'R', 'R': 'F', 'U': 'D', 'B': 'L', 'L': 'B'}, 
                        'FR': {'R': 'U', 'F': 'R', 'U': 'F', 'L': 'D', 'B': 'L', 'D': 'B'}, 
                        'FD': {'B': 'U', 'R': 'R', 'U': 'F', 'F': 'D', 'L': 'L', 'D': 'B'}, 
                        'FL': {'L': 'U', 'B': 'R', 'U': 'F', 'R': 'D', 'F': 'L', 'D': 'B'}, 
                        'DR': {'D': 'U', 'F': 'R', 'R': 'F', 'U': 'D', 'B': 'L', 'L': 'B'}, 
                        'DF': {'D': 'U', 'L': 'R', 'F': 'F', 'U': 'D', 'R': 'L', 'B': 'B'}, 
                        'DL': {'D': 'U', 'B': 'R', 'L': 'F', 'U': 'D', 'F': 'L', 'R': 'B'}, 
                        'DB': {'D': 'U', 'R': 'R', 'B': 'F', 'U': 'D', 'L': 'L', 'F': 'B'}, 
                        'LU': {'F': 'U', 'D': 'R', 'L': 'F', 'B': 'D', 'U': 'L', 'R': 'B'}, 
                        'LF': {'R': 'U', 'D': 'R', 'F': 'F', 'L': 'D', 'U': 'L', 'B': 'B'}, 
                        'LD': {'B': 'U', 'D': 'R', 'R': 'F', 'F': 'D', 'U': 'L', 'L': 'B'}, 
                        'LB': {'L': 'U', 'D': 'R', 'B': 'F', 'R': 'D', 'U': 'L', 'F': 'B'}, 
                        'BU': {'F': 'U', 'R': 'R', 'D': 'F', 'B': 'D', 'L': 'L', 'U': 'B'}, 
                        'BR': {'L': 'U', 'F': 'R', 'D': 'F', 'R': 'D', 'B': 'L', 'U': 'B'}, 
                        'BD': {'B': 'U', 'L': 'R', 'D': 'F', 'F': 'D', 'R': 'L', 'U': 'B'}, 
                        'BL': {'R': 'U', 'B': 'R', 'D': 'F', 'L': 'D', 'F': 'L', 'U': 'B'}}
    FACES = ['U', 'R', 'F', 'D', 'L', 'B'] # Standard cube faces


    def __init__(self):
        """Initialize the Symmetries class and create rotation maps."""
        self.__make_rotation_maps()
        self.__make_orientations_map()
        self.generate_rotational_symmetries()

    def __make_rotation_maps(self):
        """Helper to convert rotations to operations on faces. Later used for string manipulations"""
        inverse = [x + "'" for x in self.BASE_ROTATIONS]
        double = [x + "2" for x in self.BASE_ROTATIONS]
        rotations = self.BASE_ROTATIONS + inverse + double
        permutation = {'x': ['U', 'B', 'D', 'F'], 'y': ['L', 'B', 'R', 'F'], 'z': ['U', 'R', 'D', 'L']}
        permutation.update({x+"'": y[::-1] for x, y in permutation.items()}) # Add inverses
        #start with identity
        self._reorient = {"I": {x: x for x in self.FACES}}
        self._reorient[""] = self._reorient["I"]
        # Do base and inverse rotations
        for rotation in rotations:
            shift = {x: x for x in self.FACES} #start with identity
            for face in self.FACES:
                if "2" in rotation:
                    if face in permutation[rotation[0]]:
                        index = permutation[rotation[0]].index(face)
                        new_face = permutation[rotation[0]][(index + 2) % 4]
                        shift[face] = new_face
                else:
                    if face in permutation[rotation]:
                        index = permutation[rotation].index(face)
                        new_face = permutation[rotation][(index + 1) % 4]
                        shift[face] = new_face
            self._reorient[rotation] = shift

    
    def __make_orientations_map(self):
        """Helper to convert orientations to rotational moves on faces. Later used for string manipulations"""
        self._orientations = {}
        for key, value in self.ORIENTATIONS.items():
            if value == "":
                self._orientations[key] = self._reorient["I"]
            else:
                self._orientations[key] = self.__get_rotation_map(value)

    @staticmethod        
    def get_rotation_effects(faces, rotation):
        """Applies a rotation map to faces of cube. Utilized to determine where U, R, F, D, L, B go.
        Args:
            rotation dict: A dictionary mapping original face positions to final face positions.
        returns FACES after rotation."""
        return [rotation[face] for face in faces]
    
    def notation_to_orientation(self, rotation_string):
        new_faces = self.__get_orientation(rotation_string)
        # shows the new UF faces, hence the result of a rotation from standard issue.
        return new_faces[0]+new_faces[2]
    
    def generate_rotational_symmetries(self):
        """
        Generates the rotational symmetries, as in equivalent rotations such as y x = z y = x z

        This reduction is made easier by converting rotations into their resulting orientations.
        There are 90 length 2 rotations, but only 24 orientations of the cube. 
        """
        #first, find one move cases
        self.equivalence_map = {x: self.notation_to_orientation(x) for x in self.SINGLE_ROTATIONS}
        # Next we produce all length 2 symmetries
        all_rotations = [f"{x} {y}" for x in self.SINGLE_ROTATIONS for y in self.SINGLE_ROTATIONS]
        for x in all_rotations:
            self.equivalence_map[x] = self.notation_to_orientation(x)
        self.equivalence_classes = {}
        for key, value in self.equivalence_map.items():
            if value not in self.equivalence_classes:
                self.equivalence_classes[value] = [key]
            else:
                self.equivalence_classes[value].append(key)
        for key in self.ORIENTATIONS.keys():
            if key not in self.equivalence_classes:
                print(f"FUCK: {key}")
        
    def get_equivalent_rotations(self, rotation_string):
        orientation = self.notation_to_orientation(rotation_string)
        return self.equivalence_classes[orientation]

    def __get_rotation_map(self, rotation_string):
        final_orientation = self.__get_orientation(rotation_string)
        return {x:y for x, y in zip(final_orientation, self.FACES)}
        
    
    def __get_orientation(self, rotation_string):
        rotations = rotation_string.split(" ")
        faces_to_permute = self.FACES.copy()
        for rotation in rotations:
            #the permutation map
            permute = self._reorient[rotation]
            faces_to_permute = [permute[face] for face in faces_to_permute]
        return faces_to_permute
    
    @staticmethod
    def get_canonical_orientation(self, state):
        s = state
        centers = s[4:54:9]
        canon = Symmetries.FACES[centers.index("U")] + Symmetries.FACES[centers.index("F")]
        return canon
    
    def get_canon_rotated_state(self, state):
        """Rotate the cube into canonical orientation preserving
        the permutation structure of the cube"""
        s = state
        canon = self.get_canonical_orientation(s)
        perm_map = self._orientations[canon]
        rotated_state = "".join(perm_map[x] for x in s)
        return rotated_state
    
    def rotate_state(self, rotation_str, state):
        orientation = self.notation_to_orientation(rotation_str)
        perm_map = self._orientations(orientation)
        rotated_state = "".join(perm_map[x] for x in state)
        return rotated_state
    
        

    

if __name__ == "__main__":
    sym = Symmetries()
    print(sym.equivalence_classes)