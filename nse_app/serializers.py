from rest_framework import serializers
from .models import *



class settingSerializer(serializers.ModelSerializer):
    class Meta:
        model = nse_setting
        fields = "__all__"
        # exclude = ['sell_buy_time',]

class stockListSerializer(serializers.ModelSerializer):
    percentage = settingSerializer()
    class Meta:
        model = stock_detail
        fields = "__all__"
        depth = 1
        # exclude = ['sell_buy_time',]

class stockPostSerializer(serializers.ModelSerializer):
    # percentage = settingSerializer()
    class Meta:
        model = stock_detail
        fields = "__all__"
        # depth = 1
        # exclude = ['sell_buy_time',]


class putbankniftySerializer(serializers.ModelSerializer):
    class Meta:
        model = stock_detail
        fields = "__all__"
        # exclude = ['percentage',]




# class UserRegistrationSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ['email','fullname' ,'password','password2']
#         extra_kwargs={
#             'password':{'write_only':True}
#     }


#     def validate(self, attrs):
#         password=attrs.get('password')
#         password2=attrs.get('password2')
#         if password != password2:
#             raise serializers.ValidationError("password and confirm password DOES NOT MATCH")
#         return attrs

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)


from rest_framework import serializers


# class LoginSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             "email",
#             "password",
#         ]

#         extra_kwargs = {"password": {"write_only": True}}

#     def validate(self, data):
#         password = data.get("password")
#         email = data.get("email")


# class RegistrationSerializer(serializers.ModelSerializer):

# 	password2 				= serializers.CharField(style={'input_type': 'password'}, write_only=True)

# 	class Meta:
# 		model = User
# 		fields = ['email', 'username', 'password', 'password2']
# 		extra_kwargs = {
# 				'password': {'write_only': True},
# 		}	


# 	def	save(self):

# 		account = User(
# 					email=self.validated_data['email'],
# 					username=self.validated_data['username']
# 				)
# 		password = self.validated_data['password']
# 		password2 = self.validated_data['password2']
# 		if password != password2:
# 			raise serializers.ValidationError({'password': 'Passwords must match.'})
# 		account.set_password(password)
# 		account.save()
# 		return account

# class UserLoginSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(max_length=255)
#     class Meta:
#         model = User
#         fields = ['email',  'password']        