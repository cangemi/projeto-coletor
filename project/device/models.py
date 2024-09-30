from django.db import models


class Device(models.Model):
    id = models.AutoField(primary_key=True)
    mac_address = models.CharField(max_length=17, unique=True)  # Endereço MAC do dispositivo
    name = models.CharField(max_length=100, blank=True)  # Nome opcional do dispositivo
    description = models.TextField(blank=True)  # Descrição opcional do dispositivo
    update_available = models.BooleanField(default=False)  # Flag para saber se há atualização disponível
    capture_light = models.IntegerField(default=0)  # Controle da luz de captura, aceita qualquer valor inteiro


    def __str__(self):
        return self.mac_address

class PhotoData(models.Model):
    id = models.AutoField(primary_key=True)
    data = models.DateTimeField(auto_now_add=True)  # Data e hora em que o registro foi criado
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='photo_data')  # Relacionamento com o modelo Device
    temperature = models.FloatField() 
    pressure = models.FloatField()  
    altitude = models.FloatField()  
    image_link = models.URLField(max_length=200)  # Link da imagem (URL)

    def __str__(self):
        return f"PhotoData(id={self.id}, device_mac={self.device.mac_address}, temperature={self.temperature}, pressure={self.pressure}, altitude={self.altitude}, image_link={self.image_link})"