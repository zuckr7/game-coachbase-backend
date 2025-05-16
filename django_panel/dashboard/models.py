import uuid
from django.db import models
from .cb import CB

class LevelDoc(models.Model):
    level_id   = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name       = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    data       = models.JSONField()

    class Meta:
        managed = True
        verbose_name = "Level"
        verbose_name_plural = "Levels"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        doc = {
            "level_id":   str(self.level_id),
            "name":       self.name,
            "difficulty": self.difficulty,
            "data":       self.data,
        }
        CB.levels_col.upsert(str(self.level_id), doc)

    def delete(self, *args, **kwargs):
        CB.levels_col.remove(str(self.level_id))
        super().delete(*args, **kwargs)

class UserProgressDoc(models.Model):
    user_id     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username    = models.CharField(max_length=150)         # ← добавляем здесь
    points      = models.IntegerField(default=0)
    coins       = models.IntegerField(default=0)
    passedLevel = models.IntegerField(default=0)
    items       = models.JSONField(blank=True, default=list)

    class Meta:
        managed = True
        verbose_name = "User Progress"
        verbose_name_plural = "User Progresses"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # upsert всего документа, включая username
        full_doc = CB.users_col.get(str(self.user_id)).content_as[dict] if CB.users_col.exists(str(self.user_id)) else {
            "user_id": str(self.user_id),
            "username": self.username,
            "version": 0,
            "password_hash": "",
            "progress": {}
        }
        full_doc.update({
            "username": self.username,
            "progress": {
                "points":      self.points,
                "coins":       self.coins,
                "passedLevel": self.passedLevel,
                "items":       self.items,
            },
            "version": full_doc.get("version", 0) + 1
        })
        CB.users_col.upsert(str(self.user_id), full_doc)

    def delete(self, *args, **kwargs):
        CB.users_col.remove(str(self.user_id))
        super().delete(*args, **kwargs)
