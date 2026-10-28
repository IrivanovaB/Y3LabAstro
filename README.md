# Y3LabAstro
Y3 Lab Astronomical Image Processing

This project is using object detection to count the number of astronomical objects in the provided image of the Lockman Hole North Field. Using this data, we can establish the relation between the number of objects that can be seen per apparent magnitude. We aim to investigate this relation with respect to a predefined model which predicts log(N) = 0.6m + c where N = cumulative count, m = apparent magnitude, and c = constant - which is based on assumptions such as a uniform distribution of galaxies. 

This directory works as follows:

Y3LabAstro/
    archived/
        old files 
    CCfits_source/
        information about CC fits
    data/
        the folder where the output data is loaded into
    figures/
        figures generated during testing
    figures_presentation/
        figures generated that are used in the presentation
    Fits_Data/
        the input image and various alterations to it

    analysis.py
        calculates and plots the relation described above
    header.py
        allows for the header of the image to be viewed in an interactive window or by printing it
    images.py
        a module used to load in the image and perform some operations to it
    maths.py
        contains the customised mathematical functions used by other modules
    photometry_testing.py 
        tests assumptions that were used in the photometry pipeline
    photometry.py
        reads in the image, does the object detection, and produces the photometry
    shape_classify.py
        identifies the shape of each object based on the object's parameters and plots this against its magnitude
    simulate.py
        performs a simulation to see if our code works for artificial data
    snr.py
        plots the average SNR per apparent magnitude


To run:
    1. Run photometry.py
    2. Run classify.py


Main Package Dependencis and Versions:
    astropy                      8.0.1    
    imageio                      2.37.4              
    matplotlib-base              3.11.2   
    numpy                        2.5.3             
    opencv                       4.13.0  
    scikit-image                 0.26.0 
    scipy                        1.18.1

Suitable Python Version:
    python                       3.14.8
