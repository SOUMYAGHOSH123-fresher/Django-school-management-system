from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import (
    User, Subject, SchoolClass, 
    Quiz, Question, Choice, StudentAttempt, 
    StudentAnswer, QuizInvitation, AttendanceSystem
    )
from django.db import transaction
from django.conf import settings


# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'password', 'first_name', 'last_name', 'role', 'student_class']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)
    

#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')
#         role = data.get('role')
#         student_class = data.get('student_class')

#         print(student_class)

#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email is already exist')

#         username_part = email.split('@')[0]
#         if len(username_part) < 3:
#             raise ValidationError("Email must have at least 3 characters before '@'")

#         if len(password) < 6 or len(password) > 50:
#             raise ValidationError("Password must be between 6 and 50 characters")
        
#         isDigit = False
#         for char in password:
#             if char.isdigit():
#                 isDigit = True

#         if not isDigit:
#             raise ValidationError('password must be a digit')

#         if first_name and not first_name[0].isupper():
#             raise ValidationError("first_name", "First letter must be uppercase")

#         if last_name and not last_name[0].isupper():
#             raise ValidationError("last_name", "First letter must be uppercase")
        
#         # Names should not be same
#         if first_name and last_name and first_name == last_name:
#             raise ValidationError("First name and last name cannot be same")
        
#          # 2. Role-Based Logic
#         if role != 'student':
#             raise ValidationError('canot register as other role')
#         else:
#             if not student_class:
#                 raise serializers.ValidationError({"student_class": "Students must have a class."})

#         return data 


# class TeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['email', 'password', 'first_name', 'last_name', 'role', 'subject']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)
    

#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')
#         role = data.get('role')
#         subject = data.get('subject')

#         print(subject)

#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email is already exist')

#         username_part = email.split('@')[0]
#         if len(username_part) < 3:
#             raise ValidationError("Email must have at least 3 characters before '@'")

#         if len(password) < 6 or len(password) > 50:
#             raise ValidationError("Password must be between 6 and 50 characters")
        
#         isDigit = False
#         for char in password:
#             if char.isdigit():
#                 isDigit = True

#         if not isDigit:
#             raise ValidationError('password must be a digit')

#         if first_name and not first_name[0].isupper():
#             raise ValidationError("first_name", "First letter must be uppercase")

#         if last_name and not last_name[0].isupper():
#             raise ValidationError("last_name", "First letter must be uppercase")
        
#         # Names should not be same
#         if first_name and last_name and first_name == last_name:
#             raise ValidationError("First name and last name cannot be same")
        
#          # 2. Role-Based Logic
#         if role != 'teacher':
#             raise ValidationError('canot register as other role')
#         else:
#             if not subject:
#                 raise serializers.ValidationError({"subject": "Teacher must be assigned a subject."})

#         return data 


# class PrincipalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role']
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         return User.objects.create_superuser(**validated_data)
    
#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         first_name = data.get('first_name')
#         last_name = data.get('last_name')

#         role = data.get('role')

#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email is already exist')

#         username_part = email.split('@')[0]
#         if len(username_part) < 3:
#             raise ValidationError("Email must have at least 3 characters before '@'")

#         if len(password) < 6 or len(password) > 50:
#             raise ValidationError("Password must be between 6 and 50 characters")
        
#         isDigit = False
#         for char in password:
#             if char.isdigit():
#                 isDigit = True

#         if not isDigit:
#             raise ValidationError('password must be a digit')

#         if first_name and not first_name[0].isupper():
#             raise ValidationError('first_name', "First letter must be uppercase")

#         if last_name and not last_name[0].isupper():
#             raise ValidationError('last_name', "First letter must be uppercase")
        
#         # Names should not be same
#         if first_name and last_name and first_name == last_name:
#             raise ValidationError("First name and last name cannot be same")

#         if role != 'principal':
#             raise ValidationError("Canot be register as other")
        
#         request = self.context.get('request')
#         postman_code = request.data.get('admin_code')
#         if role == 'principal':
#             if postman_code != settings.ADMIN_REGISTRATION_CODE:
#                 raise ValidationError({"admin_code": "Incorrect admin secret key."})
        

#         return data 
  

# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)   

#     def validate_email(self, email):
#         if '@' not in email or '.' not in email:
#             raise ValidationError("Invalid email")

