### Description
    - This is my attempt to dewarp pages utilizing a Uunet diffusion model.

### Setup Environment: 
    - Install Anaconda: https://www.anaconda.com/download
    - Install CUDA Toolkit: https://developer.nvidia.com/cuda-12-8-0-download-archive
    - Set directory to the root, execute:
        - conda env create -f environment.yml
        - conda activate PageDewarp

### Synthetic Data Generation:

Utilizing the Harey 2015 dataset, and Blender for a 3d Environment, I created the synthetic data by importing each of the images and snapping shotting intermediate frames of a translation that allow the creation of unique perspective warps.

![Demo animation](/Documentation/demo.gif)

Showcasing the Image Generation:

| Frame 0      | Frame 10     | Frame 20     |
|--------------|--------------|--------------|
| ![](/Documentation/Images/pan_sample_0000.png) | ![](/Documentation/Images/pan_sample_0010.png) | ![](/Documentation/Images/pan_sample_0020.png) |
| Frame 30     | Frame 40     | Frame 50     |
| ![](/Documentation/Images/pan_sample_0030.png) | ![](/Documentation/Images/pan_sample_0040.png) | ![](/Documentation/Images/pan_sample_0050.png) |
| Frame 60     | Frame 70     | Frame 80     |
| ![](/Documentation/Images/pan_sample_0060.png) | ![](/Documentation/Images/pan_sample_0070.png) | ![](/Documentation/Images/pan_sample_0080.png) |
| Frame 90     | Frame 100    | Frame 110    |
| ![](/Documentation/Images/pan_sample_0090.png) | ![](/Documentation/Images/pan_sample_0100.png) | ![](/Documentation/Images/pan_sample_0110.png) |
| Frame 120    |              |              |
| ![](/Documentation/Images/pan_sample_0120.png) |              |              |


### References:
    - Adam W Harley, Alex Ufkes, & Konstantinos G Derpanis 2015. Evaluation of Deep Convolutional Nets for Document Image Classification and Retrieval. https://huggingface.co/datasets/aharley/rvl_cdip https://github.com/TylerDeBruin/Page-Dewarp