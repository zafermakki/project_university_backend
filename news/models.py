from django.db import models

class News(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='news_images/')
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "news"
        verbose_name_plural = "News"
        
    def __str__(self) -> str:
        return self.name
