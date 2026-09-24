import cv2
import numpy as np

class DIPEngine:
    """
    Digital Image Processing (DIP) Engine.
    Handles color transformation, illumination normalization (CLAHE),
    noise filtering, and Local Binary Pattern (LBP) texture extraction.
    """

    def __init__(self, clip_limit=2.5, tile_grid_size=(8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def to_grayscale(self, bgr_image: np.ndarray) -> np.ndarray:
        """Convert BGR image to single-channel 8-bit Grayscale."""
        if len(bgr_image.shape) == 2:
            return bgr_image
        return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

    def apply_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Contrast Limited Adaptive Histogram Equalization (CLAHE).
        Compensates for non-uniform ambient illumination, shadows, and low lighting.
        """
        if len(gray_image.shape) == 3:
            gray_image = self.to_grayscale(gray_image)
        return self.clahe.apply(gray_image)

    def apply_bilateral_filter(self, gray_image: np.ndarray, d=5, sigma_color=50, sigma_space=50) -> np.ndarray:
        """
        Bilateral filtering to reduce high-frequency sensor noise while strictly
        preserving sharp facial edge boundaries.
        """
        return cv2.bilateralFilter(gray_image, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)

    def preprocess_face_roi(self, face_bgr_or_gray: np.ndarray, target_size=(200, 200)) -> np.ndarray:
        """
        Complete DIP pipeline for face Region of Interest (ROI):
        1. Grayscale conversion
        2. Bilinear/Bicubic geometric resizing
        3. CLAHE illumination normalization
        4. Subtle edge-preserving bilateral filtering
        """
        if len(face_bgr_or_gray.shape) == 3:
            gray = self.to_grayscale(face_bgr_or_gray)
        else:
            gray = face_bgr_or_gray.copy()

        # Resize to standard canonical dimensions
        resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA if gray.shape[0] > target_size[0] else cv2.INTER_CUBIC)

        # Apply CLAHE to equalize facial contrast
        equalized = self.clahe.apply(resized)

        # Bilateral filter for noise reduction with edge preservation
        filtered = self.apply_bilateral_filter(equalized, d=5, sigma_color=40, sigma_space=40)
        return filtered

    def compute_lbp(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Vectorized computation of Local Binary Patterns (LBP) texture descriptor.
        Evaluates 8 circular/square neighbors for each pixel:
        LBP(x_c, y_c) = sum_{p=0..7} s(i_p - i_c) * 2^p
        where s(x) = 1 if x >= 0 else 0.
        """
        if len(gray_image.shape) == 3:
            gray = self.to_grayscale(gray_image)
        else:
            gray = gray_image

        h, w = gray.shape
        if h < 3 or w < 3:
            return np.zeros_like(gray, dtype=np.uint8)

        # Center pixels
        center = gray[1:h-1, 1:w-1].astype(np.int16)

        # 8 Neighbors:
        # 0: Top-Left       (r-1, c-1)
        # 1: Top            (r-1, c)
        # 2: Top-Right      (r-1, c+1)
        # 3: Right          (r,   c+1)
        # 4: Bottom-Right   (r+1, c+1)
        # 5: Bottom         (r+1, c)
        # 6: Bottom-Left    (r+1, c-1)
        # 7: Left           (r,   c-1)
        n0 = gray[0:h-2, 0:w-2].astype(np.int16) >= center
        n1 = gray[0:h-2, 1:w-1].astype(np.int16) >= center
        n2 = gray[0:h-2, 2:w  ].astype(np.int16) >= center
        n3 = gray[1:h-1, 2:w  ].astype(np.int16) >= center
        n4 = gray[2:h  , 2:w  ].astype(np.int16) >= center
        n5 = gray[2:h  , 1:w-1].astype(np.int16) >= center
        n6 = gray[2:h  , 0:w-2].astype(np.int16) >= center
        n7 = gray[1:h-1, 0:w-2].astype(np.int16) >= center

        # Bitwise accumulation of 8-bit binary pattern
        lbp = (n0 * 1 +
               n1 * 2 +
               n2 * 4 +
               n3 * 8 +
               n4 * 16 +
               n5 * 32 +
               n6 * 64 +
               n7 * 128).astype(np.uint8)

        # Pad with 1 pixel border to preserve original dimensions
        lbp_padded = cv2.copyMakeBorder(lbp, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
        return lbp_padded

    def create_dip_quad_view(self, bgr_frame: np.ndarray) -> np.ndarray:
        """
        Creates a 4-quadrant real-time educational DIP inspector panel:
        [ Quad 1: Raw BGR Camera Feed      ] [ Quad 2: Grayscale Intensity Map    ]
        [ Quad 3: CLAHE Equalized Contrast  ] [ Quad 4: LBP Micro-Texture Patterns ]
        """
        h, w = bgr_frame.shape[:2]
        half_w, half_h = w // 2, h // 2

        # 1. Raw BGR
        q1 = cv2.resize(bgr_frame, (half_w, half_h))
        self._draw_quad_label(q1, "1. RAW INPUT [BGR SENSOR]", (0, 255, 255))

        # 2. Grayscale
        gray = self.to_grayscale(bgr_frame)
        q2_gray = cv2.resize(gray, (half_w, half_h))
        q2 = cv2.cvtColor(q2_gray, cv2.COLOR_GRAY2BGR)
        self._draw_quad_label(q2, "2. GRAYSCALE LUMINANCE [Y-CHANNEL]", (200, 200, 200))

        # 3. CLAHE
        clahe_img = self.apply_clahe(gray)
        q3_clahe = cv2.resize(clahe_img, (half_w, half_h))
        q3 = cv2.cvtColor(q3_clahe, cv2.COLOR_GRAY2BGR)
        self._draw_quad_label(q3, "3. CLAHE CONTRAST ENHANCEMENT", (0, 255, 128))

        # 4. LBP Texture
        # Subsample for fast real-time frame rates in quad view
        small_gray = cv2.resize(gray, (half_w, half_h))
        lbp_img = self.compute_lbp(small_gray)
        # Apply colormap to make micro-textures vibrant and easy to observe
        lbp_color = cv2.applyColorMap(lbp_img, cv2.COLORMAP_JET)
        self._draw_quad_label(lbp_color, "4. LBP MICRO-TEXTURE ANALYSIS", (255, 165, 0))

        # Combine into 2x2 grid
        top_row = np.hstack([q1, q2])
        bottom_row = np.hstack([q3, lbp_color])
        quad_display = np.vstack([top_row, bottom_row])

        # Add crosshair separators
        cv2.line(quad_display, (half_w, 0), (half_w, h), (40, 40, 40), 2)
        cv2.line(quad_display, (0, half_h), (w, half_h), (40, 40, 40), 2)

        return quad_display

    def _draw_quad_label(self, img: np.ndarray, text: str, color=(0, 255, 0)):
        """Overlay informative panel header."""
        cv2.rectangle(img, (0, 0), (img.shape[1], 26), (20, 20, 20), -1)
        cv2.putText(img, text, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
