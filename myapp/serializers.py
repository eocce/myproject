from rest_framework import serializers
from .models import RemoteSensingData, UploadedFile
from django.contrib.auth.models import User


class RemoteSensingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemoteSensingData
        fields = ['zname', 'zpath', 'MSname', 'MSpath', 'PAname',
                  'PApath', 'CloudPercent', 'GeodeticInfo',
                  'browsejpgpath', 'ProductTime', 'id']


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        file = validated_data.get('file')
        # 你可以在这里处理你的文件，例如保存它到你的文件系统
        # 或者解压它然后保存到你的数据库
        # 在这个示例中，我们只是简单地把文件保存到了'Django项目的根目录/uploads'文件夹
        with open(f'uploads/{file.name}', 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        UploadedFile.objects.create(file_name=file.name, uploaded_by=user)
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user