# cube-reconstruction

This repository hosts a variety of sub-projects. Essentially a mono-repo.

## [ ] Project 1: Cube State/Scramble Extractor

1. [x] Cube simulator: A simple python cube that has a string-representation. Solve, scramble, string equivalence that's starting orientation invariant.
2. [ ] A cube validator: Takes arbitrary 54 length strings containing 6 letters, and validates them as a valid rubik's cube state.
3. [ ] Cube loss: String to a collection of losses for how much the string is not a rubik's cube. Constraints: [x] Corner orientation (0-2), permutation (0-1), cubie(0-2), [ ] Edge Orientation(0-1), permutation (0-1), cubie (0-1), [x] Centers(0-6), [ ] stickers (0-42), [x] total_state (0 valid, 1 invalid)
4. [ ] A RUCSAC-WGAN: This is a RUbik's Cube Scramble Auxilary Classifier, Wasserstein Generative Adversarial Network. A generative machine learning model (to be) trained to produce valid cube states by utilizing an auxillary classifier (utilizing #3), to backpropagate Rubik's cube constraints. Wasserstein losses for descriminator (Real distribution vs generator distribution) to promote better training of GAN.
5. [ ] Image to cube-state model, with RUCSAC-WG head, and extra-losses from AC heads.
6. [ ] Extend to a video to cube-state model that takes inspection, and produces the cube-state
7. [x] Cube State to actual scramble. Kociemba the cube state, get a solution. Invert Solution. There's your scramble.

## [ ] Project 2: Wack Image Augmentation

Image augmentation project to multiply the data by 24 for all symmetries of the Rubik's cube. I'll just call it Rubik's cube color space rotation.

- [x] Color rotation with radial basis functions.
- [ ] Explore different basis RGB -> HSV/LAB/CEILAB -> Rotation -> RGB
- [ ] Convert to data augmentation for data loader
- [ ] Preprocess video/images

## [ ] Project 3: Data Annotation

Data annotation bootstrap:

- [ ] Lil UI framework for: Keyframe detection of (scramble, optional), Inspection, Solution, Region proposal, Cube Detection/tracking
- [ ] Moondream detector for bootstrapping region/detection
- [ ] Kallman Filters for tracking detections

## [ ] Project 4: Keyframe Detection 

Model for video to keyframe detections to provide clip bounding boxes. 

- 3D CNN

## [ ] Project 5: Scramble Extraction

Largely solved from Project #1

## [ ] Project 6: VIT for solve reconstruction

## [ ] Optional: BERT seq2seq

Error correction of reconstructions through BERT seq2seq transformers to push success rate up.



