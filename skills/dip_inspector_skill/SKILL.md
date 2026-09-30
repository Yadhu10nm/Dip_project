# DIP Inspector Skill

## Purpose
Renders an educational 4-quadrant real-time split screen demonstrating digital image processing stages: Raw Input, Grayscale Luminance, CLAHE Contrast Enhancement, and LBP Micro-Texture analysis.

## Responsibilities
- Downscale frames into sub-quadrants.
- Generate grayscale luminance map ($Y$-channel).
- Compute Contrast Limited Adaptive Histogram Equalization (CLAHE).
- Compute Local Binary Patterns (LBP) texture representation rendered in Jet pseudocolor.
- Composite panels into a single 4-quadrant inspection screen with dividing crosshairs.

## Inputs
- BGR video frame (`numpy.ndarray`).

## Outputs
- 4-quadrant composite video frame (`numpy.ndarray`).

## Tools / Libraries
- OpenCV (`cv2.createCLAHE`, `cv2.applyColorMap`, `cv2.resize`, `cv2.line`)
- NumPy

## Workflow
1. Accept input frame.
2. Downsample and annotate Quad 1 (Raw BGR).
3. Convert to grayscale and downsample for Quad 2.
4. Apply CLAHE and annotate for Quad 3.
5. Compute LBP operator, apply Jet colormap, and annotate for Quad 4.
6. Assemble quadrants and return composite frame.

## Commands
- `create_quad_view(bgr_frame)`: Produces the 4-way inspection canvas.

## Error Handling
- Returns original frame safely if input is None or zero-sized.

## Performance Requirements
- Sub-15ms generation per frame via optimized vectorized NumPy LBP kernel.

## Dependencies
- OpenCV, NumPy

## Example
```python
from skills.dip_inspector_skill.implementation import DIPInspectorSkill

inspector = DIPInspectorSkill()
quad_view = inspector.create_quad_view(webcam_frame)
```

## Rules
- Educational visualization only; must not modify or disrupt recognition processing.
