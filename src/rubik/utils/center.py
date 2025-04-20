from rubik.symmetries import Symmetries

class CenterValidate:
    def _get_centers(self, s):
        return s[4:54:9]
    
    def validate_centers(self, s):
        right_orientation = Symmetries.get_canonical_orientation(s)
        centers = self._get_centers(right_orientation)
        # Check if the centers are in the correct orientation
        return centers == "URFDLB"
    
    @staticmethod
    def center_loss(s1, s2):
        """
        This method calculates the center loss between two cube strings.
        It returns the number of centers that are not in the correct orientation.
        """
        # Get the centers from both strings
        centers1 = s1[4:54:9]
        centers2 = s2[4:54:9]
        
        # Count the number of centers that are not in the correct orientation
        loss = sum(1 for c1, c2 in zip(centers1, centers2) if c1 != c2)
        
        return loss