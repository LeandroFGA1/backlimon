from rest_framework import serializers
from .models import Cliente, Usuario
from django.db import transaction
from .validators import validate_run_dv
#from .utils import RecaptchaValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from utils.validators import validate_email

class ClienteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        write_only=True,
        validators=[
            lambda value: validate_email(value)
        ]
    )
    class Meta:
        model = Cliente
        fields = [
            'email', 'password', 'password_confirm', 'primer_nombre', 'segundo_nombre', 'primer_apellido',
            'segundo_apellido', 'run', 'dv', 'region', 'comuna', 'direccion'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.pop('password_confirm', None)
        if password and password_confirm and password != password_confirm:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})

        run = data.get('run')
        dv = data.get('dv')
        if run and dv:
            validate_run_dv(run, dv)

        return data
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = Usuario.objects.create_user(email=email, password=password)

        cliente = Cliente.objects.create(user=user, **validated_data)
        return cliente

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user_data = validated_data.pop('user', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if user_data:
                instance.user.email = user_data.get('email', instance.user.email)
                instance.user.save()

            if password:
                instance.user.set_password(password)
                instance.user.save()

        return instance

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        # Validación de email y password
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError('Las credenciales no son correctas.')
        else:
            raise serializers.ValidationError('Se requieren email y contraseña.')

        data = super().validate(attrs)
        return data