#         if len(email.split('@')[0]) < 5:
#             raise ValidationError("Email must have at least 5 characters before '@'")
        
#         return email
    

# class ResetPasswordRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)

#     def validate_email(self, email):
#         if '@' not in email or '.' not in email:
#             raise serializers.ValidationError("Invalid email format")

#         if len(email.split('@')[0]) < 4:
#             raise serializers.ValidationError("Email must have at least 4 characters before '@'")

#         return email


# class ResetPasswordSerializer(serializers.ModelSerializer):
#     new_password = serializers.CharField(write_only=True, required=True)
#     confirm_password = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ['new_password', 'confirm_password']

    
#     def validate(self, data):
#         if data['new_password'] and data['confirm_password'] and data['new_password'] != data['confirm_password']:
#             raise serializers.ValidationError("password not match")
        
#         return data


# class ProfileSerializer(serializers.ModelSerializer):
#     email = serializers.ReadOnlyField(source='user.email')

#     class Meta:
#         model = Profile
#         fields = ['email', 'phone', 'bio', 'address']


# class BulkStudentSerializer(serializers.ModelSerializer):
#     class_name = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'id', 
#             'email', 
#             'password', 
#             'first_name', 
#             'last_name', 
#             'role', 
#             'class_name'
#         ]
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         class_name = validated_data.pop('class_name')
#         print('validated data', validated_data)
#         # student_class = SchoolClass.objects.get(class_name__icontains=class_name).id
#         user = User.objects.create_user(**validated_data)
#         user._skip_welcome_email = True
#         return user

#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         role = data.get('role')
#         class_name = data.get('class_name', None)

#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email is already exist')

#         username_part = email.split('@')[0]
#         if len(username_part) < 3:
#             raise ValidationError("Email must have at least 3 characters before '@'")

#         if len(password) < 6 or len(password) > 50:
#             raise ValidationError("Password must be between 6 and 50 characters")
        
#         try:
#             school_class = SchoolClass.objects.get(class_name__icontains=class_name)
#         except SchoolClass.DoesNotExist:
#             raise ValidationError({
#                 "class_name": f"{class_name} not found"
#             })

#         # 2. Role-Based Logic
#         if role != 'student':
#             raise ValidationError('can not register as other role')
#         else:
#             if not school_class:
#                 raise serializers.ValidationError({"student_class": "Students must have a class."})
        
#         data['student_class'] = school_class
#         data['role'] = 'student'

#         return data 


# class BulkTeacherSerializer(serializers.ModelSerializer):
#     subject = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'id', 
#             'email', 
#             'password', 
#             'first_name', 
#             'last_name', 
#             'role', 
#             'subject'
#         ]
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         subject_name = validated_data.pop('subject')
#         # print("validated_data", validated_data)
#         # subject=Subject.objects.get(subject__icontains=subject_name)
#         user = User.objects.create_user(**validated_data)
#         user._skip_welcome_email = True
#         return user
    

#     def validate(self, data):
#         email = data.get('email')
#         password = data.get('password')
#         role = data.get('role')
#         subject = data.get('subject', None)


#         if User.objects.filter(email=email).exists():
#             raise ValidationError('Email is already exist')

#         username_part = email.split('@')[0]
#         if len(username_part) < 3:
#             raise ValidationError("Email must have at least 3 characters before '@'")

#         if len(password) < 6 or len(password) > 50:
#             raise ValidationError("Password must be between 6 and 50 characters")
        
#         try:
#             subject = Subject.objects.get(subject__icontains=subject)
#         except Subject.DoesNotExist:
#             raise ValidationError({
#                 "subject": f"{subject} not found"
#             })

#         # 2. Role-Based Logic
#         if role != 'teacher':
#             raise ValidationError('can not register as other role')
#         else:
#             if not subject:
#                 raise serializers.ValidationError({"subject": "Teacher must have a subject."})
        
#         data['subject'] = subject
#         data['role'] = 'teacher'

#         return data 


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        subject = str(validated_data.get('subject'))
        return Subject.objects.create(
            subject=subject
        )


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = '__all__'
    
    def create(self, validated_data):
        class_name = str(validated_data.get('class_name'))
        return SchoolClass.objects.create(
            class_name=class_name
        )


class StudentSerializer(serializers.ModelSerializer):
    student_class = SchoolClassSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'student_class', 'is_approved']


class ChoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Choice
        fields = ['id', 'option', 'is_true']
        extra_kwargs = {'is_true': {'write_only': True}}


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question', 'mark', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.subject')
    teacher_name = serializers.ReadOnlyField(source='teacher.email')
    questions = QuestionSerializer(many=True)
    student_class = serializers.SerializerMethodField()
    student_class_key = serializers.PrimaryKeyRelatedField(
        queryset=SchoolClass.objects.all(),
        source='student_class'
    )


    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'subject_name', 'teacher_name',
            'student_class', 'quiz_type', 'questions', 
            'duration', 'is_active', 'student_class_key'
        ]
        read_only_fields = ['is_active']

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        student_class = validated_data.pop('student_class')

        with transaction.atomic():
            quiz = Quiz.objects.create(
                student_class=student_class,
                **validated_data,
            )

            for ques in questions:
                choice_data = ques.pop('choices')

                if not any(c.get('is_true') for c in choice_data):
                    raise ValidationError("Each question must have at least one correct answer")
                question = Question.objects.create(quiz=quiz, **ques)

                for choice_data in choice_data:
                    Choice.objects.create(question=question, **choice_data)

        return quiz
    
    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])

        ## update the data
        instance.title = validated_data.get('title', instance.title)
        instance.quiz_type = validated_data.get('quiz_type', instance.quiz_type)
        if 'student_class' in validated_data:
            instance.student_class = validated_data.get(
                'student_class'
            )
        instance.save()

        existing_questions = {q.id: q for q in instance.questions.all()}

        if questions_data:
            with transaction.atomic():
                for ques_data in questions_data:
                    choices_data = ques_data.pop('choices', [])
                    ques_id = ques_data.get('id')

                    # ================= UPDATE EXISTING =================
                    if ques_id and ques_id in existing_questions:
                        question = existing_questions.pop(ques_id)

                        question.question = ques_data.get('question', question.question)
                        question.mark = ques_data.get('mark', question.mark)
                        question.save()

                    # ================= CREATE NEW =================
                    else:
                        question = Question.objects.create(quiz=instance, **ques_data)

                    # ================= HANDLE CHOICES =================
                    existing_choices = {c.id: c for c in question.choices.all()}

                    for choice_data in choices_data:
                        choice_id = choice_data.get('id')

                        if choice_id and choice_id in existing_choices:
                            choice = existing_choices.pop(choice_id)
                            choice.option = choice_data.get('option', choice.option)
                            choice.is_true = choice_data.get('is_true', choice.is_true)
                            choice.save()
                        else:
                            Choice.objects.create(question=question, **choice_data)

                    # delete removed choices
                    for choice in existing_choices.values():
                        choice.delete()

                # delete removed questions
                for question in existing_questions.values():
                    question.delete()

        return instance

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
        
        user = request.user   
        subject = getattr(user, 'subject', None)
        # if student_class is None:
        #     raise ValidationError("student class is None")
        
        # print("data", data.get('student_class'))
        title = data.get('title', self.instance.title if self.instance else None)

        queryset = Quiz.objects.filter(teacher=request.user, subject=subject, title=title)

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
                                   
        if queryset.exists():
            raise serializers.ValidationError(
                'You have already created a quiz with this title for this subject.'
            )
    
        return data

    def get_student_class(self, obj):
        if not obj.student_class:
            return None
        
        return {
            'id': obj.student_class.id,
            'class_name': obj.student_class.class_name
        }


class UserSerializer(serializers.ModelSerializer):
    student_class = SchoolClassSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'subject', 'student_class', 'is_approved']


class StudentAttemptSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField()

    class Meta:
        model = StudentAttempt
        fields = ['id', 'student', 'quiz', 'score', 'completed']

    def get_quiz(self, obj):
        return {
            'id': obj.quiz.id,
            "title": obj.quiz.title
        }


class QuizInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizInvitation
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='question.question')
    selected_answer = serializers.CharField(source='select_answer.option')
    correct_answer = serializers.SerializerMethodField()
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_answer', 'correct_answer', 'is_correct']

    def get_correct_answer(self, obj):
        correct = obj.question.choices.filter(is_true=True).first()
        return correct.option if correct else None
    
    def get_is_correct(self, obj):
        return obj.select_answer.is_true


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSystem
        fields = '__all__'

