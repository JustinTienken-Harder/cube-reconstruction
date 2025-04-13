from PIL import Image
import numpy as np
from scipy.linalg import solve
from validators.symmetries import Symmetries

def color_permutation_operator(map = None, rbf_choice = "gaussian", epsilon = 0.85):
    """
    Constructs a non-linear operator for the given color permutation using RBF interpolation.

    The permutation is:
    White -> Green
    Red -> Red
    Green -> Yellow
    Yellow -> Blue
    Orange -> Orange
    Blue -> White

    Colors are represented as RGB vectors (normalized to [0, 1]).
    """

    # Define the input colors
    colors = {
        "U": np.array([1, 1, 1]),
        "R": np.array([1, 0, 0]),
        "F": np.array([0, 1, 0]),
        "D": np.array([1, 1, 0]),
        "L": np.array([1, 0.65, 0]),
        "B": np.array([0, 0, 1])
    }
    input_colors = np.array([colors[x] for x in Symmetries.FACES] + np.array([0, 0, 0]))

    # Define the target colors
    
    target_colors = np.array([colors[map[x]] for x in Symmetries.FACES] + np.array([0, 0, 0]))

    num_points = len(input_colors)

    # Choose a radial basis function (e.g., r^3)
    def options(choice):
        if choice == "gaussian":
            return lambda r: np.exp(-(r/epsilon)**2)
        elif choice == "linear":
            return lambda r: r
        elif choice == "cubic":
            return lambda r: r**3
        elif choice == "quintic":
            return lambda r: r**5
        elif choice == "inverse_quadratic":
            return lambda r: 1/(1 + (r*epsilon)**2)
        elif choice == 'mq':
            return lambda r: np.sqrt(1 + (r/epsilon)**2)
        elif choice == 'thin_plate':
            return lambda r: r**1/2 * np.log(r + 1e-10)
        elif choice == 'imq':
            return lambda r: 1/np.sqrt(1 + (r/epsilon)**2)
        elif choice == "bump":
            return lambda r: np.exp(-1/(1 - (r/epsilon)**2))
        else:
            raise ValueError("Invalid RBF choice")

    rbf = options(rbf_choice)
    # Calculate the distance matrix
    distance_matrix = np.zeros((num_points, num_points))
    for i in range(num_points):
        for j in range(num_points):
            distance_matrix[i, j] = np.linalg.norm(input_colors[i] - input_colors[j])

    # Form the matrix A
    A = rbf(distance_matrix)

    # Form the matrix C' of target colors
    C_prime = target_colors

    # Solve for the weight matrix W
    try:
        W = solve(A, C_prime)
    except np.linalg.LinAlgError:
        print("Singular matrix A: RBF interpolation might not be uniquely defined for these points with the chosen RBF.")
        return None

    return input_colors, W, rbf

def apply_operator_to_image_vectorized(image_path, output_path, operator_data):
    """
    Applies the color permutation operator to each pixel of an image using vectorized NumPy operations.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the output image.
        operator_data (tuple): A tuple containing input_colors (np.array), weights (np.array), and rbf function.
    """
    try:
        input_colors, W, rbf = operator_data
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img, dtype=np.float32) / 255.0  # Normalize to [0, 1]

        height, width, channels = img_array.shape
        pixels = img_array.reshape((-1, channels))  # Reshape to (N_pixels, 3)

        # Vectorized distance calculation
        diffs = pixels[:, np.newaxis, :] - input_colors[np.newaxis, :, :]  # (N_pixels, 6, 3)
        distances = np.linalg.norm(diffs, axis=2)  # (N_pixels, 6)

        # Apply RBF
        rbf_values = rbf(distances)  # (N_pixels, 6)

        # Matrix multiplication with weights
        transformed_pixels = np.dot(rbf_values, W)  # (N_pixels, 3)

        # Ensure values stay within [0, 1]
        transformed_pixels = np.clip(transformed_pixels, 0, 1)

        # Reshape back to image shape
        transformed_array = transformed_pixels.reshape(img_array.shape)

        # Scale back to [0, 255] and convert to uint8
        output_img_array = (transformed_array * 255).astype(np.uint8)
        output_img = Image.fromarray(output_img_array)
        output_img.save(output_path)

        print(f"Transformed image (vectorized) saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    rotations = ["z y2", "x2", "z y", "x'", "z' y"]
    sym = Symmetries()
    for key, value in sym._orientations.items():
        sym = Symmetries()
        operator_data = color_permutation_operator(value, rbf_choice="gaussian", epsilon=.85)

        if operator_data:
            input_image_path = "data/SEI_228697583.webp"  # Replace with the actual path to your image
            output_image_path_vectorized = f"data/output{key}.webp"



            apply_operator_to_image_vectorized(input_image_path, output_image_path_vectorized, operator_data)