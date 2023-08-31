from .data_processing import publish_data_to_geoserver, query_data
from rest_framework import viewsets
from .models import RemoteSensingData
from .serializers import RemoteSensingDataSerializer, FileSerializer
import threading
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from captcha.models import CaptchaStore
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.decorators import api_view, permission_classes
from django.http import FileResponse, HttpResponseNotFound



from .scan_and_extract_data import scan_and_extract_data





class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        file_serializer = FileSerializer(data=request.data, context={'request': request})

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RemoteSensingDataView(viewsets.ModelViewSet):
    queryset = RemoteSensingData.objects.all()
    serializer_class = RemoteSensingDataSerializer

# class ScanDataView(APIView):
#     def get(self, request, format=None):
#         directory = '/path/to/your/directory'  # 你的文件夹路径
#         data_info = scan_and_extract_data(directory)
#         # ...

class PublishDataView(APIView):
    def post(self, request, format=None):
        workspace = request.data.get('workspace')
        datastore = request.data.get('datastore')
        layer = request.data.get('layer')
        publish_data_to_geoserver(workspace, datastore, layer)
        # ...

class QueryDataView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        time = request.query_params.get('time')
        coordinates = request.query_params.get('coordinates')
        polygon = request.query_params.get('polygon')

        data = query_data(time, coordinates, polygon)
        serializer = RemoteSensingDataSerializer(data, many=True)

        return Response(serializer.data)

def scan_data(directory):
    data_info = scan_and_extract_data(directory)
    # ...

# 创建一个后台线程来执行 scan_data 函数
thread = threading.Thread(target=scan_data, args=(r'E:\gggg\gfdata',))
thread.start()


class UserCreate(APIView):
    """
    创建新用户.
    """

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)

        # 检查用户名是否已存在
        username = request.data.get('username', '')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证码验证
        user_captcha = request.data.get('captcha', '')
        captcha_key = request.data.get('captcha_key', '')

        try:
            correct_captcha = CaptchaStore.objects.get(hashkey=captcha_key).response
        except CaptchaStore.DoesNotExist:
            return Response({'error': 'Invalid captcha key'}, status=status.HTTP_400_BAD_REQUEST)

        if user_captcha.lower() != correct_captcha.lower():
            return Response({'error': 'Incorrect captcha'}, status=status.HTTP_400_BAD_REQUEST)

        # 如果验证码正确，继续注册逻辑
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])


def check_username(request):
    username = request.GET.get('username', None)
    if username is None:
        return Response({'error': 'Username parameter is missing.'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'exists': True})
    else:
        return Response({'exists': False})

class UserLogin(APIView):
    """
    用户登录视图.
    """

    def post(self, request, format=None):
        data = request.data

        print('Request data:', data)  # 打印请求数据
        username = data.get('username', '')
        password = data.get('password', '')

        print('Trying to authenticate user:', username)
        user = authenticate(username=username, password=password)
        if user is None:
            print('Authentication failed for user:', username)
        else:
            print('Authentication succeeded for user:', username)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)


def custom_captcha_refresh(request):
    new_key = CaptchaStore.pick()
    image_url = reverse('captcha-image', args=[new_key])
    response = {
        'key': new_key,
        'image_url': image_url
    }
    return JsonResponse(response)


@api_view(['GET'])
def check_login_status(request):
    if request.user.is_authenticated:
        return Response({
            'isLoggedIn': True,
            'accountId': request.user.username
        })
    else:
        return Response({
            'isLoggedIn': False
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'detail': 'Current password and new password are required.'}, status=400)

    user = request.user
    if not check_password(current_password, user.password):
        return Response({'detail': 'Current password is incorrect.'}, status=400)

    user.password = make_password(new_password)
    user.save()

    return Response({'detail': 'Password changed successfully.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()  # 删除令牌
    return Response({'detail': 'Logged out successfully.'})

@api_view(['GET'])
def get_data_directory(request):
    # 从数据库中查询所有数据
    data_entries = RemoteSensingData.objects.all()

    # 使用序列化器将查询结果转换为JSON格式
    serializer = RemoteSensingDataSerializer(data_entries, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def get_browse_image(request, data_id):
    try:
        # 从数据库中获取指定ID的数据对象
        data = RemoteSensingData.objects.get(id=data_id)
        # 返回图片文件
        return FileResponse(open(data.browsejpgpath, 'rb'), content_type='image/jpeg')
    except RemoteSensingData.DoesNotExist:
        return HttpResponseNotFound("Image not found")

def download_data(request, data_id):
    # 获取文件路径
    data = RemoteSensingData.objects.get(id=data_id)
    print(data.zpath)
    response = FileResponse(open(data.zpath, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="image_{data_id}.7z"'
    return response