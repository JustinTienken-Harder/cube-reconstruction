import random
import collections
try:
    import kociemba
    KOCIEMBA_AVAILABLE = True
except ImportError:
    KOCIEMBA_AVAILABLE = False
    print("Warning: 'kociemba' library not found. Solve and scramble methods will not function.")
from validators.symmetries import Symmetries
from validators.string_tools import StringManipulate



class RubiksCube(Symmetries):
    """
    Represents a Rubik's Cube and provides methods for manipulation,
    validation, solving, and scrambling using cube string notation.
    Includes methods to define moves via sequences and generate derived moves.
    """

    SOLVED_STATE = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
    FACES = ['U', 'R', 'F', 'D', 'L', 'B'] # Standard cube faces
    BASE_MOVES = list(FACES + ["M", "E", "S", "x", "y", 'z']) # Moves for which cycles are initially defined
    

    def __init__(self, state_string=SOLVED_STATE):
        """
        Initializes the cube.

        Args:
            state_string (str, optional): The initial state of the cube
                                         in 54-character cube string notation.
                                         Defaults to the solved state.

        Raises:
            ValueError: If the provided state_string is invalid.
        """
        super().__init__() # Initialize the Symmetries base class
        if not self.validate_cubestring(state_string):
            raise ValueError(f"Invalid initial cube state string provided: {state_string}")
        self.state = list(state_string) # Use list for easier manipulation

        # --- Move Definitions ---
        self._permutations = {} # Store permutation maps {from_idx: to_idx}
        self._define_base_permutations()
        self._generate_derived_moves() # Generate U', U2, R', R2 etc.

        # Example: Add whole cube rotations (optional)
        # self._add_sequence_as_move('x', "R M' L'") # M' requires middle slice implementation first
        # self._add_sequence_as_move('y', "U E' D'") # E' requires middle slice implementation first
        # self._add_sequence_as_move('z', "F S B'") # S requires middle slice implementation first

        # Update the list of all valid move notations after generation/addition
        self.valid_moves = list(self._permutations.keys())


    def _define_base_permutations(self):
        """Defines the raw permutation effect of basic 90-degree clockwise moves."""
        # Base cycles derived from the previous implementation's logic
        # Format: ([face_corners], [face_edges], [side_pieces_affected])
        base_cycles = {
            'U': ([0, 2, 8, 6], [1, 5, 7, 3], [18, 19, 20, 36, 37, 38, 45, 46, 47, 9, 10, 11]),
            'R': ([9, 11, 17, 15], [10, 14, 16, 12], [8, 5, 2, 45, 48, 51, 35, 32, 29, 26, 23, 20]), 
            'F': ([18, 20, 26, 24], [19, 23, 25, 21], [6, 7, 8, 9, 12, 15, 29, 28, 27, 44, 41, 38]),
            'D': ([27, 29, 35, 33], [28, 32, 34, 30], [24, 25, 26, 15, 16, 17, 51, 52, 53, 42, 43, 44]),
            'L': ([36, 38, 44, 42], [37, 41, 43, 39], [0, 3, 6, 18, 21, 24, 27, 30, 33, 53, 50, 47]), 
            'B': ([45, 47, 53, 51], [46, 50, 52, 48], [2, 1, 0, 36, 39, 42, 33, 34, 35, 17, 14, 11]), 
        }
        unconventional_moves = {
            'M': [1, 4, 7, 19, 22, 25, 28, 31, 34, 52, 49, 46], 
            "E": [39, 40, 41, 21, 22, 23, 12, 13, 14, 48, 49, 50],
            "S": [3, 4, 5, 10, 13, 16, 32, 31, 30, 43, 40, 37],
        }
        inverses = {x+"'": y[::-1] for x, y in unconventional_moves.items()}
        unconventional_moves.update(inverses) # Add inverses to the dictionary
        # Add identity map
        self._permutations['I'] = {i: i for i in range(54)}
        # Convert base cycles into permutation maps {from_idx: to_idx}
        for move, (corners, edges, sides) in base_cycles.items():
            perm_map = {i: i for i in range(54)} # Start with identity

            # Apply face cycles
            for cycle in [corners, edges]:
                for i in range(len(cycle)):
                    perm_map[cycle[i-1]] = cycle[i] # Map previous element's index to current element's index

            # Apply side cycles (groups of 3)
            for i in range(len(sides)):
                 perm_map[sides[i-3]] = sides[i] # Map element 3 positions back to current element

            self._permutations[move] = perm_map
        for move, slice in unconventional_moves.items():
            perm_map = {i: i for i in range(54)} #start with identity
            # apply groups of 3
            for i in range(len(slice)):
                perm_map[slice[i-3]] = slice[i]
            self._permutations[move] = perm_map

    def _apply_permutation(self, permutation_map):
        """Applies a permutation map to the current cube state."""
        initial_state = list(self.state)
        for original_index, final_index in permutation_map.items():
            # Check if index actually moved to avoid unnecessary assignments
            if initial_state[original_index] != self.state[final_index]:
                 self.state[final_index] = initial_state[original_index]

    def _compose_permutations(self, perm_map1, perm_map2):
        """Composes two permutation maps (applies perm_map1 then perm_map2)."""
        composed_map = {}
        for i in range(54):
            # Where does index i go after map1? perm_map1.get(i, i)
            # Where does THAT index go after map2? perm_map2.get(perm_map1.get(i, i), perm_map1.get(i, i))
            composed_map[i] = perm_map2.get(perm_map1.get(i, i), perm_map1.get(i, i))
        return composed_map

    def _generate_derived_moves(self):
        """
        Generates inverse (') and double (2) moves from the base clockwise moves
        and adds their permutation maps to self._permutations.
        """
        #Generate basic rotations
        x = ["R", "M'", "L'"]
        y = ["U", "E'", "D'"]
        z = ["F", "S", "B'"]
        base_rotations = {"x": x, "y": y, "z": z}

        def compose_sequential(moves_list):
            """Helper function to compose a sequence of moves as a permutation map"""
            identity = self._permutations['I']
            for count, move in enumerate(moves_list):
                if move not in self._permutations:
                    raise ValueError(f"Move '{move}' in sequence is not defined.")
                move_map = self._permutations[move]
                if count == 0:
                    perm = self._compose_permutations(identity, move_map)
                else:
                    perm = self._compose_permutations(perm, move_map)
            return perm

        for base_move in self.BASE_MOVES:
            if base_move not in self._permutations: 
                for rotation, sequence in base_rotations.items():
                    # Generate the permutation map for the rotation
                    perm_map = compose_sequential(sequence)
                    self._permutations[rotation] = perm_map


            p1 = self._permutations[base_move]       # Permutation for one 90-deg turn
            p2 = self._compose_permutations(p1, p1)  # Permutation for 180-deg turn (p1 applied twice)
            p3 = self._compose_permutations(p1, p2)  # Permutation for 270-deg turn (p1 applied three times)

            self._permutations[base_move + '2'] = p2
            self._permutations[base_move + "'"] = p3 # Inverse is 3 clockwise turns
        

    def _get_permutation_from_sequence(self, sequence_string):
        """
        Calculates the net permutation map resulting from applying a
        sequence of known moves to a solved state.

        Args:
            sequence_string (str): A space-separated string of moves already
                                   defined in self._permutations.

        Returns:
            dict: The net permutation map {from_idx: to_idx}.

        Raises:
            ValueError: If any move in the sequence is not defined.
        """
        moves = sequence_string.split()
        current_map = {i: i for i in range(54)} # Start with identity map

        for move in moves:
            if move not in self._permutations:
                raise ValueError(f"Move '{move}' in sequence is not defined.")
            move_map = self._permutations[move]
            current_map = self._compose_permutations(current_map, move_map)

        return current_map

    def _add_sequence_as_move(self, notation_to_add, sequence_string):
        """
        Defines a new move notation based on the net effect of a sequence
        of existing moves.

        Args:
            notation_to_add (str): The name for the new move (e.g., 'x', 'MyAlg').
            sequence_string (str): The sequence of existing moves
                                   (e.g., "R U R'", "U R U' L'").

        Raises:
            ValueError: If the notation already exists or if sequence contains undefined moves.
        """
        if notation_to_add in self._permutations:
            raise ValueError(f"Move notation '{notation_to_add}' already exists.")

        print(f"Defining '{notation_to_add}' as sequence '{sequence_string}'...")
        try:
            net_permutation = self._get_permutation_from_sequence(sequence_string)
            self._permutations[notation_to_add] = net_permutation
            # Update the list of valid moves if needed dynamically
            if notation_to_add not in self.valid_moves:
                 self.valid_moves.append(notation_to_add)
            print(f"Move '{notation_to_add}' defined successfully.")
        except ValueError as e:
            print(f"Failed to define move '{notation_to_add}': {e}")
            raise # Re-raise the error


    def __str__(self):
        """Returns the current state as a cube string."""
        return "".join(self.state)

    def __call__(self, string):
        self.apply_moves(string)

    def get_state_string(self):
        """Returns the current state as a cube string."""
        return "".join(self.state)

    @staticmethod
    def validate_cubestring(state_string):
        """
        Validates if a string represents a valid Rubik's Cube state.
        Needs to add parity, orientation, and color checks.
        """
        if not isinstance(state_string, str) or len(state_string) != 54:
            return False
        counts = collections.Counter(state_string)
        expected_counts = {face: 9 for face in RubiksCube.FACES}
        return counts == expected_counts

    def solve(self):
        """
        Solves the current cube state using the Kociemba algorithm.
        
        """
        if not KOCIEMBA_AVAILABLE:
            raise RuntimeError("Kociemba library not installed. Cannot solve.")
        try:
            solution = kociemba.solve(self.get_state_string())
            return solution
        except Exception as e:
            raise Exception(f"Kociemba solver failed: {e}")

    def scramble(self, num_moves=25):
        """
        Applies a random sequence of standard moves (U, U', U2, R, ...)
        to the current state.

        Args:
            num_moves (int, optional): The number of random moves to apply.
                                       Defaults to 25.
        """
        # Generate scramble using only the standard 18 moves for conventional scrambling
        standard_moves = [m for m in self.valid_moves if len(m) <= 2 and m[0] in self.FACES]
        if not standard_moves: # Should not happen after init
             standard_moves = [f + s for f in self.FACES for s in ['', "'", '2']]

        scramble_sequence = [random.choice(standard_moves) for _ in range(num_moves)]
        # print(f"Applying scramble: {' '.join(scramble_sequence)}") # Optional: print the scramble
        self.apply_moves(" ".join(scramble_sequence))


    def apply_moves(self, move_sequence, state=None):
        """
        Applies a sequence of moves (like a solution or scramble string)
        to the cube.

        Args:
            move_sequence (str): A space-separated string of moves (e.g., "R U R'").
        """
        moves = move_sequence.split()
        for move in moves:
            state = self.turn(move, state)

    def turn(self, move, state=None):
        """
        Applies a single turn to a cube state using precomputed permutations.
        
        Args:
            move (str): The move to apply (e.g., 'U', "R'", "F2", or custom defined).
            state (list or str, optional): The state to apply the move to.
                                          If None, uses and modifies self.state.
        
        Returns:
            list or None: The resulting state after the move if state was provided,
                         otherwise None when applying to self.state.
        
        Raises:
            ValueError: If the move string is not defined.
        """
        if move not in self._permutations:
            # Check if it's a base move that somehow wasn't generated (shouldn't happen)
            # Or if it's just an invalid notation
            raise ValueError(f"Invalid or undefined move: {move}")

        permutation_map = self._permutations[move]
        
        if state is not None:
            # If state is a string, convert to list for manipulation
            if isinstance(state, str):
                state = list(state)
                
            # Create a temporary copy to read original positions from
            initial_state = list(state)
            result_state = list(state)  # Create a new list to modify
            
            # Apply permutation to the provided state
            for original_index, final_index in permutation_map.items():
                result_state[final_index] = initial_state[original_index]
                
            # Return as string if input was string, otherwise as list
            return ''.join(result_state) if isinstance(state, str) else result_state
        else:
            # Create a temporary copy to read original positions from
            initial_state = list(self.state)
            
            # Update self.state based on where each piece comes *from*
            for original_index, final_index in permutation_map.items():
                self.state[final_index] = initial_state[original_index]
            
            return self.state
    
    def get_canonical_orientation(self, state = None):
        s = self.state if state is None else state
        centers = s[4:54:9]
        canon = self.FACES[centers.index("U")] + self.FACES[centers.index("F")]
        return canon
    
    def get_canon_rotated_state(self, state=None):
        s = state
        canon = self.get_canonical_orientation(s)
        rotation = self.ORIENTATIONS[canon]
        rotated_state = self.rotate_state(rotation, s)
        return rotated_state
    
    def get_rotated_to_canon(self, state=None):
        s = self.state if state is None else state
        canon = self.get_canonical_orientation(s)
        rotation = self.ORIENTATIONS[canon]
        rotated_state = self.apply_moves(rotation, s.copy())
        return rotated_state

    def is_equivalent(self, other_state, state = None):
        """
        Checks if the current cube state is equivalent to another state.
        R U R' U' is equivalent to L D L' D' and so on.
        
        Args:
            other_state (str): The state to compare against in cube string notation.
        
        Returns:
            bool: True if equivalent, False otherwise.
        """
        # produce all equivalencies based on symmetries.
        other_state = self.get_canon_rotated_state(other_state)
        for k, v in self.ORIENTATIONS.items():
            scramble_rotate = self.rotate_state(v, other_state)
            v_p = StringManipulate.inverse(v)
            back_to_base = self.apply_moves(v_p, scramble_rotate)
            if self.is_equal(back_to_base, state):
                return True
        return False
    
    def is_equal(self, other_state, state = None):
        """
        Checks if the current cube state is equal to another state.
        As in, if you applied the same moves to solve the cube, both would be solved
        
        Args:
            other_state (str): The state to compare against in cube string notation.
            state (str, optional): The state to compare against. Defaults to None.
        
        Returns:
            bool: True if equal, False otherwise.
        """
        s = self.state if state is None else state
        s = self.get_canon_rotated_state(s)
        other_state = self.get_canon_rotated_state(other_state)
        return s == other_state

    def is_solved(self, state = None):
        return self.is_equal(self.SOLVED_STATE, state)


    def reset(self):
        """
        Resets the cube to the solved state.
        """
        self.state = list(self.SOLVED_STATE)

    # Add this method inside the RubiksCube class definition

    def display(self, state=None):
        """Prints a visual representation of the current cube state."""
        s = self.state if state is None else state # Shorter alias for self.state list

        # Ensure state has 54 elements before trying to access them all
        if len(s) != 54:
            print("Error: Cube state does not have 54 elements.")
            return

        visual_layout = f"""
             |***********|
             |*{s[0]} * {s[1]} * {s[2]}*|
             |***********|
             |*{s[3]} * {s[4]} * {s[5]}*|
             |***********|
             |*{s[6]} * {s[7]} * {s[8]}*|
             |***********|
 |***********|***********|***********|***********|
 |*{s[36]} * {s[37]} * {s[38]}*|*{s[18]} * {s[19]} * {s[20]}*|*{s[9]} * {s[10]} * {s[11]}*|*{s[45]} * {s[46]} * {s[47]}*|
 |***********|***********|***********|***********|
 |*{s[39]} * {s[40]} * {s[41]}*|*{s[21]} * {s[22]} * {s[23]}*|*{s[12]} * {s[13]} * {s[14]}*|*{s[48]} * {s[49]} * {s[50]}*|
 |***********|***********|***********|***********|
 |*{s[42]} * {s[43]} * {s[44]}*|*{s[24]} * {s[25]} * {s[26]}*|*{s[15]} * {s[16]} * {s[17]}*|*{s[51]} * {s[52]} * {s[53]}*|
 |***********|***********|***********|***********|
             |***********|
             |*{s[27]} * {s[28]} * {s[29]}*|
             |***********|
             |*{s[30]} * {s[31]} * {s[32]}*|
             |***********|
             |*{s[33]} * {s[34]} * {s[35]}*|
             |***********|
"""
        print(visual_layout)


