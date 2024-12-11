from django.db import models
from products.models import SubCategory

class Newgames(models.Model):
    name = models.CharField(max_length= 250, unique= True)
    image_path = models.ImageField(upload_to= 'newgames/')
    description = models.TextField(default= "", blank= True)
    video_url = models.URLField(max_length= 200, blank=True, null=True)
    release_date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(default=0,null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=4,null=True, blank=True)
    game_type = models.ForeignKey(
        SubCategory,
        on_delete= models.CASCADE,
        related_name='new_games',
        null= True,
        blank= True,
        limit_choices_to={'parent_category__name': 'Games'}
    )
     
    
    class Meta:
        db_table = 'newgames'
            
    def __str__(self) -> str:
        return self.name