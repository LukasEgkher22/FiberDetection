# Project description
## Data
https://zenodo.org/records/5483719#.ZD47Wi8Rpqs

## Goal
Segment individual fibers and measure their orientation and curvature.

## Tasks
1. Detect fibers in each slice - (x,y)-direction
2. Track fibers in the z-direction as 3D curves
3. Measure fiber orientation - azimuth and elevation angles
4. Measure fiber curvature
5. Make histograms of orientation angles and curvatures
6. Compare your method to low resolution data (downscale the samples)

## Reference
Fiber analysis:
https://journals.sagepub.com/doi/10.1177/00219983211052741

## Contact
Andreas Dahl (abda@dtu.dk)

# ToDo
- copy/load the following zip files into the FiberDetection/data folder: (I would like to not have the data in the repo)
    - Mock-01_FoV_2_B2_recon_2Dtif.zip
    - UD-01_FoV_2_B2_recon_2Dtif.zip
- unzip them by running the following command
```bash
unzip UD-01_FoV_2_B2_recon_2Dtif.zip
unzip Mock-01_FoV_2_B2_recon_2Dtif.zip
```
- Install packages for merging 2D tiff files (if needed):
```bash
pip install natsort
```


QUESTIONS:
* downscaling with factor two dissapoints already
* curvature is more for UD data - should not be the case
* presentation length ? and format, theory?