# --- Example Usage ---
if __name__ == "__main__":
    # Create a solved cube (this now computes derived moves in init)
    cube = RubiksCube()
    print(f"Initial state (solved): {cube}")
    print(f"Defined moves: {sorted(cube.valid_moves)}") # Show R, R', R2 etc.

    # Apply derived moves directly
    try:
        unique_U = "R U L B"
        cube.apply_moves(unique_U)
        cube.display() # Show the state after applying the unique move
        cube.turn("U'") # Apply inverse
        cube.display() # Show the state after applying the inverse
    except ValueError as e:
        print(f"Error applying turn: {e}")

    # # Reset and test adding a sequence
    # cube = RubiksCube()
    # print("\nDefining new move 'MyAlg' as 'R U R' U R U2 R'',")
    # sexy_move = "R U R' U'" # Example sequence
    # try:
    #     # First define the base sequence if needed, e.g. Sexy Move
    #     cube._add_sequence_as_move('Sexy', sexy_move)
    #     cube.turn('Sexy') # Apply the sexy move
    #     print(f"State after applying 'Sexy' move once: {cube}") # Apply and print

    #     # Define a longer alg using the base moves
    #     y_perm = "R U' R' U' R U R' F' R U R' U' R' F R"
    #     cube._add_sequence_as_move('YPerm', y_perm)

    #     # Test applying the new move
    #     cube.reset() # Reset
    #     print("Applying YPerm...")
    #     cube.turn('YPerm')
    #     print(f"State after YPerm: {cube}")
    #     # Validate YPerm state here if desired - it should be different from solved

    #     # You can now use 'YPerm' in sequences or solve results if needed
    #     # Note: kociemba solver will still return standard URFDLB moves

    # except ValueError as e:
    #     print(f"Error defining or using custom move: {e}")

    # # Scramble and solve example (unchanged logic, uses derived moves internally now)
    # print("\nScrambling and Solving:")
    # cube = RubiksCube()
    # cube.scramble()
    # scrambled = cube.get_state_string()
    # print(f"Scrambled state: {scrambled}")
    # if KOCIEMBA_AVAILABLE:
    #     try:
    #         solution = cube.solve()
    #         print(f"Solution: {solution}")
    #         # Verify
    #         verifier = RubiksCube(scrambled)
    #         verifier.apply_moves(solution)
    #         print(f"Verifier state after solution: {verifier}")
    #         print(f"Solved correctly? {verifier.get_state_string() == RubiksCube.SOLVED_STATE}")
    #     except Exception as e:
    #         print(f"Error during solve/verify: {e}")