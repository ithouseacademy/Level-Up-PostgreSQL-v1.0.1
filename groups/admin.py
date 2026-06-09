# groups/admin.py - TO'G'IRILGAN VERSIYA

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Group, Student, ExamSession, ExamResult, ExamControl, 
    AdminPassword, Rules, Category, QuizQuestion, Teacher, TeacherScoreLog, AssessmentScore,
    CertificateSetting, Certificate, GroupExamConfig,
    Folder, FolderCategory, GroupFolder, FolderGroupConfig
)

# forms.py dan import
from django import forms
from .models import QuizQuestion

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['category', 'question_type', 'question_text', 'correct_answer', 'scrambled_words', 'correct_sentence']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border rounded p-2'}),
            'correct_answer': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'scrambled_words': forms.Textarea(attrs={'rows': 2, 'class': 'w-full border rounded p-2 font-mono', 'placeholder': "he / go / school / I / to"}),
            'correct_sentence': forms.TextInput(attrs={'class': 'w-full border rounded p-2', 'placeholder': "I go to school"}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        
        if question_type == 'sentence_arrangement':
            if not cleaned_data.get('scrambled_words'):
                self.add_error('scrambled_words', 'So\'zlarni kiriting!')
            if not cleaned_data.get('correct_sentence'):
                self.add_error('correct_sentence', 'To\'g\'ri gapni kiriting!')
        
        return cleaned_data


# ============ KATEGORIYA ADMIN ============
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Kategoriya admin paneli"""
    list_display = ['id', 'name', 'description_preview', 'question_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'description')
        }),
        ('Vaqt', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def description_preview(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_preview.short_description = 'Tavsif'
    
    def question_count(self, obj):
        return obj.quiz_questions.count()
    question_count.short_description = 'Savollar soni'


# ============ SAVOL ADMIN - TO'G'IRILGAN ============
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Savol admin paneli"""
    form = QuizQuestionForm
    # list_display ga question_type qo'shildi
    list_display = ['id', 'category', 'question_type', 'question_type_badge', 'preview', 'created_at']
    list_filter = ['category', 'question_type', 'created_at']
    search_fields = ['question_text', 'correct_answer', 'correct_sentence', 'scrambled_words']
    # list_editable o'chirildi (yoki list_display ga qo'shilgan maydonlar bilan ishlatish mumkin)
    # list_editable = ['question_type']  # BU QATOR O'CHIRILDI
    list_per_page = 20
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('category', 'question_type')
        }),
        ('Fill Blank (Bo\'sh joy to\'ldirish)', {
            'fields': ('question_text', 'correct_answer'),
            'classes': ('collapse',),
            'description': 'Savol matnida ___ bilan bo\'sh joy belgilang. Masalan: I ___ to school every day.'
        }),
        ('Sentence Arrangement (So\'zlarni tartibga solish)', {
            'fields': ('scrambled_words', 'correct_sentence'),
            'classes': ('collapse',),
            'description': 'So\'zlarni / bilan ajrating. Masalan: he / go / school / I / to'
        }),
    )
    
    def question_type_badge(self, obj):
        if obj.question_type == 'fill_blank':
            return '📝 Bo\'sh joy'
        elif obj.question_type == 'sentence_arrangement':
            return '🔀 So\'z tartibi'
        else:
            return '❓ Boshqa'
    question_type_badge.short_description = 'Savol turi belgisi'
    
    def preview(self, obj):
        if obj.question_type == 'fill_blank':
            text = obj.question_text[:60] if obj.question_text else '-'
            return f'📝 {text}'
        else:
            text = obj.correct_sentence[:60] if obj.correct_sentence else '-'
            words = obj.get_scrambled_words_list() if hasattr(obj, 'get_scrambled_words_list') else []
            words_str = ' / '.join(words[:5]) + ('...' if len(words) > 5 else '')
            return f'🔀 {text}<br><span style="color:gray;font-size:11px;">🔀 {words_str}</span>'
    preview.short_description = 'Savol'
    preview.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


