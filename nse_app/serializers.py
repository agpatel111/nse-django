from rest_framework import serializers
from .models import *



class settingSerializer(serializers.ModelSerializer):
    class Meta:
        model = nse_setting
        # fields = "__all__"
        exclude = ['you_can_buy', 'id']

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

class pcr_stock_nameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = pcr_stock_name
        fields = "__all__"




