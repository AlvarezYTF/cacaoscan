"""
Refinador de máscaras usando OpenCV.

Este módulo maneja el refinamiento preciso de máscaras,
siguiendo el principio de Responsabilidad Única.
"""
import cv2
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.mask_refinement")


class MaskRefiner:
    """
    Refinador de máscaras usando OpenCV para detección precisa de píxeles.
    
    Esta clase es responsable de:
    - Refinar máscaras usando OpenCV
    - Remover bordes blancos residuales
    - Ajustar píxel por píxel
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def refine(self, rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Refina máscara usando OpenCV para detección precisa de píxeles.
        Remueve bordes blancos residuales y ajusta píxel por píxel.
        
        Args:
            rgb: Imagen RGB original (H, W, 3)
            mask: Máscara inicial del modelo (H, W) con valores 0-255
            
        Returns:
            Máscara refinada (H, W) con valores 0-255
        """
        h, w = mask.shape
        
        # 1. Convertir máscara a binaria
        _, mask_binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        
        # 2. Remover ruido inicial
        kernel_small = np.ones((3, 3), np.uint8)
        mask_clean = cv2.morphologyEx(
            mask_binary, cv2.MORPH_OPEN, kernel_small, iterations=1
        )
        mask_clean = cv2.morphologyEx(
            mask_clean, cv2.MORPH_CLOSE, kernel_small, iterations=1
        )
        
        # 3. Detectar y remover bordes blancos
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        
        # Identificar píxeles blancos/claros (fondo residual)
        white_threshold = 220
        is_white = gray > white_threshold
        
        # Dilatar máscara para encontrar área cerca del borde
        kernel_dilate = np.ones((3, 3), np.uint8)
        mask_dilated = cv2.dilate(mask_clean, kernel_dilate, iterations=1)
        border_region = mask_dilated.astype(bool) & ~(mask_clean.astype(bool))
        
        # Remover píxeles blancos en región de borde
        mask_clean = np.where(
            border_region & is_white, 0, mask_clean
        ).astype(np.uint8)
        
        # 4. Erosionar ligeramente para remover bordes blancos residuales
        kernel_erode = np.ones((3, 3), np.uint8)
        mask_clean = cv2.erode(mask_clean, kernel_erode, iterations=1)
        
        # Remover áreas blancas dentro del objeto erosionado
        mask_eroded_white = np.where(
            is_white & (mask_clean > 128), 0, mask_clean
        ).astype(np.uint8)
        
        # 5. Operaciones morfológicas mínimas para evitar halos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask_clean = cv2.morphologyEx(
            mask_eroded_white, cv2.MORPH_CLOSE, kernel, iterations=1
        )
        mask_clean = cv2.morphologyEx(
            mask_clean, cv2.MORPH_OPEN, kernel, iterations=1
        )
        
        # 6. Detectar contorno más grande (el grano de cacao)
        contours, _ = cv2.findContours(
            mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if contours:
            # Encontrar contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Crear máscara solo para contorno más grande
            mask_final = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask_final, [largest_contour], -1, 255, thickness=-1)
            
            # 7. Usar GrabCut para refinamiento adicional (mejora precisión píxel por píxel)
            try:
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                
                # Preparar máscara para GrabCut
                gc_mask = np.where(
                    mask_final > 128, cv2.GC_PR_FGD, cv2.GC_PR_BGD
                ).astype(np.uint8)
                
                # Aplicar GrabCut
                bgd_model = np.zeros((1, 65), np.float64)
                fgd_model = np.zeros((1, 65), np.float64)
                cv2.grabCut(
                    bgr, gc_mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK
                )
                
                # Crear máscara final de GrabCut
                mask_grabcut = np.where(
                    (gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0
                ).astype(np.uint8)
                
                # Combinar: usar GrabCut pero mantener solo área del contorno más grande
                mask_final = cv2.bitwise_and(mask_grabcut, mask_final)
                
            except Exception:
                # Si GrabCut falla, usar solo contorno
                pass
            
            # 8. Remover artefactos pequeños (componentes conectados pequeños)
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
                mask_final, connectivity=8
            )
            if num_labels > 1:
                # Mantener solo componente más grande (el grano)
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                mask_final = (labels == largest_label).astype(np.uint8) * 255
            
        else:
            # Si no hay contornos, usar máscara limpia
            mask_final = mask_clean
        
        return mask_final

