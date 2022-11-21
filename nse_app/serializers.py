from rest_framework import serializers
from .models import *



class nse_dataSerializer(serializers.ModelSerializer):

    
    class Meta:                     
        model = nse_model
        fields = '__all__'
        # exclude = ['buy_time']

class nse_profitSerializer(serializers.ModelSerializer):

    
    class Meta:                     
        model = nse_profit
        fields = '__all__'
        # exclude = ['buy_time']

class nse_s_Serializer(serializers.ModelSerializer):

    
    class Meta:                     
        model = nse_data
        fields = '__all__'
        # exclude = ['buy_time']

class nseSerializer(serializers.ModelSerializer):

    
    class Meta:                     
        model = nse
        fields = '__all__'
        # exclude = ['buy_time']