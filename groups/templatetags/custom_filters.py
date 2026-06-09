from django import template
import json
import re


register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Dict dan qiymat olish"""
    if dictionary is None:
        return {}
    if isinstance(dictionary, dict):
        val = dictionary.get(key)
        if val is not None:
            return val
        return dictionary.get(str(key), {})
    return {}

@register.filter
def json_loads(value):
    """JSON stringni dict ga o'giradi"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except:
        return {}

@register.filter
def split_cloze_blanks(text):
    """
    Cloze matnini bo'sh joylarga ajratadi
    Masalan: "London is ___1___ city" 
    Natija: [{'text': 'London is ', 'blank_num': None}, {'text': None, 'blank_num': '1'}, {'text': ' city', 'blank_num': None}]
    """
    if not text:
        return []
    
    pattern = r'(___(\d+)___)'
    parts = []
    last_end = 0
    
    for match in re.finditer(pattern, text):
        start, end = match.span()
        blank_num = match.group(2)
        
        # Matn qismi (agar mavjud bo'lsa)
        if start > last_end:
            parts.append({'text': text[last_end:start], 'blank_num': None})
        
        # Bo'sh joy qismi
        parts.append({'text': None, 'blank_num': blank_num})
        last_end = end
    
    # Qolgan matn
    if last_end < len(text):
        parts.append({'text': text[last_end:], 'blank_num': None})
    
    # Agar hech qanday bo'sh joy topilmasa, butun matnni qaytarish
    if not parts:
        parts.append({'text': text, 'blank_num': None})
    
    return parts

@register.filter
def get_cloze_options(question, blank_num):
    """Cloze savoli uchun variantlarni olish"""
    if hasattr(question, 'blank_options') and question.blank_options:
        return question.blank_options.get(str(blank_num), [])
    return []

    from django import template
from ..models import StudentAudioPlay

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Dict dan qiymat olish"""
    if dictionary is None:
        return ''
    val = dictionary.get(key)
    if val is not None:
        return val
    return dictionary.get(str(key), '')

@register.filter
def get_audio_play(student, group_id):
    """Studentning audio eshitish ma'lumotlarini olish"""
    if not student or not group_id:
        return None
    try:
        return StudentAudioPlay.objects.filter(
            student=student, 
            group_id=group_id
        ).first()
    except:
        return None

@register.filter
def split_cloze_blanks(text):
    """Cloze matnini bo'sh joylarga ajratish"""
    import re
    if not text:
        return []
    
    parts = []
    pattern = r'(___\d+___)'
    split_text = re.split(pattern, text)
    
    for part in split_text:
        if part and part.startswith('___') and part.endswith('___'):
            blank_num = part.strip('_')
            parts.append({'blank_num': blank_num, 'text': None})
        else:
            if part:
                parts.append({'blank_num': None, 'text': part})
    
    return parts