# models.py
from django.db import models
from django.contrib.auth.models import User
import json
import re


class QuestionType(models.TextChoices):
    FILL_BLANK = 'fill_blank', "Bo'sh joy to'ldirish (Word Bank)"
    FILL_BLANK_NO_WORD = 'fill_blank_no_word', "Bo'sh joy to'ldirish (Variantlarsiz)"
    SENTENCE_ARRANGEMENT = 'sentence_arrangement', "So'zlarni tartibga solish"
    MULTIPLE_CHOICE = 'multiple_choice', "Test varianti"
    TRUE_FALSE = 'true_false', "To'g'ri/Noto'g'ri"
    READING_COMPREHENSION = 'reading_comprehension', "Matn asosida savol"
    UNDERLINE_CORRECT = 'underline_correct', "To'g'ri so'zni tanlash"
    MATCHING = 'matching', "Moslashtirish"
    CLOZE_MULTIPLE_BLANKS = 'cloze_multiple_blanks', "Matn ichidagi bo'sh joylar"
    COMPLETE_THE_WORDS = 'complete_the_words', "So'zlarni to'ldirish (birinchi harf berilgan)"
    WRITING = 'writing', "Yozma ish (Writing)"
    SPEAKING = 'speaking', "Og'zaki (Speaking)"


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Guruh nomi")
    teacher = models.CharField(max_length=200, verbose_name="O'qituvchi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students', verbose_name="Guruh"
    )
    is_archived = models.BooleanField(default=False, verbose_name="Arxivlangan")
    rules_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Qoidalarni qabul qilgan vaqt")

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.user.get_full_name() if self.user.get_full_name() else self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    # Audio sozlamalari
    audio_file = models.FileField(
        upload_to='category_audio/', blank=True, null=True,
        verbose_name="Kategoriya audio fayli"
    )
    max_audio_plays = models.IntegerField(
        default=1,
        verbose_name="Audio necha marta eshitilishi mumkin (0=cheksiz)"
    )
    audio_instruction = models.TextField(
        blank=True, null=True,
        verbose_name="Audio uchun qo'shimcha ko'rsatma"
    )

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Folder(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Papka nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Papka"
        verbose_name_plural = "Papkalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class FolderCategory(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_folders')

    class Meta:
        verbose_name = "Papka kategoriyasi"
        verbose_name_plural = "Papka kategoriyalari"
        unique_together = ['folder', 'category']

    def __str__(self):
        return f"{self.folder.name} - {self.category.name}"


class GroupFolder(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_folders')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_groups')
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Guruh papkasi"
        verbose_name_plural = "Guruh papkalari"
        unique_together = ['group', 'folder']

    def __str__(self):
        return f"{self.group.name} - {self.folder.name}"


class FolderGroupConfig(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_group_configs')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='folder_configs')
    categories_to_select = models.IntegerField(default=1, verbose_name="Tanlanadigan kategoriyalar soni")
    randomize_categories = models.BooleanField(default=True, verbose_name="Random tanlash")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Papka guruh sozlamasi"
        verbose_name_plural = "Papka guruh sozlamalari"
        unique_together = ['folder', 'group']

    def __str__(self):
        return f"{self.folder.name} -> {self.group.name} ({self.categories_to_select} kategoriya)"


class GroupCategory(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_categories')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='group_categories')
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Guruh kategoriyasi"
        verbose_name_plural = "Guruh kategoriyalari"
        unique_together = ['group', 'category']

    def __str__(self):
        return f"{self.group.name} - {self.category.name}"


class ReadingText(models.Model):
    title = models.CharField(max_length=200, verbose_name="Matn sarlavhasi")
    content = models.TextField(verbose_name="Matn mazmuni")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='reading_texts', verbose_name="Kategoriya"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Matn"
        verbose_name_plural = "Matnlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ReadingQuestion(models.Model):
    """Matnga oid savollar"""
    reading_text = models.ForeignKey(
        ReadingText, on_delete=models.CASCADE,
        # MUHIM: related_name ikki joyda ham mos kelishi kerak
        related_name='reading_questions',
        verbose_name="Matn"
    )
    question_text = models.TextField(verbose_name="Savol matni")
    correct_answer = models.CharField(max_length=500, verbose_name="To'g'ri javob")
    order = models.IntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Matn savoli"
        verbose_name_plural = "Matn savollari"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.reading_text.title} - {self.question_text[:50]}"


class QuizQuestion(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='quiz_questions', verbose_name="Kategoriya")
    question_type = models.CharField(max_length=30, choices=QuestionType.choices, default=QuestionType.FILL_BLANK, verbose_name="Savol turi")
    question_text = models.TextField(verbose_name="Savol matni", blank=True, null=True)
    correct_answer = models.TextField(max_length=2000, verbose_name="To'g'ri javob", blank=True, null=True)
    scrambled_words = models.TextField(blank=True, null=True, verbose_name="Chalkashtirilgan so'zlar / Variantlar / Matching data")
    correct_sentence = models.TextField(blank=True, null=True, verbose_name="To'g'ri gap")
    reading_text = models.ForeignKey('ReadingText', on_delete=models.CASCADE, null=True, blank=True, related_name='quiz_questions', verbose_name="Matn")
    blank_options = models.JSONField(default=dict, blank=True, null=True, verbose_name="Bo'sh joy variantlari")
    blank_positions = models.JSONField(default=dict, blank=True, null=True, verbose_name="Bo'sh joy pozitsiyalari")
    points = models.IntegerField(default=1, verbose_name="Ball")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['category__name', 'id']

    def __str__(self):
        if self.question_type == 'reading_comprehension' and self.reading_text:
            return f"[{self.category.name}] Matn: {self.reading_text.title}"
        if self.question_type == 'sentence_arrangement':
            words = self.get_scrambled_words_list()
            return f"[{self.category.name}] So'z tartib: {' '.join(words[:3])}..."
        text = self.question_text or "Savol"
        return f"[{self.category.name}] {text[:50]}..."

    # =========================================================
    # SENTENCE ARRANGEMENT
    # =========================================================
    def get_scrambled_words_list(self):
        """Sentence arrangement uchun so'zlar ro'yxatini qaytaradi"""
        if not self.scrambled_words:
            return []
        
        # JSON formatda saqlangan bo'lsa
        try:
            data = json.loads(self.scrambled_words)
            if isinstance(data, list):
                return data
        except:
            pass
        
        # / bilan ajratilgan bo'lsa
        if '/' in self.scrambled_words:
            words = [w.strip() for w in self.scrambled_words.split('/') if w.strip()]
            if words:
                return words
        
        # Bo'sh joy bilan ajratilgan bo'lsa
        words = self.scrambled_words.split()
        if words:
            return words
        
        return []

    def get_correct_sentence_list(self):
        """To'g'ri gapni so'zlar ro'yxati sifatida qaytaradi"""
        if self.correct_sentence:
            return self.correct_sentence.split()
        return self.get_scrambled_words_list()

    def save(self, *args, **kwargs):
        """Saqlashdan oldin correct_sentence ni so'zlardan yig'ish"""
        if self.question_type == 'sentence_arrangement' and self.scrambled_words and not self.correct_sentence:
            words = self.get_scrambled_words_list()
            self.correct_sentence = ' '.join(words)
        super().save(*args, **kwargs)

    # =========================================================
    # FILL BLANK - WORD BANK UCHUN
    # =========================================================
    def get_options_list(self):
        """Fill blank uchun variantlarni qaytaradi (Word Bank so'zlari)"""
        options = []
        
        if self.question_type == 'fill_blank':
            # 1. scrambled_words dan olish (JSON format)
            if self.scrambled_words:
                try:
                    data = json.loads(self.scrambled_words)
                    if isinstance(data, list):
                        return data
                except:
                    pass
            
            # 2. scrambled_words dan / bilan ajratilgan holda
            if self.scrambled_words and '/' in self.scrambled_words:
                options = [opt.strip() for opt in self.scrambled_words.split('/') if opt.strip()]
                if options:
                    return options
            
            # 3. correct_answer dan olish
            if self.correct_answer:
                if '|' in self.correct_answer:
                    options = [opt.strip() for opt in self.correct_answer.split('|') if opt.strip()]
                    if options:
                        return options
                else:
                    return [self.correct_answer.strip()]
            
            # 4. Agar hech narsa bo'lmasa, question_text dan blankdan keyingi so'zni olish
            if self.question_text:
                match = re.search(r'_{3,}\s*(\w+)', self.question_text)
                if match:
                    return [match.group(1)]
        
        elif self.question_type == 'multiple_choice':
            if self.scrambled_words:
                try:
                    options = json.loads(self.scrambled_words)
                    if isinstance(options, list):
                        return options
                except:
                    if '|' in self.scrambled_words:
                        return [opt.strip() for opt in self.scrambled_words.split('|') if opt.strip()]
                    return [self.scrambled_words]
        
        return options

    # =========================================================
    # UNDERLINE CORRECT
    # =========================================================
    def get_underline_options(self):
        if self.question_type != 'underline_correct':
            return []
        if self.scrambled_words:
            try:
                data = json.loads(self.scrambled_words)
                if isinstance(data, list):
                    return data
            except:
                pass
        if self.scrambled_words and '/' in self.scrambled_words:
            return [opt.strip() for opt in self.scrambled_words.split('/') if opt.strip()]
        if self.question_text and '/' in self.question_text:
            text = self.question_text
            slash_index = text.find('/')
            before = text[:slash_index].strip().split()
            after = text[slash_index + 1:].strip().split()
            left = before[-1] if before else ''
            right = after[0] if after else ''
            return [left, right]
        return []

    # =========================================================
    # MATCHING
    # =========================================================
    def get_matching_left_items(self):
        if self.question_type == 'matching' and self.scrambled_words:
            try:
                data = json.loads(self.scrambled_words)
                return data.get('left', [])
            except:
                return []
        return []

    def get_matching_right_items(self):
        if self.question_type == 'matching' and self.scrambled_words:
            try:
                data = json.loads(self.scrambled_words)
                return data.get('right', [])
            except:
                return []
        return []

    def get_matching_correct_answers(self):
        if self.question_type == 'matching' and self.correct_answer:
            try:
                return json.loads(self.correct_answer)
            except:
                return {}
        return {}

    # =========================================================
    # CLOZE
    # =========================================================
    def get_cloze_blanks(self):
        if self.question_type == 'cloze_multiple_blanks' and self.question_text:
            blanks = re.findall(r'___(\d+)___', self.question_text)
            return sorted(set(blanks), key=int)
        return []

    def get_cloze_blank_options(self, blank_num):
        if self.blank_options:
            return self.blank_options.get(str(blank_num), [])
        return []

    def get_cloze_correct_answers(self):
        if self.question_type != 'cloze_multiple_blanks' or not self.correct_answer:
            return {}
        try:
            result = json.loads(self.correct_answer)
            if isinstance(result, dict):
                return result
        except:
            pass
        return {}

    def get_cloze_text_with_selects(self):
        if self.question_type != 'cloze_multiple_blanks':
            return self.question_text or ""
        text = self.question_text or ""
        def replace_match(match):
            blank_num = match.group(1)
            options = self.get_cloze_blank_options(blank_num)
            name_attr = f'q_{self.id}_blank_{blank_num}'
            if options:
                options_html = '<option value="">-- Tanlang --</option>'
                for opt in options:
                    options_html += f'<option value="{opt}">{opt}</option>'
                return f'<select name="{name_attr}" class="cloze-select border border-gray-300 px-2 py-1 mx-1" data-blank="{blank_num}">{options_html}</select>'
            return f'<input type="text" name="{name_attr}" class="cloze-input border border-gray-300 px-2 py-1 mx-1 w-32" data-blank="{blank_num}" placeholder="___{blank_num}___" autocomplete="off">'
        return re.sub(r'___(\d+)___', replace_match, text)

    # =========================================================
    # COMPLETE THE WORDS
    # =========================================================
    def get_complete_words_blanks(self):
        if self.question_type != 'complete_the_words' or not self.question_text:
            return {}
        blanks = {}
        pattern = r'([a-zA-Z]*)_{3,}'
        matches = list(re.finditer(pattern, self.question_text))
        for idx, match in enumerate(matches, 1):
            prefix = match.group(1) if match.group(1) else ''
            blanks[str(idx)] = {
                'prefix': prefix.lower(),
                'full_match': match.group(0),
                'start_pos': match.start(),
                'end_pos': match.end()
            }
        if not blanks:
            matches2 = list(re.finditer(r'_{3,}', self.question_text))
            for idx, match in enumerate(matches2, 1):
                blanks[str(idx)] = {
                    'prefix': '',
                    'full_match': match.group(0),
                    'start_pos': match.start(),
                    'end_pos': match.end()
                }
        return blanks

    def get_complete_words_answers(self):
        if self.question_type != 'complete_the_words' or not self.correct_answer:
            return {}
        result = {}
        if ',' in self.correct_answer:
            parts = [p.strip() for p in self.correct_answer.split(',') if p.strip()]
            for idx, part in enumerate(parts, 1):
                result[str(idx)] = part
        else:
            result["1"] = self.correct_answer.strip()
        return result

    # =========================================================
    # INLINE INPUTS
    # =========================================================
    def get_question_text_with_inline_inputs(self, user_answer=None, question_type_override=None):
        text = self.question_text or ""
        q_type = question_type_override or self.question_type

        if q_type == 'complete_the_words':
            blanks = self.get_complete_words_blanks()
            if blanks:
                for blank_num, blank_info in blanks.items():
                    prefix = blank_info.get('prefix', '')
                    full_match = blank_info.get('full_match', '___')
                    value = ''
                    if isinstance(user_answer, dict):
                        value = user_answer.get(blank_num, '')
                    elif isinstance(user_answer, str):
                        value = user_answer
                    input_html = f'<input type="text" name="q_{self.id}_blank_{blank_num}" class="inline-blank-input complete-word-input" value="{value}" placeholder="{prefix}..." autocomplete="off" data-blank-num="{blank_num}" style="min-width: 80px;">'
                    if prefix:
                        text = text.replace(full_match, f'<span class="inline-flex items-center gap-1"><span>{prefix}</span>{input_html}</span>', 1)
                    else:
                        text = text.replace(full_match, input_html, 1)
                return text

        if q_type == 'reading_comprehension' and self.reading_text:
            return text

        if q_type in ['fill_blank', 'fill_blank_no_word']:
            blanks = re.findall(r'_{3,}', text)
            if len(blanks) == 1:
                value = user_answer if isinstance(user_answer, str) else ''
                return re.sub(
                    r'_{3,}',
                    f'<input type="text" name="q_{self.id}" class="inline-blank-input" value="{value}" placeholder="___" autocomplete="off">',
                    text,
                    count=1
                )
            elif len(blanks) > 1:
                for i, blank in enumerate(blanks):
                    value = user_answer.get(str(i), '') if isinstance(user_answer, dict) else ''
                    text = text.replace(blank, f'<input type="text" name="q_{self.id}_blank_{i}" class="inline-blank-input" value="{value}" placeholder="___{i+1}___" size="12" autocomplete="off">', 1)
                return text

        return text

    @property
    def blank_text(self):
        return self.question_text


class QuizSession(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Quiz sessiyasi"
        verbose_name_plural = "Quiz sessiyalari"

    def __str__(self):
        return f"{self.group.name if self.group else 'O\'chirilgan'} - {'Faol' if self.is_active else 'Tugagan'}"


class QuizResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='quiz_results')
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='results')
    score = models.FloatField(default=0, verbose_name="Ball (0-100)")
    total_questions = models.IntegerField(default=0, verbose_name="Jami savollar")
    answers = models.JSONField(default=dict, verbose_name="Javoblar")
    submitted_at = models.DateTimeField(auto_now_add=True)
    attempt_number = models.IntegerField(default=1, verbose_name="Urinish raqami")
    student_name_saved = models.CharField(max_length=200, blank=True, verbose_name="Student nomi (saqlangan)")
    group_name_saved = models.CharField(max_length=100, blank=True, verbose_name="Guruh nomi (saqlangan)")

    class Meta:
        verbose_name = "Quiz natijasi"
        verbose_name_plural = "Quiz natijalari"
        ordering = ['-submitted_at']

    def __str__(self):
        name = self.student_name_saved or (self.student.full_name if self.student else 'Noma\'lum')
        return f"{name} - {self.score}/100 (#{self.attempt_number})"

    @property
    def percentage(self):
        return self.score  # 0-100 oralig'ida

class UserExamAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_attempts')
    exam_session = models.ForeignKey(
        QuizSession, on_delete=models.CASCADE,
        related_name='attempts', null=True, blank=True
    )
    selected_questions = models.JSONField(default=list, verbose_name="Tanlangan savollar")
    user_answers = models.JSONField(default=dict, blank=True, verbose_name="Foydalanuvchi javoblari")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    attempt_number = models.IntegerField(default=1, verbose_name="Urinish raqami")

    class Meta:
        verbose_name = "Imtihon urinishi"
        verbose_name_plural = "Imtihon urinishlari"
        ordering = ['-started_at']

    def __str__(self):
        status = "Tugallangan" if self.is_completed else "Jarayonda"
        name = self.student.full_name if self.student else 'Noma\'lum'
        return f"{name} - #{self.attempt_number} - {status}"
















class ExamControl(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='exam_control')
    is_active = models.BooleanField(default=False)
    is_paused = models.BooleanField(default=False)  # <-- BU MAYDON BO'LISHI KERAK
    started_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    elapsed_time = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Imtihon boshqaruvi"
        verbose_name_plural = "Imtihon boshqaruvlari"








class ExamSession(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_sessions')
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exams')

    class Meta:
        verbose_name = "Imtihon sessiyasi"
        verbose_name_plural = "Imtihon sessiyalari"

    def __str__(self):
        return f"{self.group.name if self.group else 'O\'chirilgan'} - {'Faol' if self.is_active else 'Tugagan'}"


class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_results')
    exam_session = models.ForeignKey(ExamSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='results')
    score = models.IntegerField(default=0)
    answers = models.JSONField(default=dict)
    submitted_at = models.DateTimeField(auto_now_add=True)
    student_name_saved = models.CharField(max_length=200, blank=True, verbose_name="Student nomi (saqlangan)")
    group_name_saved = models.CharField(max_length=100, blank=True, verbose_name="Guruh nomi (saqlangan)")

    class Meta:
        verbose_name = "Imtihon natijasi"
        verbose_name_plural = "Imtihon natijalari"


class AdminPassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_password')
    plain_password = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admin paroli"
        verbose_name_plural = "Admin parollari"

    def __str__(self):
        return f"{self.user.username} - Parol"


class Rules(models.Model):
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Video URL")
    video_file = models.FileField(upload_to='rules_videos/', blank=True, null=True, verbose_name="Video fayl")
    image1 = models.ImageField(upload_to='rules_images/', blank=True, null=True, verbose_name="Rasm 1")
    image1_title = models.CharField(max_length=200, blank=True, default="Imtihon tartibi")
    image1_description = models.TextField(blank=True, default="Imtihon vaqtida nimalarga e'tibor berish kerak")
    image2 = models.ImageField(upload_to='rules_images/', blank=True, null=True, verbose_name="Rasm 2")
    image2_title = models.CharField(max_length=200, blank=True, default="Baholash mezonlari")
    image2_description = models.TextField(blank=True, default="Qanday qilib yuqori ball olish mumkin")
    rules_text = models.TextField(default="""1. Telefon va qurilmalardan foydalanish QAT'IY MAN ETILADI
2. Belgilangan vaqtda topshirish shart
3. Ko'chirish qat'iyan man etiladi
4. Texnik muammoda o'qituvchiga murojaat qiling
5. Natijalar tekshiruvdan keyin e'lon qilinadi""")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Qonun va qoidalar"
        verbose_name_plural = "Qonun va qoidalar"

    def __str__(self):
        return "Qonun va qoidalar"

    def get_video_url(self):
        if self.video_url:
            if 'youtube.com/watch?v=' in self.video_url:
                video_id = self.video_url.split('v=')[1].split('&')[0]
                return f"https://www.youtube.com/embed/{video_id}"
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
                return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url


class CategoryGroupConfig(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='group_configs')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='category_configs')
    questions_count = models.IntegerField(default=5, verbose_name="Savollar soni")
    random_order = models.BooleanField(default=True, verbose_name="Random tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kategoriya guruh sozlamasi"
        verbose_name_plural = "Kategoriya guruh sozlamalari"
        unique_together = ['category', 'group']

    def __str__(self):
        return f"{self.category.name} -> {self.group.name} ({self.questions_count} savol)"


class Device(models.Model):
    device_id = models.CharField(max_length=255, unique=True, verbose_name="Qurilma ID")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nomi")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
    user_agent = models.TextField(blank=True, verbose_name="Brauzer ma'lumoti")
    ip_address = models.CharField(max_length=45, blank=True, verbose_name="IP manzil")
    platform = models.CharField(max_length=100, blank=True, verbose_name="Platforma")
    screen_resolution = models.CharField(max_length=20, blank=True, verbose_name="Ekran o'lchami")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Oxirgi ko'rilgan")
    first_seen = models.DateTimeField(auto_now_add=True, verbose_name="Birinchi ko'rilgan")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        verbose_name = "Qurilma"
        verbose_name_plural = "Qurilmalar"
        ordering = ['-last_seen']

    def __str__(self):
        return self.name or self.device_id[:20]

    @property
    def is_online(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.last_seen >= timezone.now() - timedelta(minutes=2)


class StudentQuestionHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='question_history')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'category', 'question']
        ordering = ['seen_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.category.name} - {self.question.id}"


class GroupExamConfig(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='exam_config')
    use_category_configs = models.BooleanField(default=True, verbose_name="Kategoriya sozlamalaridan foydalanish")
    questions_per_student = models.IntegerField(default=10, verbose_name="Har talaba uchun savollar soni")
    total_questions = models.IntegerField(default=10, verbose_name="Jami savollar soni")
    random_order = models.BooleanField(default=True, verbose_name="Random tartib")
    show_correct_answer = models.BooleanField(default=False, verbose_name="To'g'ri javobni ko'rsatish")
    time_limit = models.IntegerField(default=0, verbose_name="Vaqt limiti (daqiqa)")
    max_attempts = models.IntegerField(default=1, verbose_name="Maksimal urinishlar")

    # Baholash tizimi (past/o'rta/yuqori yoki fail/passed)
    grading_enabled = models.BooleanField(default=False, verbose_name="Baholash tizimini yoqish")
    low_threshold = models.IntegerField(default=40, verbose_name="Past/o'rta chegarasi (%)")
    high_threshold = models.IntegerField(default=70, verbose_name="O'rta/yuqori chegarasi (%)")
    label_low = models.CharField(max_length=50, default="Past", verbose_name="Past uchun yorliq")
    label_medium = models.CharField(max_length=50, default="O'rta", verbose_name="O'rta uchun yorliq")
    label_high = models.CharField(max_length=50, default="Yuqori", verbose_name="Yuqori uchun yorliq")

    # Audio sozlamalari (guruh uchun umumiy, eski)
    audio_file = models.FileField(upload_to='exam_audio/', blank=True, null=True, verbose_name="Imtihon audio fayli")
    max_audio_plays = models.IntegerField(default=1, verbose_name="Audio necha marta eshitilishi mumkin")
    audio_instruction = models.TextField(blank=True, null=True, verbose_name="Audio ko'rsatmasi")

    # Sertifikat sozlamalari
    certificate_enabled = models.BooleanField(default=True, verbose_name="Sertifikat berish")
    certificate_level = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="Sertifikat darajasi",
        help_text="Masalan: A1, A2, B1, B2, C1, C2"
    )
    certificate_teacher = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name="Sertifikatdagi o'qituvchi ismi",
        help_text="Bo'sh qoldirilsa, guruh o'qituvchisi ishlatiladi"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imtihon sozlamasi"
        verbose_name_plural = "Imtihon sozlamalari"

    def __str__(self):
        return f"{self.group.name}: {self.total_questions} savol/talaba"


class StudentAudioPlay(models.Model):
    """
    Har bir student, guruh va kategoriya uchun audio eshitish hisoblagichi.
    Asosiy maydonlar:
    - student: kimning hisobi
    - group: qaysi guruh
    - category: qaysi kategoriya audiosini eshitilyapti
    - exam_session: qaysi sessiyada (nullable)
    - play_count: necha marta eshitgan
    - max_plays: maksimal ruxsat etilgan marta (0=cheksiz)
    """
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='audio_plays')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    exam_session = models.ForeignKey(
        'QuizSession', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    play_count = models.IntegerField(default=0)
    max_plays = models.IntegerField(default=1)
    last_played_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student audio ijrosi"
        verbose_name_plural = "Student audio ijrolari"
        # Har bir student + group + category + session kombinatsiyasi unique
        unique_together = ['student', 'group', 'category', 'exam_session']

    def __str__(self):
        max_display = self.max_plays if self.max_plays > 0 else '∞'
        return f"{self.student.full_name} | {self.category.name} | {self.play_count}/{max_display}"

    def can_play(self):
        """Yana eshitish mumkinmi?"""
        if self.max_plays == 0:
            return True  # Cheksiz
        return self.play_count < self.max_plays

    def increment_play(self):
        """Eshitish sonini +1 qilish"""
        if self.can_play():
            self.play_count += 1
            self.save(update_fields=['play_count', 'last_played_at'])
            return True
        return False

    @property
    def remaining_plays(self):
        """Qolgan eshitish soni"""
        if self.max_plays == 0:
            return None  # Cheksiz
        return max(0, self.max_plays - self.play_count)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    groups = models.ManyToManyField(Group, related_name='teachers', verbose_name="Guruhlar", blank=True)
    all_groups = models.BooleanField(default=False, verbose_name="Barcha guruhlarga kirish")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'qituvchi"
        verbose_name_plural = "O'qituvchilar"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class AssessmentScore(models.Model):
    ASSESSMENT_TYPES = [
        ('speaking', 'Og\'zaki (Speaking)'),
        ('written', 'Yozma ish (Written)'),
    ]

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessment_scores')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, verbose_name="Baholash turi")
    score = models.IntegerField(default=0, verbose_name="Ball")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_assessments', verbose_name="Qo'shgan foydalanuvchi")
    comment = models.TextField(blank=True, verbose_name="Izoh")
    student_name_saved = models.CharField(max_length=200, blank=True, verbose_name="Student nomi (saqlangan)")
    group_name_saved = models.CharField(max_length=100, blank=True, verbose_name="Guruh nomi (saqlangan)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Baholash"
        verbose_name_plural = "Baholashlar"
        unique_together = ['student', 'group', 'assessment_type']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_name_saved} - {self.get_assessment_type_display()}: {self.score}"


class TeacherScoreLog(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='score_logs')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_score_logs')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    student_name_saved = models.CharField(max_length=200, blank=True, verbose_name="Student nomi (saqlangan)")
    group_name_saved = models.CharField(max_length=100, blank=True, verbose_name="Guruh nomi (saqlangan)")
    score_added = models.IntegerField(default=0, verbose_name="Qo'shilgan ball")
    comment = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "O'qituvchi ball qo'shish"
        verbose_name_plural = "O'qituvchi ball qo'shishlar"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.student and not self.student_name_saved:
            self.student_name_saved = self.student.full_name
        if self.group and not self.group_name_saved:
            self.group_name_saved = self.group.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} -> {self.student_name_saved}: +{self.score_added}"


class CertificateSetting(models.Model):
    background_image = models.ImageField(
        upload_to='certificate_bg/',
        verbose_name="Sertifikat fon rasmi"
    )
    threshold_percentage = models.IntegerField(
        default=50,
        verbose_name="Sertifikat olish uchun minimal ball (%)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sertifikat sozlamasi"
        verbose_name_plural = "Sertifikat sozlamalari"

    def __str__(self):
        return f"Sertifikat sozlamasi ({self.threshold_percentage}%)"


class Certificate(models.Model):
    student_name = models.CharField(max_length=200, verbose_name="Student ismi")
    group_name = models.CharField(max_length=100, verbose_name="Guruh nomi")
    score = models.FloatField(verbose_name="Ball")
    certificate_file = models.FileField(
        upload_to='certificates/',
        verbose_name="Sertifikat fayli"
    )
    quiz_result = models.ForeignKey(
        QuizResult, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='certificates', verbose_name="Test natijasi"
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    is_archived = models.BooleanField(default=False, verbose_name="Arxivlangan")

    class Meta:
        verbose_name = "Sertifikat"
        verbose_name_plural = "Sertifikatlar"
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.student_name} - {self.score}%"