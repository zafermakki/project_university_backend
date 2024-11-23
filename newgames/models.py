from django.db import models

class Newgames(models.Model):
    name = models.CharField(max_length= 250, unique= True)
    image_path = models.ImageField(upload_to= 'newgames/')
    description = models.TextField(default= "", blank= True)
    video_url = models.URLField(max_length= 200, blank=True, null=True)
     
    
    class Meta:
        db_table = 'newgames'
            
    def __str__(self) -> str:
        return self.name