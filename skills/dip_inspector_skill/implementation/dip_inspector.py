import cv2
import numpy as np
import config


class DIPInspectorSkill:
    """
    Digital Image Processing (DIP) Educational Inspector Skill.
    Constructs a live 4-quadrant diagnostic display demonstrating image transformations:
    - Quad 1: Raw BGR Camera Sensor Feed
    - Quad 2: Grayscale Luminance Intensity (Y-Channel)
    - Quad 3: CLAHE Local Contrast Enhancement
    - Quad 4: LBP (Local Binary Patterns) Micro-Texture Descriptor (Jet pseudo-color)

    RULE:
    Educational visualization only; does not alter recognition data or downstream processing.
    """

    def __init__(
        self,
        clip_limit: float = config.CLAHE_CLIP_LIMIT,
        tile_grid_size: tuple = config.CLAHE_TILE_GRID_SIZE,
    ):
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    def create_quad_view(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Builds a 4-quadrant side-by-side comparative inspection canvas.
        Input: BGR Frame (numpy.ndarray)
        Output: 4-Quadrant Composite BGR Frame (numpy.ndarray)
        """
        if bgr_frame is None or bgr_frame.size == 0:
            return bgr_frame

        h, w = bgr_frame.shape[:2]
        half_w, half_h = w // 2, h // 2

        # 1. Raw BGR Input
        q1 = cv2.resize(bgr_frame, (half_w, half_h))
        self._overlay_panel_header(q1, "1. RAW INPUT [BGR SENSOR]", (0, 255, 255))

        # 2. Grayscale Luminance
        if len(bgr_frame.shape) == 3:
            gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = bgr_frame.copy()

        q2_gray = cv2.resize(gray, (half_w, half_h))
        q2 = cv2.cvtColor(q2_gray, cv2.COLOR_GRAY2BGR)
        self._overlay_panel_header(q2, "2. GRAYSCALE LUMINANCE [Y-CHANNEL]", (200, 200, 200))

        # 3. CLAHE Local Contrast Equalization
        clahe_img = self.clahe.apply(gray)
        q3_clahe = cv2.resize(clahe_img, (half_w, half_h))
        q3 = cv2.cvtColor(q3_clahe, cv2.COLOR_GRAY2BGR)
        self._overlay_panel_header(q3, "3. CLAHE CONTRAST ENHANCEMENT", (0, 255, 128))

        # 4. Local Binary Patterns (LBP) Texture Map
        small_gray = cv2.resize(gray, (half_w, half_h))
        lbp_map = self._compute_lbp(small_gray)
        lbp_color = cv2.applyColorMap(lbp_map, cv2.COLORMAP_JET)
        self._overlay_panel_header(lbp_color, "4. LBP MICRO-TEXTURE ANALYSIS", (255, 165, 0))

        # Combine into 2x2 grid
        top_row = np.hstack([q1, q2])
        bottom_row = np.hstack([q3, lbp_color])
        composite = np.vstack([top_row, bottom_row])

        # Crosshair division lines
        cv2.line(composite, (half_w, 0), (half_w, h), (40, 40, 40), 2)
        cv2.line(composite, (0, half_h), (w, half_h), (40, 40, 40), 2)

        return composite

    def _compute_lbp(self, gray: np.ndarray) -> np.ndarray:
        """Vectorized LBP operator computation."""
        h, w = gray.shape
        if h < 3 or w < 3:
            return np.zeros_like(gray, dtype=np.uint8)

        center = gray[1:h-1, 1:w-1].astype(np.int16)
        n0 = (gray[0:h-2, 0:w-2].astype(np.int16) >= center) * 1
        n1 = (gray[0:h-2, 1:w-1].astype(np.int16) >= center) * 2
        n2 = (gray[0:h-2, 2:w  ].astype(np.int16) >= center) * 4
        n3 = (gray[1:h-1, 2:w  ].astype(np.int16) >= center) * 8
        n4 = (gray[2:h  , 2:w  ].astype(np.int16) >= center) * 16
        n5 = (gray[2:h  , 1:w-1].astype(np.int16) >= center) * 32
        n6 = (gray[2:h  , 0:w-2].astype(np.int16) >= center) * 64
        n7 = (gray[1:h-1, 0:w-2].astype(np.int16) >= center) * 128
        lbp = (n0 + n1 + n2 + n3 + n4 + n5 + n6 + n7).astype(np.uint8)
        return cv2.copyMakeBorder(lbp, 1, 1, 1, 1, cv2.BORDER_REPLICATE)

    def _overlay_panel_header(self, img: np.ndarray, title: str, color: tuple):
        cv2.rectangle(img, (0, 0), (img.shape[1], 26), (20, 20, 20), -1)
        cv2.putText(img, title, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