# ============ STUDENT INLINE ============
class StudentInline(admin.StackedInline):
    """Student profilini User admin panelida ko'rsatish"""
    model = Student
    can_delete = False
    verbose_name_plural = 'Student profili'
    fk_name = 'user'
    fields = ['group']
    autocomplete_fields = ['group']


# ============ CUSTOM USER ADMIN ============
class CustomUserAdmin(UserAdmin):
    """Foydalanuvchi admin panelini sozlash"""
    inlines = [StudentInline]
    list_display = ['username', 'get_full_name', 'email', 'is_staff', 'is_superuser', 'get_group', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'student_profile__group']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'student_profile__group__name']
    readonly_fields = ['last_login', 'date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ()}),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'To\'liq ism'
    get_full_name.admin_order_field = 'first_name'
    
    def get_group(self, obj):
        if hasattr(obj, 'student_profile') and obj.student_profile and obj.student_profile.group:
            return obj.student_profile.group.name
        return '-'
    get_group.short_description = 'Guruh'
    get_group.admin_order_field = 'student_profile__group__name'


# User modelini qayta ro'yxatdan o'tkazish
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============ GROUP ADMIN ============
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Guruh admin paneli"""
    list_display = ['name', 'teacher', 'student_count', 'category_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'teacher']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'teacher')
        }),
        ('Vaqt', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'O\'quvchilar soni'
    student_count.admin_order_field = 'students__count'
    
    def category_count(self, obj):
        return obj.group_categories.filter(is_active=True).count()
    category_count.short_description = 'Kategoriyalar soni'


# ============ STUDENT ADMIN ============
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin paneli"""
    list_display = ['full_name', 'username', 'email', 'group', 'created_at']
    list_filter = ['group', 'user__is_staff']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__email', 'group__name']
    raw_id_fields = ['user']
    autocomplete_fields = ['group']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Guruh', {
            'fields': ('group',)
        }),
        ('Vaqt', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'To\'liq ism'
    full_name.admin_order_field = 'user__first_name'
    
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'
    username.admin_order_field = 'user__username'
    
    def email(self, obj):
        return obj.user.email or '-'
    email.short_description = 'Email'
    email.admin_order_field = 'user__email'
    
    def created_at(self, obj):
        return obj.user.date_joined
    created_at.short_description = 'Ro\'yxatdan o\'tgan sana'
    created_at.admin_order_field = 'user__date_joined'


# ============ EXAM SESSION ADMIN ============
@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    """Imtihon sessiyasi admin paneli"""
    list_display = ['id', 'group', 'is_active', 'started_at', 'ended_at', 'created_by', 'duration']
    list_filter = ['is_active', 'started_at', 'group']
    search_fields = ['group__name', 'created_by__username']
    readonly_fields = ['started_at', 'ended_at']
    raw_id_fields = ['created_by']
    autocomplete_fields = ['group']
    
    fieldsets = (
        ('Imtihon ma\'lumotlari', {
            'fields': ('group', 'is_active', 'created_by')
        }),
        ('Vaqt', {
            'fields': ('started_at', 'ended_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration(self, obj):
        if obj.started_at:
            end = obj.ended_at or obj.started_at
            delta = end - obj.started_at
            minutes = delta.total_seconds() // 60
            return f'{int(minutes)} daqiqa'
        return '-'
    duration.short_description = 'Davomiyligi'


# ============ EXAM RESULT ADMIN ============
@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """Imtihon natijasi admin paneli"""
    list_display = ['student', 'exam_session', 'score', 'submitted_at', 'answer_count']
    list_filter = ['exam_session__group', 'submitted_at', 'score']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'exam_session__group__name']
    readonly_fields = ['submitted_at', 'answers']
    
    fieldsets = (
        ('Natija ma\'lumotlari', {
            'fields': ('student', 'exam_session', 'score')
        }),
        ('Javoblar', {
            'fields': ('answers',),
            'classes': ('collapse',)
        }),
        ('Vaqt', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    def answer_count(self, obj):
        return len(obj.answers) if obj.answers else 0
    answer_count.short_description = 'Javoblar soni'


# ============ EXAM CONTROL ADMIN ============
@admin.register(ExamControl)
class ExamControlAdmin(admin.ModelAdmin):
    """Imtihon boshqaruvi admin paneli"""
    list_display = ['group', 'is_active', 'started_at', 'status_badge']
    list_filter = ['is_active', 'started_at']
    search_fields = ['group__name']
    readonly_fields = ['started_at']
    autocomplete_fields = ['group']
    
    fieldsets = (
        ('Imtihon boshqaruvi', {
            'fields': ('group', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('started_at',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_active:
            return '🟢 Faol'
        return '🔴 Faol emas'
    status_badge.short_description = 'Holat'


# ============ ADMIN PASSWORD ADMIN ============
@admin.register(AdminPassword)
class AdminPasswordAdmin(admin.ModelAdmin):
    """Admin parollari admin paneli (faqat superuser ko'radi)"""
    list_display = ['user', 'plain_password_preview', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['user', 'updated_at']
    
    fieldsets = (
        ('Admin ma\'lumotlari', {
            'fields': ('user', 'plain_password')
        }),
        ('Vaqt', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def plain_password_preview(self, obj):
        if obj.plain_password:
            return obj.plain_password[:10] + '...' if len(obj.plain_password) > 10 else obj.plain_password
        return '-'
    plain_password_preview.short_description = 'Parol'
    
    def get_queryset(self, request):
        """Faqat superuserlar ko'rishi mumkin"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


# ============ RULES ADMIN ============
@admin.register(Rules)
class RulesAdmin(admin.ModelAdmin):
    """Qonun va qoidalar admin paneli"""
    list_display = ['id', 'video_preview', 'images_status', 'rules_preview', 'updated_at']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Video', {
            'fields': ('video_url', 'video_file'),
            'classes': ('wide',)
        }),
        ('Rasmlar', {
            'fields': (
                ('image1', 'image1_title', 'image1_description'),
                ('image2', 'image2_title', 'image2_description'),
            ),
        }),
        ('Qoidalar matni', {
            'fields': ('rules_text',),
        }),
        ('Vaqt', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def video_preview(self, obj):
        if obj.video_url:
            return f'<a href="{obj.video_url}" target="_blank">📹 YouTube</a>'
        elif obj.video_file:
            return '📁 Video fayl'
        return '❌ Video yo\'q'
    video_preview.short_description = 'Video'
    video_preview.allow_tags = True
    
    def images_status(self, obj):
        images = []
        if obj.image1:
            images.append('✅ Rasm 1')
        else:
            images.append('❌ Rasm 1')
        if obj.image2:
            images.append('✅ Rasm 2')
        else:
            images.append('❌ Rasm 2')
        return ' | '.join(images)
    images_status.short_description = 'Rasmlar holati'
    
    def rules_preview(self, obj):
        if obj.rules_text:
            preview = obj.rules_text[:50]
            return preview + '...' if len(obj.rules_text) > 50 else preview
        return '-'
    rules_preview.short_description = 'Qoidalar (qisqacha)'
    
    def has_add_permission(self, request):
        """Faqat bitta qator bo'lishi mumkin"""
        if Rules.objects.exists():
            return False
        return True


# ============ ADMIN PANEL UCHUN QO'SHIMCHA SOZLAMALAR ============

# ============ TEACHER ADMIN ============
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'all_groups', 'groups_display', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
    filter_horizontal = ['groups']
    list_filter = ['is_active', 'all_groups']

    def groups_display(self, obj):
        if obj.all_groups:
            return 'Barcha guruhlar'
        return ', '.join(g.name for g in obj.groups.all())
    groups_display.short_description = 'Guruhlar'


@admin.register(AssessmentScore)
class AssessmentScoreAdmin(admin.ModelAdmin):
    list_display = ['student_name_saved', 'group_name_saved', 'assessment_type', 'score', 'added_by', 'created_at']
    list_filter = ['assessment_type', 'group_name_saved']
    search_fields = ['student_name_saved', 'group_name_saved']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TeacherScoreLog)
class TeacherScoreLogAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'student_name_saved', 'group_name_saved', 'score_added', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['teacher__user__username', 'student_name_saved', 'group_name_saved']


# Admin panel sarlavhasini o'zgartirish
admin.site.site_header = 'Guruhlar Boshqaruvi - Admin Panel'
admin.site.site_title = 'Guruhlar Admin'
admin.site.index_title = 'Boshqaruv paneliga xush kelibsiz'


# ============ QO'SHIMCHA ACTIONLAR ============

@admin.action(description='Tanlangan imtihonlarni to\'xtatish')
def stop_exam_sessions(modeladmin, request, queryset):
    """Tanlangan imtihonlarni to'xtatish"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} ta imtihon to\'xtatildi.')


# ExamSession adminiga action qo'shish
ExamSessionAdmin.actions = [stop_exam_sessions]


# ============ CATEGORY VA QUIZ QUESTION UCHUN QO'SHIMCHA ACTIONLAR ============

@admin.action(description='Tanlangan savollarni o\'chirish')
def delete_selected_questions(modeladmin, request, queryset):
    deleted = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f'{deleted} ta savol o\'chirildi.')


@admin.action(description='Tanlangan savollarni "Fill Blank" ga o\'zgartirish')
def change_to_fill_blank(modeladmin, request, queryset):
    updated = queryset.update(question_type='fill_blank')
    modeladmin.message_user(request, f'{updated} ta savol "Bo\'sh joy" turiga o\'zgartirildi.')


@admin.action(description='Tanlangan savollarni "Sentence Arrangement" ga o\'zgartirish')
def change_to_sentence_arrangement(modeladmin, request, queryset):
    updated = queryset.update(question_type='sentence_arrangement')
    modeladmin.message_user(request, f'{updated} ta savol "So\'z tartibi" turiga o\'zgartirildi.')


# QuizQuestion adminiga actionlar qo'shish
QuizQuestionAdmin.actions = [delete_selected_questions, change_to_fill_blank, change_to_sentence_arrangement]


@admin.register(CertificateSetting)
class CertificateSettingAdmin(admin.ModelAdmin):
    list_display = ['threshold_percentage', 'is_active', 'updated_at']
    list_editable = ['is_active']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'group_name', 'score', 'generated_at']
    list_filter = ['group_name', 'generated_at']
    search_fields = ['student_name', 'group_name']
    readonly_fields = ['student_name', 'group_name', 'score', 'certificate_file', 'generated_at']


@admin.register(GroupExamConfig)
class GroupExamConfigAdmin(admin.ModelAdmin):
    list_display = ['group', 'questions_per_student', 'time_limit', 'certificate_enabled', 'certificate_level']
    list_filter = ['certificate_enabled', 'certificate_level']
    search_fields = ['group__name']
    fieldsets = [
        ('Asosiy sozlamalar', {'fields': ['group', 'questions_per_student', 'random_order',
                                          'show_correct_answer', 'time_limit', 'max_attempts',
                                          'use_category_configs']}),
        ('Baholash tizimi', {'fields': ['grading_enabled', 'low_threshold', 'high_threshold',
                                        'label_low', 'label_medium', 'label_high']}),
        ('Sertifikat', {'fields': ['certificate_enabled', 'certificate_level', 'certificate_teacher']}),
        ('Audio', {'fields': ['audio_file', 'max_audio_plays', 'audio_instruction']}),
    ]


# ============ FOLDER (PAPKA) ADMIN ============
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'categories_count', 'created_at']
    search_fields = ['name']
    ordering = ['name']

    def categories_count(self, obj):
        return obj.folder_categories.count()
    categories_count.short_description = 'Kategoriyalar soni'


@admin.register(FolderCategory)
class FolderCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'folder', 'category']
    list_filter = ['folder']
    search_fields = ['folder__name', 'category__name']


@admin.register(GroupFolder)
class GroupFolderAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'folder', 'is_active', 'assigned_at']
    list_filter = ['is_active', 'folder']
    search_fields = ['group__name', 'folder__name']


@admin.register(FolderGroupConfig)
class FolderGroupConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'folder', 'group', 'categories_to_select', 'is_active']
    list_filter = ['is_active']
    search_fields = ['folder__name', 'group__name']