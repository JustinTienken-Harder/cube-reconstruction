import pytest
from src.rubikrubik import RubiksCube  # Adjust the import path as needed



class TestRubiksCubeState:
    def setup_method(self):
        """Set up a fresh cube instance for each test"""
        self.cube = RubiksCube()
        self.solved_state = RubiksCube.SOLVED_STATE

    def test_initial_state(self):
        # Verify specific stickers moved to expected positions
        # Example: checking specific state elements after U move
        expected_state = self.solved_state  # Replace with actual expected values
        assert self.cube.get_state_string() == expected_state
        assert self.cube.is_solved() is True
    
    def test_moves(self):
        """Test that all individual moves work correctly
        
        Don't need to test all moves, as the rest are generated from the base cases"""
        moves = ["U", "D", "L", "R", "F", "B"]
        move_states = {
            "U": "UUUUUUUUUBBBRRRRRRRRRFFFFFFDDDDDDDDDFFFLLLLLLLLLBBBBBB",
            "D": 'UUUUUUUUURRRRRRFFFFFFFFFLLLDDDDDDDDDLLLLLLBBBBBBBBBRRR',
            "L": 'BUUBUUBUURRRRRRRRRUFFUFFUFFFDDFDDFDDLLLLLLLLLBBDBBDBBD',
            "R": 'UUFUUFUUFRRRRRRRRRFFDFFDFFDDDBDDBDDBLLLLLLLLLUBBUBBUBB',
            "F": 'UUUUUULLLURRURRURRFFFFFFFFFRRRDDDDDDLLDLLDLLDBBBBBBBBB',
            "B": 'RRRUUUUUURRDRRDRRDFFFFFFFFFDDDDDDLLLULLULLULLBBBBBBBBB',
        }

        for move in moves:
            initial_state = self.cube.get_state_string()
            self.cube.turn(move)
            assert self.cube.get_state_string() == move_states[move]
            # Check that the cube is not solved
            assert not self.cube.is_solved()
            # Revert the move
            self.cube.turn(move + "'")
            # Check that the cube is back to its original state
            assert self.cube.get_state_string() == initial_state

    def test_algorithm(self):
        """Test that a specific algorithm works correctly"""
        # Apply a scramble
        alg = "D B2 D2 L2 B2 L2 B2 U' B2 F2 U2 R D' L2 B D L R' F D2 R"
        resulting_state = 'URFBULBLDLDDRRDULRDUFFFBDRBBULDDFULBFURFLUFBLRDLFBRUBR'
        self.cube.apply_moves(alg)
        assert self.cube.get_state_string() == resulting_state
        inverse = "R' D2 F' R L' D' B' L2 D R' U2 F2 B2 U B2 L2 B2 L2 D2 B2 D'"
        self.cube(inverse)
        # Cube should be solved again
        assert self.cube.get_state_string() == self.solved_state

    def test_solver(self):
        scramble = "D B2 D2 L2 B2 L2 B2 U' B2 F2 U2 R D' L2 B D L R' F D2 R"
        self.cube.apply_moves(scramble)
        solution = self.cube.solve()
        self.cube.apply_moves(solution)
        assert self.cube.get_state_string() == self.solved_state
        assert self.cube.is_solved() is True