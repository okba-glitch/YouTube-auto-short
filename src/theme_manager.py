"""
theme_manager.py - إدارة الألوان والمواضيع (Themes)

يوفر مجموعات لونية احترافية مختلفة للفيديو (Dark Mode, Light Mode, High Contrast).
يستخدم في render_engine.py لتطبيق الألوان على الكود والواجهة البصرية.
"""

from typing import Dict, Tuple, Optional
from enum import Enum


class ThemeName(Enum):
    """أسماء المواضيع المتاحة"""
    DARK_PROFESSIONAL = "dark_professional"
    LIGHT_CLEAN = "light_clean"
    HIGH_CONTRAST = "high_contrast"
    MONOKAI = "monokai"
    SOLARIZED_DARK = "solarized_dark"
    SOLARIZED_LIGHT = "solarized_light"
    GRUVBOX_DARK = "gruvbox_dark"
    NORD = "nord"
    DRACULA = "dracula"


class Color:
    """فئة لتمثيل الألوان (RGB و BGR)"""
    
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b
    
    @property
    def rgb(self) -> Tuple[int, int, int]:
        """الحصول على اللون بصيغة RGB"""
        return (self.r, self.g, self.b)
    
    @property
    def bgr(self) -> Tuple[int, int, int]:
        """الحصول على اللون بصيغة BGR (لـ OpenCV)"""
        return (self.b, self.g, self.r)
    
    @property
    def hex(self) -> str:
        """الحصول على اللون بصيغة HEX"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class Theme:
    """فئة تمثل موضوع (Theme) كامل"""
    
    def __init__(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        """
        Args:
            name: اسم الموضوع
            colors: قاموس الألوان {name: (r, g, b)}
        """
        self.name = name
        self.colors = colors
    
    def get_color(self, key: str, default: Tuple = None) -> Tuple[int, int, int]:
        """الحصول على لون محدد من الموضوع
        
        Args:
            key: اسم اللون
            default: لون افتراضي إذا لم يوجد
            
        Returns:
            الكود اللوني (BGR)
        """
        return self.colors.get(key, default or (255, 255, 255))


class ThemeManager:
    """مدير المواضيع والألوان"""
    
    # ============================================================
    # DARK PROFESSIONAL - Theme احترافي مظلم
    # ============================================================
    DARK_PROFESSIONAL = Theme(
        "Dark Professional",
        {
            "background": (15, 23, 42),           # Dark blue-gray
            "code_background": (30, 41, 59),     # Slightly lighter
            "text": (229, 231, 235),             # Light gray
            "keyword": (102, 217, 239),          # Cyan blue
            "string": (167, 243, 208),           # Mint green
            "number": (253, 230, 125),           # Golden yellow
            "comment": (113, 128, 150),          # Gray-blue
            "function": (198, 160, 246),         # Purple
            "class": (248, 113, 113),            # Red
            "success": (34, 197, 94),            # Green
            "error": (239, 68, 68),              # Red
            "warning": (245, 158, 11),           # Orange
            "info": (59, 130, 246),              # Blue
            "highlight": (251, 191, 36),         # Amber
            "cursor": (251, 146, 60),            # Orange cursor
            "selection": (59, 130, 246),         # Blue selection
        }
    )
    
    # ============================================================
    # LIGHT CLEAN - Theme نظيف فاتح
    # ============================================================
    LIGHT_CLEAN = Theme(
        "Light Clean",
        {
            "background": (255, 255, 255),       # White
            "code_background": (245, 245, 250), # Very light blue
            "text": (15, 23, 42),                # Dark gray-blue
            "keyword": (6, 32, 173),             # Dark blue
            "string": (34, 138, 97),             # Forest green
            "number": (193, 132, 1),             # Brown
            "comment": (100, 116, 139),          # Gray
            "function": (88, 28, 135),           # Dark purple
            "class": (159, 0, 0),                # Dark red
            "success": (22, 163, 74),            # Dark green
            "error": (220, 38, 38),              # Dark red
            "warning": (217, 119, 6),            # Dark orange
            "info": (37, 99, 235),               # Dark blue
            "highlight": (245, 158, 11),         # Amber
            "cursor": (15, 23, 42),              # Dark cursor
            "selection": (219, 234, 254),        # Light blue
        }
    )
    
    # ============================================================
    # HIGH CONTRAST - Theme عالي التباين (للوضوح الأقصى)
    # ============================================================
    HIGH_CONTRAST = Theme(
        "High Contrast",
        {
            "background": (0, 0, 0),             # Pure black
            "code_background": (20, 20, 20),    # Very dark gray
            "text": (255, 255, 255),             # Pure white
            "keyword": (0, 255, 255),            # Cyan
            "string": (0, 255, 0),               # Lime green
            "number": (255, 255, 0),             # Yellow
            "comment": (128, 128, 128),          # Medium gray
            "function": (255, 0, 255),           # Magenta
            "class": (255, 0, 0),                # Pure red
            "success": (0, 255, 0),              # Pure green
            "error": (255, 0, 0),                # Pure red
            "warning": (255, 165, 0),            # Orange
            "info": (0, 0, 255),                 # Pure blue
            "highlight": (255, 255, 0),          # Yellow
            "cursor": (255, 255, 255),           # White cursor
            "selection": (128, 0, 255),          # Purple
        }
    )
    
    # ============================================================
    # MONOKAI - Theme محبوب بين المبرمجين
    # ============================================================
    MONOKAI = Theme(
        "Monokai",
        {
            "background": (39, 40, 34),          # Very dark gray
            "code_background": (39, 40, 34),    # Same as background
            "text": (248, 248, 242),             # Off-white
            "keyword": (249, 38, 114),           # Magenta
            "string": (230, 219, 116),           # Yellow
            "number": (174, 129, 255),           # Purple
            "comment": (117, 113, 94),           # Gray
            "function": (166, 226, 46),          # Green
            "class": (253, 151, 31),             # Orange
            "success": (166, 226, 46),           # Green
            "error": (249, 38, 114),             # Magenta/Red
            "warning": (253, 151, 31),           # Orange
            "info": (102, 217, 239),             # Cyan
            "highlight": (230, 219, 116),        # Yellow
            "cursor": (248, 248, 242),           # Off-white
            "selection": (73, 72, 62),           # Dark gray
        }
    )
    
    # ============================================================
    # SOLARIZED DARK - Theme محترم وسهل للعين
    # ============================================================
    SOLARIZED_DARK = Theme(
        "Solarized Dark",
        {
            "background": (7, 54, 66),           # Dark blue-green
            "code_background": (0, 43, 54),     # Darker
            "text": (131, 148, 150),             # Gray-green
            "keyword": (38, 139, 210),           # Blue
            "string": (42, 161, 152),            # Teal
            "number": (181, 137, 0),             # Yellow
            "comment": (88, 110, 117),           # Gray
            "function": (133, 153, 0),           # Green
            "class": (268, 102, 66),             # Orange
            "success": (133, 153, 0),            # Green
            "error": (220, 50, 47),              # Red
            "warning": (268, 102, 66),           # Orange
            "info": (38, 139, 210),              # Blue
            "highlight": (181, 137, 0),          # Yellow
            "cursor": (131, 148, 150),           # Gray-green
            "selection": (7, 102, 120),          # Darker teal
        }
    )
    
    # ============================================================
    # SOLARIZED LIGHT - نسخة فاتحة من Solarized
    # ============================================================
    SOLARIZED_LIGHT = Theme(
        "Solarized Light",
        {
            "background": (253, 246, 227),       # Very light yellow
            "code_background": (238, 232, 213), # Light beige
            "text": (101, 123, 131),             # Dark gray
            "keyword": (38, 139, 210),           # Blue
            "string": (42, 161, 152),            # Teal
            "number": (181, 137, 0),             # Yellow
            "comment": (147, 161, 161),          # Gray
            "function": (133, 153, 0),           # Green
            "class": (268, 102, 66),             # Orange
            "success": (133, 153, 0),            # Green
            "error": (220, 50, 47),              # Red
            "warning": (268, 102, 66),           # Orange
            "info": (38, 139, 210),              # Blue
            "highlight": (181, 137, 0),          # Yellow
            "cursor": (101, 123, 131),           # Dark gray
            "selection": (218, 237, 240),        # Light cyan
        }
    )
    
    # ============================================================
    # GRUVBOX DARK - Theme دافئ وقديم المظهر
    # ============================================================
    GRUVBOX_DARK = Theme(
        "Gruvbox Dark",
        {
            "background": (40, 40, 40),          # Very dark gray
            "code_background": (50, 48, 47),    # Slightly lighter
            "text": (235, 219, 178),             # Light beige
            "keyword": (131, 165, 152),          # Green-gray
            "string": (184, 187, 38),            # Olive-green
            "number": (215, 153, 33),            # Orange
            "comment": (168, 153, 132),          # Gray-brown
            "function": (142, 192, 124),         # Light green
            "class": (249, 100, 65),             # Orange-red
            "success": (184, 187, 38),           # Green
            "error": (251, 73, 52),              # Red
            "warning": (249, 100, 65),           # Orange
            "info": (131, 165, 152),             # Teal
            "highlight": (184, 187, 38),         # Olive
            "cursor": (235, 219, 178),           # Light beige
            "selection": (80, 73, 70),           # Dark brown
        }
    )
    
    # ============================================================
    # NORD - Theme بارد وهادئ (Arctic, north-bluish)
    # ============================================================
    NORD = Theme(
        "Nord",
        {
            "background": (46, 52, 64),          # Polar night
            "code_background": (36, 41, 51),    # Darker polar
            "text": (216, 222, 233),             # Snow storm
            "keyword": (136, 192, 208),          # Frost
            "string": (163, 190, 140),           # Aurora green
            "number": (191, 144, 0),             # Aurora yellow
            "comment": (76, 86, 106),            # Polar night
            "function": (143, 188, 187),         # Aurora cyan
            "class": (191, 97, 106),             # Aurora red
            "success": (163, 190, 140),          # Green
            "error": (191, 97, 106),             # Red
            "warning": (235, 203, 139),          # Yellow
            "info": (136, 192, 208),             # Blue
            "highlight": (235, 203, 139),        # Yellow
            "cursor": (216, 222, 233),           # Snow
            "selection": (76, 86, 106),          # Polar night
        }
    )
    
    # ============================================================
    # DRACULA - Theme حديث وشهير جداً
    # ============================================================
    DRACULA = Theme(
        "Dracula",
        {
            "background": (40, 42, 54),          # Dark background
            "code_background": (40, 42, 54),    # Same as background
            "text": (248, 248, 242),             # Foreground
            "keyword": (189, 147, 249),          # Purple
            "string": (165, 142, 251),           # Cyan-purple
            "number": (189, 147, 249),           # Purple
            "comment": (98, 114, 164),           # Comment
            "function": (80, 250, 123),          # Green
            "class": (255, 121, 198),            # Pink
            "success": (80, 250, 123),           # Green
            "error": (255, 121, 198),            # Pink
            "warning": (241, 250, 140),          # Yellow
            "info": (139, 233, 253),             # Cyan
            "highlight": (255, 184, 108),        # Orange
            "cursor": (248, 248, 242),           # Foreground
            "selection": (68, 71, 90),           # Selection
        }
    )
    
    # قائمة جميع المواضيع المتاحة
    ALL_THEMES = {
        ThemeName.DARK_PROFESSIONAL.value: DARK_PROFESSIONAL,
        ThemeName.LIGHT_CLEAN.value: LIGHT_CLEAN,
        ThemeName.HIGH_CONTRAST.value: HIGH_CONTRAST,
        ThemeName.MONOKAI.value: MONOKAI,
        ThemeName.SOLARIZED_DARK.value: SOLARIZED_DARK,
        ThemeName.SOLARIZED_LIGHT.value: SOLARIZED_LIGHT,
        ThemeName.GRUVBOX_DARK.value: GRUVBOX_DARK,
        ThemeName.NORD.value: NORD,
        ThemeName.DRACULA.value: DRACULA,
    }
    
    @classmethod
    def get_theme(cls, theme_name: str = "dark_professional") -> Theme:
        """الحصول على موضوع محدد
        
        Args:
            theme_name: اسم الموضوع
            
        Returns:
            كائن Theme
        """
        return cls.ALL_THEMES.get(theme_name.lower(), cls.DARK_PROFESSIONAL)
    
    @classmethod
    def list_available_themes(cls) -> list:
        """الحصول على قائمة بأسماء جميع المواضيع المتاحة"""
        return list(cls.ALL_THEMES.keys())
    
    @classmethod
    def get_default_theme(cls) -> Theme:
        """الحصول على الموضوع الافتراضي (Dark Professional)"""
        return cls.DARK_PROFESSIONAL
