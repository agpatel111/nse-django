from rest_framework import serializers
from .models import *



class settingSerializer(serializers.ModelSerializer):
    class Meta:
        model = nse_setting
        # fields = "__all__"
        exclude = ['you_can_buy']

class stockListSerializer(serializers.ModelSerializer):
    percentage = settingSerializer()
    PL = serializers.SerializerMethodField()
    
    class Meta:
        model = stock_detail
        fields = "__all__"
        # depth = 1
    
    def get_PL(self, obj):
        option = obj.percentage.option.split()
        if option[0] == 'BANKNIFTY' and obj.exit_price:
            if option[1] == 'FUTURE' and obj.type == 'SELL':
                return round((obj.buy_price - obj.exit_price) * 15, 2)
            else:
                return round((obj.exit_price - obj.buy_price) * 15, 2)
            
        elif option[0] == 'NIFTY' and obj.exit_price:
            if option[1] == 'FUTURE' and obj.type == 'SELL':
                return round((obj.buy_price - obj.exit_price) * 50, 2)
            else:
                return round((obj.exit_price - obj.buy_price) * 50, 2)
        elif option[0] == 'STOCK' and obj.exit_price:
            if option[1] == 'FUTURE' and obj.type == 'SELL':
                return round((obj.buy_price - obj.exit_price) * obj.qty, 2)
            else:
                return round((obj.exit_price - obj.buy_price) * obj.qty, 2)
        else:
            return None

class stockPostSerializer(serializers.ModelSerializer):
    # percentage = settingSerializer()
    class Meta:
        model = stock_detail
        fields = "__all__"
        # depth = 1


class putbankniftySerializer(serializers.ModelSerializer):
    class Meta:
        model = stock_detail
        fields = "__all__"
        # exclude = ['percentage',]

class pcr_stock_nameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = pcr_stock_name
        fields = "__all__"

class accountDetailsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccountCredential
        fields = "__all__"




