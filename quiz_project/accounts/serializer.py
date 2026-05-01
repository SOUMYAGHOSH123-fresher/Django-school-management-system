from quiz_api.models import User, Profile, SchoolClass, Subject
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.conf import settings
from quiz_api.services import send_create_user_email, send_approve_user_email, send_user_email


class RegisterSerializer(serializers.ModelSerializer):
    # extra fields (optional, role-based)
    student_class = serializers.PrimaryKeyRelatedField(
        queryset=SchoolClass.objects.all(),
        required=False
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False
    )
    admin_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'student_class',
            'subject',
            'admin_code'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    # ---------------- VALIDATION ----------------
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role')

        # 🔹 Common validations
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})

        if len(email.split('@')[0]) < 3:
            raise serializers.ValidationError({'email': "Minimum 3 chars before @"})

        if not (6 <= len(password) <= 50):
            raise serializers.ValidationError({'password': "6–50 characters required"})

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({'password': "Must contain at least 1 digit"})

        if first_name and not first_name[0].isupper():
            raise serializers.ValidationError({'first_name': "Must start with uppercase"})

        if last_name and not last_name[0].isupper():
            raise serializers.ValidationError({'last_name': "Must start with uppercase"})

        if first_name == last_name:
            raise serializers.ValidationError("First and last name cannot be same")

        # 🔹 Role-based validation
        if role == 'student':
            if not data.get('student_class'):
                raise serializers.ValidationError({'student_class': "Required for students"})

        elif role == 'teacher':
            if not data.get('subject'):
                raise serializers.ValidationError({'subject': "Required for teachers"})

        elif role == 'principal':
            admin_code = data.get('admin_code')
            if admin_code != settings.ADMIN_REGISTRATION_CODE:
                raise serializers.ValidationError({'admin_code': "Invalid admin code"})

        else:
            raise serializers.ValidationError({'role': "Invalid role"})

        return data

    # ---------------- CREATE ----------------
    def create(self, validated_data):
        role = validated_data.get('role')

        # remove non-model field
        validated_data.pop('admin_code', None)

        if role == 'principal':
            user = User.objects.create_superuser(**validated_data)
            send_user_email(validated_data.get('email'))
        else:
            user = User.objects.create_user(**validated_data)
            send_create_user_email(validated_data.get('email'))

        return user


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'student_class']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_create_user_email(validated_data.get('email'))
        return user

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role')
        student_class = data.get('student_class')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is already exist')

        username_part = email.split('@')[0]
        if len(username_part) < 3:
            raise ValidationError("Email must have at least 3 characters before '@'")

        if len(password) < 6 or len(password) > 50:
            raise ValidationError("Password must be between 6 and 50 characters")
        
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit')

        if first_name and not first_name[0].isupper():
            raise ValidationError("first_name", "First letter must be uppercase")

        if last_name and not last_name[0].isupper():
            raise ValidationError("last_name", "Last letter must be uppercase")
        
        # Names should not be same
        if first_name and last_name and first_name == last_name:
            raise ValidationError("First name and last name cannot be same")
        
         # 2. Role-Based Logic
        if role != 'student':
            raise ValidationError('canot register as other role')
        else:
            if not student_class:
                raise serializers.ValidationError({"student_class": "Students must have a class."})

        return data 


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role', 'subject']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        send_create_user_email(validated_data.get('email'))
        return user

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role')
        subject = data.get('subject')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is already exist')

        username_part = email.split('@')[0]
        if len(username_part) < 3:
            raise ValidationError("Email must have at least 3 characters before '@'")

        if len(password) < 6 or len(password) > 50:
            raise ValidationError("Password must be between 6 and 50 characters")
        
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit')

        if first_name and not first_name[0].isupper():
            raise ValidationError("first_name", "First letter must be uppercase")

        if last_name and not last_name[0].isupper():
            raise ValidationError("last_name", "Last letter must be uppercase")
        
        # Names should not be same
        if first_name and last_name and first_name == last_name:
            raise ValidationError("First name and last name cannot be same")
        
         # 2. Role-Based Logic
        if role != 'teacher':
            raise ValidationError('canot register as other role')
        else:
            if not subject:
                raise serializers.ValidationError({"subject": "Teacher must be assigned a subject."})

        return data 


class PrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_superuser(**validated_data)
        send_approve_user_email(validated_data.get('email'))
        return user

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role')

        if User.objects.filter(email=email).exists():
            raise ValidationError('Email is already exist')

        username_part = email.split('@')[0]
        if len(username_part) < 3:
            raise ValidationError("Email must have at least 3 characters before '@'")

        if len(password) < 6 or len(password) > 50:
            raise ValidationError("Password must be between 6 and 50 characters")
        
        if not any(char.isdigit() for char in password):
            raise ValidationError('Password must contain at least one digit')

        if first_name and not first_name[0].isupper():
            raise ValidationError({"first_name": "First letter must be uppercase"})

        if last_name and not last_name[0].isupper():
            raise ValidationError('last_name', "Last letter must be uppercase")
        
        # Names should not be same
        if first_name and last_name and first_name == last_name:
            raise ValidationError("First name and last name cannot be same")

        if role != 'principal':
            raise ValidationError("Canot be register as other")
        
        request = self.context.get('request')
        postman_code = request.data.get('admin_code')
        if role == 'principal':
            if postman_code != settings.ADMIN_REGISTRATION_CODE:
                raise ValidationError({"admin_code": "Incorrect admin secret key."})

        return data 
  

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)   

    def validate_email(self, email):
        if '@' not in email or '.' not in email:
            raise ValidationError("Invalid email")

        if len(email.split('@')[0]) < 5:
            raise ValidationError("Email must have at least 5 characters before '@'")
        
        return email
    

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if '@' not in email or '.' not in email:
            raise serializers.ValidationError("Invalid email format")

        if len(email.split('@')[0]) < 4:
            raise serializers.ValidationError("Email must have at least 4 characters before '@'")

        return email


class ResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['new_password', 'confirm_password']

    
    def validate(self, data):
        if data['new_password'] and data['confirm_password'] and data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("password not match")
        
        return data


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Profile
        fields = ['email', 'phone', 'bio', 'address']

