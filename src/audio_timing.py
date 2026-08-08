"""
audio_timing.py - مزامنة الصوت والفيديو (Audio-Video Sync)

يضمن توافق دقيق بين الكود الظاهر على الشاشة وسرعة الراوي.
يحسب توقيت ظهور سطور الكود بناءً على نطق الراوي.
"""

import json
from typing import List, Dict, Tuple, Optional
from src.logger import Logger


class AudioTiming:
    """فئة لمعالجة التوقيت الصوتي ومزامنة الكود"""
    
    def __init__(self, narration: str, audio_duration_seconds: float, 
                 words_per_minute: int = 150):
        """
        Args:
            narration: نص الشرح الكامل
            audio_duration_seconds: مدة الملف الصوتي بالثواني
            words_per_minute: سرعة الراوي (كلمة/دقيقة)
        """
        self.narration = narration
        self.audio_duration_seconds = audio_duration_seconds
        self.words_per_minute = words_per_minute
        self.words = narration.split()
        self.word_count = len(self.words)
        
        # حساب وقت كل كلمة
        if self.word_count > 0:
            self.time_per_word = audio_duration_seconds / self.word_count
        else:
            self.time_per_word = 0
    
    def get_word_timing(self, word_index: int) -> float:
        """الحصول على وقت نطق كلمة معينة
        
        Args:
            word_index: فهرس الكلمة في النص
            
        Returns:
            الوقت بالثواني
        """
        if word_index < 0 or word_index >= self.word_count:
            return 0.0
        return word_index * self.time_per_word
    
    def get_phrase_timing(self, phrase: str) -> Tuple[float, float]:
        """الحصول على وقت بداية ونهاية عبارة معينة
        
        Args:
            phrase: العبارة المراد العثور على توقيتها
            
        Returns:
            (start_time, end_time) بالثواني
        """
        narration_lower = self.narration.lower()
        phrase_lower = phrase.lower()
        
        start_index = narration_lower.find(phrase_lower)
        if start_index == -1:
            return (0.0, 0.0)
        
        # حساب عدد الكلمات قبل العبارة
        words_before = self.narration[:start_index].split()
        start_word_index = len(words_before)
        
        # حساب عدد الكلمات في العبارة
        phrase_words = phrase.split()
        phrase_word_count = len(phrase_words)
        
        start_time = self.get_word_timing(start_word_index)
        end_time = self.get_word_timing(start_word_index + phrase_word_count)
        
        return (start_time, end_time)
    
    def get_code_line_timing(self, code_lines: List[str]) -> List[Dict]:
        """حساب وقت ظهور كل سطر من الكود
        
        يفترض أن الراوي يشرح الكود سطر بسطر بترتيب متسلسل.
        
        Args:
            code_lines: قائمة أسطر الكود
            
        Returns:
            قائمة بقاموس يحتوي على {line, start_time, end_time, duration}
        """
        timing_data = []
        segment_duration = self.audio_duration_seconds / len(code_lines)
        
        for i, line in enumerate(code_lines):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            timing_data.append({
                "line_index": i,
                "code": line,
                "start_time": start_time,
                "end_time": end_time,
                "duration": segment_duration
            })
        
        return timing_data
    
    def sync_narration_to_code(self, code_sections: List[str], 
                               narration_segments: List[str]) -> List[Dict]:
        """مزامنة أجزاء الشرح مع أجزاء الكود
        
        Args:
            code_sections: أجزاء الكود
            narration_segments: أجزاء الشرح
            
        Returns:
            قائمة بالأجزاء المزامنة
        """
        synced = []
        total_segments = len(narration_segments)
        
        if total_segments == 0:
            return []
        
        segment_duration = self.audio_duration_seconds / total_segments
        
        for i, narration_segment in enumerate(narration_segments):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            
            # اختيار جزء الكود المناسب
            code_index = min(i, len(code_sections) - 1)
            code_section = code_sections[code_index] if code_sections else ""
            
            synced.append({
                "segment_index": i,
                "narration": narration_segment,
                "code": code_section,
                "start_time": start_time,
                "end_time": end_time,
                "duration": segment_duration
            })
        
        return synced
    
    def calculate_typing_speed(self, code_section: str, 
                              time_window: float) -> float:
        """حساب سرعة الكتابة المناسبة للكود
        
        Args:
            code_section: جزء الكود
            time_window: النافذة الزمنية المتاحة (بالثواني)
            
        Returns:
            سرعة الكتابة (حروف/ثانية)
        """
        char_count = len(code_section)
        if time_window <= 0:
            return 10.0  # قيمة افتراضية
        return char_count / time_window
    
    def export_timing_to_json(self, timing_data: List[Dict], 
                             filepath: str) -> bool:
        """تصدير بيانات التوقيت إلى ملف JSON
        
        Args:
            timing_data: بيانات التوقيت
            filepath: مسار الملف
            
        Returns:
            True إذا نجح، False خلاف ذلك
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(timing_data, f, indent=2, ensure_ascii=False)
            Logger.success(f"Timing data exported to {filepath}")
            return True
        except Exception as e:
            Logger.error(f"Failed to export timing data: {e}")
            return False


class SpeechRateEstimator:
    """فئة لتقدير سرعة الكلام من الملف الصوتي"""
    
    @staticmethod
    def estimate_from_duration(word_count: int, duration_seconds: float) -> int:
        """تقدير كلمات في الدقيقة من عدد الكلمات والمدة
        
        Args:
            word_count: عدد الكلمات
            duration_seconds: المدة الكلية (بالثواني)
            
        Returns:
            كلمات في الدقيقة (WPM)
        """
        if duration_seconds <= 0:
            return 150  # قيمة افتراضية
        
        minutes = duration_seconds / 60
        wpm = int(word_count / minutes)
        return wpm
    
    @staticmethod
    def classify_speed(wpm: int) -> str:
        """تصنيف سرعة الكلام
        
        Args:
            wpm: كلمات في الدقيقة
            
        Returns:
            تصنيف السرعة (slow, normal, fast, very_fast)
        """
        if wpm < 100:
            return "slow"
        elif wpm < 150:
            return "normal"
        elif wpm < 200:
            return "fast"
        else:
            return "very_fast"
