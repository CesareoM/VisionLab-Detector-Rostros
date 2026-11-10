import base64
import binascii
import cv2
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .services import detect_faces
from .models import DetectionRecord

@ensure_csrf_cookie
def home(request):
    return render(request, 'detector/home.html')

@require_POST
def analyze(request):
    # Límite de tamaño para reducir abuso y consumo de memoria
    if len(request.body) > 2_000_000:
        return JsonResponse({'error':'Fotograma demasiado grande'}, status=413)
    try:
        import json
        data=json.loads(request.body)
        raw=data.get('image','')
        if not isinstance(raw,str) or not raw.startswith('data:image/jpeg;base64,'):
            raise ValueError('Se requiere imagen JPEG')
        blob=base64.b64decode(raw.split(',',1)[1],validate=True)
        frame=cv2.imdecode(np.frombuffer(blob,dtype=np.uint8),cv2.IMREAD_COLOR)
        if frame is None or frame.shape[0]*frame.shape[1] > 1920*1080:
            raise ValueError('Imagen inválida o demasiado grande')
        boxes=detect_faces(frame)
        return JsonResponse({'count':len(boxes),'boxes':boxes,'width':frame.shape[1],'height':frame.shape[0]})
    except (ValueError,KeyError,TypeError,binascii.Error,UnicodeDecodeError):
        return JsonResponse({'error':'Imagen o petición no válida'},status=400)

@require_POST
def save_count(request):
    try:
        import json
        count=json.loads(request.body).get('count')
        if type(count) is not int or not 0 <= count <= 1000:
            raise ValueError()
        record=DetectionRecord.objects.create(face_count=count)
        return JsonResponse({'saved':True,'id':record.pk})
    except (ValueError,TypeError):
        return JsonResponse({'error':'Conteo inválido'},status=400)
