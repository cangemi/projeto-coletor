from django.shortcuts import render, get_object_or_404
from django.core.files.base import ContentFile
from azure.storage.blob import BlobServiceClient
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from PIL import Image
from django.core.cache import cache
import uuid
import base64
import json
from django.http import JsonResponse
import urllib.parse
from django.conf import settings
from .models import Device, PhotoData

def generate_unique_filename():
    return str(uuid.uuid4())

def upload_to_azure(file_name, file_data):
    # Constrói o cliente Blob
    blob_service_client = BlobServiceClient(account_url=f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net", credential=settings.AZURE_SAS_TOKEN)
    blob_client = blob_service_client.get_blob_client(container=settings.AZURE_CONTAINER, blob=file_name)

    # Upload do arquivo
    blob_client.upload_blob(file_data, blob_type="BlockBlob", overwrite=True)

    # Retorna a URL da imagem no Azure Blob Storage
    return f"https://{settings.AZURE_CUSTOM_DOMAIN}/{settings.AZURE_CONTAINER}/{file_name}"


def correct_base64_padding(base64_string):
    # Adiciona padding necessário se faltar
    missing_padding = len(base64_string) % 4
    if missing_padding:
        base64_string += '=' * (4 - missing_padding)
    return base64_string

@csrf_exempt
def receive(request):
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            temperature = data.get('temperature')
            pressure = data.get('pressure')
            altitude = data.get('altitude')
            device_mac = data.get('device_mac')
            image_chunk = data.get('image_chunk')
            chunk_index = data.get('chunk_index')
            total_chunks = data.get('total_chunks')
            
            # Gera uma chave única para armazenar as partes da imagem no cache
            cache_key = f"image_chunks_{device_mac}"
            stored_chunks = cache.get(cache_key, [])

            # Adiciona a parte atual à lista de partes armazenadas
            stored_chunks.append((chunk_index, image_chunk))
            cache.set(cache_key, stored_chunks, timeout=60 * 5)  # Expira após 5 minutos

            if chunk_index == total_chunks:
                # Ordena as partes e concatena todas em uma única string base64
                stored_chunks.sort(key=lambda x: x[0])
                complete_image_base64 = ''.join([chunk for _, chunk in stored_chunks])
                
                # Limpa o cache para esta chave (opcional)
                cache.delete(cache_key)
                
                # Verifica e decodifica a imagem completa
                decoded_string = urllib.parse.unquote(complete_image_base64)
                if decoded_string and decoded_string.startswith('data:image'):
                    decoded_string = decoded_string.split(',')[1]

                image_url = ''
                if decoded_string:
                    decoded_string = correct_base64_padding(decoded_string)
                    image_data = base64.b64decode(decoded_string)
                    image = Image.open(BytesIO(image_data))

                    # Salva a imagem no Azure Blob Storage (exemplo fictício)
                    image_io = BytesIO()
                    image.save(image_io, format='JPEG')
                    unique_filename = f"{generate_unique_filename()}.png"
                    #image_url = upload_to_azure(unique_filename, image_io.getvalue())
                    image_url = "URL_URL"  # substituir pelo upload para Azure
                    
                device, created = Device.objects.get_or_create(mac_address=device_mac)
                photo_data = PhotoData(
                    device=device,
                    temperature=temperature,
                    pressure=pressure,
                    altitude=altitude,
                    image_link=image_url
                )
                photo_data.save()

                response_data = {
                    'temperature': temperature,
                    'pressure': pressure,
                    'altitude': altitude,
                    'image_saved': bool(decoded_string),
                    'image_url': image_url
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'status': 'Chunk received, waiting for more parts'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except base64.binascii.Error:
            return JsonResponse({'error': 'Invalid base64 string'}, status=400)

    elif request.method == 'GET':
        devices = Device.objects.all()
        photos = None
        selected_device = None
        # Retorna os dados salvos na variável global e a URL da imagem
        device_id = request.GET.get('device_id')
        if device_id:
            selected_device = get_object_or_404(Device, id=device_id)
            photos = PhotoData.objects.filter(device=selected_device).prefetch_related('device')
    
        return render(request, 'device.html', {
            'devices': devices,
            'photos': photos,
            'device': selected_device,
            'SasTokien': settings.AZURE_SAS_TOKEN
        })
    # Retorna uma resposta adequada para outros métodos HTTP, se necessário
    return JsonResponse({'error': 'Method not allowed'}, status=405)