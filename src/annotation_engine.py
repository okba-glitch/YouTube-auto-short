"""
annotation_engine.py - نظام الشروح البصرية (Visual Annotations)

يضيف أسهم، تظليلات، وتعليقات نصية على الفيديو لتوضيح المفاهيم المهمة.
يستخدم OpenCV لرسم العناصر البصرية على الإطارات (Frames).

الأنواع المدعومة:
- أسهم (Arrows) - تشير من نقطة لأخرى
- تظليلات (Highlights) - صناديق ملونة حول المناطق المهمة
- نصوص توضيحية (Text Annotations) - شرح نصي على الإطار
- دوائر (Circles) - تركيز على نقاط محددة
- خطوط (Lines) - تخطيط وتقسيم
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from enum import Enum


class AnnotationType(Enum):
    """أنواع الشروح المدعومة"""
    ARROW = "arrow"
    HIGHLIGHT_BOX = "highlight_box"
    CIRCLE = "circle"
    LINE = "line"
    TEXT = "text"
    UNDERLINE = "underline"
    CURVED_ARROW = "curved_arrow"


class AnnotationEngine:
    """محرك الشروح البصرية"""
    
    # الألوان الاحترافية (BGR format)
    COLOR_RED = (0, 0, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE = (255, 0, 0)
    COLOR_YELLOW = (0, 255, 255)
    COLOR_CYAN = (255, 255, 0)
    COLOR_MAGENTA = (255, 0, 255)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_ORANGE = (0, 165, 255)
    COLOR_LIME = (0, 255, 0)
    COLOR_PURPLE = (128, 0, 128)
    
    # الألوان الفاتحة (Pastel)
    COLOR_PASTEL_RED = (100, 150, 255)
    COLOR_PASTEL_BLUE = (255, 150, 100)
    COLOR_PASTEL_GREEN = (100, 255, 150)
    
    def __init__(self, frame_width: int = 1920, frame_height: int = 1080):
        """تهيئة محرك الشروح
        
        Args:
            frame_width: عرض الإطار (Frame)
            frame_height: ارتفاع الإطار
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.font_size = 1.2
    
    def add_arrow(self, frame: np.ndarray, start_pos: Tuple[int, int], 
                  end_pos: Tuple[int, int], color: Tuple = None, 
                  thickness: int = 3, tip_length: float = 0.15) -> np.ndarray:
        """رسم سهم من نقطة البداية إلى نقطة النهاية
        
        Args:
            frame: إطار الفيديو
            start_pos: موقع البداية (x, y)
            end_pos: موقع النهاية (x, y)
            color: لون السهم (BGR)
            thickness: سمك الخط
            tip_length: طول رأس السهم كنسبة من طول السهم
            
        Returns:
            الإطار بعد إضافة السهم
        """
        if color is None:
            color = self.COLOR_RED
        
        cv2.arrowedLine(
            frame,
            start_pos,
            end_pos,
            color,
            thickness,
            tipLength=tip_length
        )
        return frame
    
    def add_highlight_box(self, frame: np.ndarray, x: int, y: int, 
                         width: int, height: int, 
                         color: Tuple = None, thickness: int = 3,
                         fill: bool = False, alpha: float = 0.3) -> np.ndarray:
        """تظليل منطقة معينة برسم صندوق ملون
        
        Args:
            frame: إطار الفيديو
            x: إحداثي X الأعلى الأيسر
            y: إحداثي Y الأعلى الأيسر
            width: عرض الصندوق
            height: ارتفاع الصندوق
            color: لون الصندوق (BGR)
            thickness: سمك الخط (0 للملء)
            fill: ملء الصندوق بشفافية
            alpha: مستوى الشفافية (0-1)
            
        Returns:
            الإطار بعد إضافة التظليل
        """
        if color is None:
            color = self.COLOR_YELLOW
        
        pt1 = (x, y)
        pt2 = (x + width, y + height)
        
        if fill:
            # إنشاء نسخة مؤقتة للرسم عليها
            overlay = frame.copy()
            cv2.rectangle(overlay, pt1, pt2, color, -1)
            # دمج الشفافية
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        else:
            cv2.rectangle(frame, pt1, pt2, color, thickness)
        
        return frame
    
    def add_circle(self, frame: np.ndarray, center: Tuple[int, int],
                   radius: int, color: Tuple = None, thickness: int = 2,
                   fill: bool = False) -> np.ndarray:
        """رسم دائرة حول نقطة معينة
        
        Args:
            frame: إطار الفيديو
            center: مركز الدائرة (x, y)
            radius: نصف قطر الدائرة
            color: لون الدائرة (BGR)
            thickness: سمك الخط
            fill: ملء الدائرة
            
        Returns:
            الإطار بعد إضافة الدائرة
        """
        if color is None:
            color = self.COLOR_GREEN
        
        thickness = -1 if fill else thickness
        cv2.circle(frame, center, radius, color, thickness)
        return frame
    
    def add_line(self, frame: np.ndarray, start_pos: Tuple[int, int],
                 end_pos: Tuple[int, int], color: Tuple = None,
                 thickness: int = 2, line_type: str = "solid") -> np.ndarray:
        """رسم خط من نقطة لأخرى
        
        Args:
            frame: إطار الفيديو
            start_pos: نقطة البداية (x, y)
            end_pos: نقطة النهاية (x, y)
            color: لون الخط (BGR)
            thickness: سمك الخط
            line_type: نوع الخط (solid, dashed, dotted)
            
        Returns:
            الإطار بعد إضافة الخط
        """
        if color is None:
            color = self.COLOR_BLUE
        
        if line_type == "solid":
            cv2.line(frame, start_pos, end_pos, color, thickness)
        elif line_type == "dashed":
            # رسم خط متقطع
            pts = self._bresenham_line(start_pos, end_pos)
            for i in range(0, len(pts), 2):
                if i + 1 < len(pts):
                    cv2.line(frame, pts[i], pts[i + 1], color, thickness)
        elif line_type == "dotted":
            # رسم نقاط
            pts = self._bresenham_line(start_pos, end_pos)
            for pt in pts[::3]:  # كل 3 نقاط
                cv2.circle(frame, pt, 1, color, thickness)
        
        return frame
    
    def add_text_annotation(self, frame: np.ndarray, text: str,
                           position: Tuple[int, int], color: Tuple = None,
                           font_size: float = 1.0, thickness: int = 2,
                           background: bool = True,
                           bg_color: Tuple = None) -> np.ndarray:
        """إضافة نص توضيحي على الإطار
        
        Args:
            frame: إطار الفيديو
            text: النص المراد كتابته
            position: موقع النص (x, y)
            color: لون النص (BGR)
            font_size: حجم الخط
            thickness: سمك الخط
            background: إضافة خلفية للنص
            bg_color: لون الخلفية
            
        Returns:
            الإطار بعد إضافة النص
        """
        if color is None:
            color = self.COLOR_WHITE
        if bg_color is None:
            bg_color = self.COLOR_BLACK
        
        # الحصول على حجم النص
        (text_width, text_height), baseline = cv2.getTextSize(
            text, self.font, font_size, thickness
        )
        
        # إضافة خلفية إذا لزم الأمر
        if background:
            x, y = position
            cv2.rectangle(
                frame,
                (x - 5, y - text_height - 5),
                (x + text_width + 5, y + baseline + 5),
                bg_color,
                -1
            )
        
        # كتابة النص
        cv2.putText(
            frame,
            text,
            position,
            self.font,
            font_size,
            color,
            thickness
        )
        
        return frame
    
    def add_underline(self, frame: np.ndarray, start_x: int, start_y: int,
                     end_x: int, end_y: int, color: Tuple = None,
                     thickness: int = 3, style: str = "solid") -> np.ndarray:
        """رسم تسطير (underline) تحت نص أو عنصر
        
        Args:
            frame: إطار الفيديو
            start_x: إحداثي X للبداية
            start_y: إحداثي Y للبداية
            end_x: إحداثي X للنهاية
            end_y: إحداثي Y للنهاية
            color: لون التسطير (BGR)
            thickness: سمك التسطير
            style: نمط التسطير (solid, wavy, double)
            
        Returns:
            الإطار بعد إضافة التسطير
        """
        if color is None:
            color = self.COLOR_YELLOW
        
        if style == "solid":
            cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)
        elif style == "wavy":
            # رسم خط متموج
            points = []
            for x in range(start_x, end_x, 10):
                y = int(start_y + 5 * np.sin((x - start_x) / 20))
                points.append((x, y))
            points = np.array(points, dtype=np.int32)
            cv2.polylines(frame, [points], False, color, thickness)
        elif style == "double":
            # رسم خطين
            cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)
            cv2.line(frame, (start_x, start_y + 4), (end_x, end_y + 4), color, thickness)
        
        return frame
    
    def add_animated_arrow(self, frames: List[np.ndarray], 
                          start_pos: Tuple[int, int],
                          end_pos: Tuple[int, int],
                          color: Tuple = None,
                          thickness: int = 3,
                          duration_frames: int = 10) -> List[np.ndarray]:
        """إضافة سهم متحرك يظهر تدريجياً
        
        Args:
            frames: قائمة الإطارات
            start_pos: موقع البداية
            end_pos: موقع النهاية
            color: لون السهم
            thickness: سمك السهم
            duration_frames: عدد الإطارات التي يستغرقها ظهور الس��م
            
        Returns:
            قائمة الإطارات بعد إضافة الأسهم المتحركة
        """
        if color is None:
            color = self.COLOR_RED
        
        # حساب الخطوات
        step_x = (end_pos[0] - start_pos[0]) / duration_frames
        step_y = (end_pos[1] - start_pos[1]) / duration_frames
        
        for i in range(min(duration_frames, len(frames))):
            current_end = (
                int(start_pos[0] + step_x * (i + 1)),
                int(start_pos[1] + step_y * (i + 1))
            )
            self.add_arrow(frames[i], start_pos, current_end, color, thickness)
        
        return frames
    
    def highlight_code_section(self, frame: np.ndarray, 
                               start_line: int, end_line: int,
                               line_height: int = 30,
                               x_offset: int = 50,
                               y_offset: int = 100,
                               color: Tuple = None) -> np.ndarray:
        """تظليل جزء معين من الكود (عدة أسطر)
        
        Args:
            frame: إطار الفيديو
            start_line: رقم السطر الأول
            end_line: رقم السطر الأخير
            line_height: ارتفاع كل سطر بالبكسل
            x_offset: المسافة من اليسار
            y_offset: المسافة من الأعلى
            color: لون التظليل
            
        Returns:
            الإطار بعد التظليل
        """
        if color is None:
            color = self.COLOR_PASTEL_YELLOW
        
        y_start = y_offset + (start_line * line_height)
        height = (end_line - start_line + 1) * line_height
        
        self.add_highlight_box(
            frame,
            x_offset,
            y_start,
            1820,  # عرض الإطار تقريباً
            height,
            color,
            thickness=0,
            fill=True,
            alpha=0.2
        )
        
        return frame
    
    def add_pointer(self, frame: np.ndarray, position: Tuple[int, int],
                   pointer_type: str = "finger", color: Tuple = None,
                   size: int = 20) -> np.ndarray:
        """إضافة مؤشر (pointer) على الإطار
        
        Args:
            frame: إطار الفيديو
            position: موقع المؤشر (x, y)
            pointer_type: نوع المؤشر (finger, arrow, dot, star)
            color: لون المؤشر
            size: حجم المؤشر
            
        Returns:
            الإطار بعد إضافة المؤشر
        """
        if color is None:
            color = self.COLOR_RED
        
        x, y = position
        
        if pointer_type == "finger":
            # رسم دائرة كبيرة مع نقطة في المنتصف
            cv2.circle(frame, position, size, color, 2)
            cv2.circle(frame, position, 3, color, -1)
        elif pointer_type == "arrow":
            # سهم صغير
            arrow_end = (x - size, y + size)
            self.add_arrow(frame, arrow_end, position, color, 2)
        elif pointer_type == "dot":
            # نقطة مضيئة
            cv2.circle(frame, position, size // 2, color, -1)
            cv2.circle(frame, position, size, color, 1)
        elif pointer_type == "star":
            # نجمة
            angles = np.linspace(0, 2 * np.pi, 5, endpoint=False)
            for i in range(5):
                angle1 = angles[i]
                angle2 = angles[(i + 1) % 5]
                x1 = int(x + size * np.cos(angle1))
                y1 = int(y + size * np.sin(angle1))
                x2 = int(x + size * np.cos(angle2))
                y2 = int(y + size * np.sin(angle2))
                cv2.line(frame, (x1, y1), (x2, y2), color, 2)
        
        return frame
    
    def add_gradient_background(self, frame: np.ndarray,
                               color1: Tuple = None,
                               color2: Tuple = None,
                               alpha: float = 0.3) -> np.ndarray:
        """إضافة خلفية متدرجة (gradient)
        
        Args:
            frame: إطار الفيديو
            color1: اللون الأول (BGR)
            color2: اللون الثاني (BGR)
            alpha: مستوى الشفافية
            
        Returns:
            الإطار بعد إضافة الخلفية
        """
        if color1 is None:
            color1 = self.COLOR_BLUE
        if color2 is None:
            color2 = self.COLOR_BLACK
        
        gradient = np.linspace(0, 1, self.frame_height)
        gradient = np.tile(gradient, (self.frame_width, 1)).T
        
        overlay = np.zeros_like(frame)
        for i in range(3):  # للقنوات الثلاث (BGR)
            overlay[:, :, i] = gradient * color1[i] + (1 - gradient) * color2[i]
        
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        return frame
    
    @staticmethod
    def _bresenham_line(p0: Tuple[int, int], p1: Tuple[int, int]) -> List[Tuple[int, int]]:
        """خوارزمية Bresenham لرسم خطوط بدقة
        
        Args:
            p0: النقطة الأولى
            p1: النقطة الثانية
            
        Returns:
            قائمة بالنقاط على الخط
        """
        points = []
        x0, y0 = p0
        x1, y1 = p1
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points


# الألوان الإضافية
AnnotationEngine.COLOR_PASTEL_YELLOW = (180, 220, 255)
AnnotationEngine.COLOR_PASTEL_PINK = (200, 150, 255)
AnnotationEngine.COLOR_PASTEL_CYAN = (255, 200, 100)
