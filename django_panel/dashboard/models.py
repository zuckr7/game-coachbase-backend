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
    username    = models.CharField(max_length=150)
    points      = models.IntegerField(default=0)
    coins       = models.IntegerField(default=0)
    passedLevel = models.IntegerField(default=0)
    items       = models.JSONField(blank=True, default=list)

    class Meta:
        managed = True
        verbose_name = "User Progress"
        verbose_name_plural = "User Progresses"

    def delete(self, *args, **kwargs):
        full_doc = CB.users_col.get(str(self.user_id)).content_as[dict]

        full_doc['progress'] = {
            "passedLevel": 0,
            "points":      0,
            "coins":       0,
            "items":       []
        }
        full_doc['version'] = full_doc.get('version', 0) + 1

        CB.users_col.upsert(str(self.user_id), full_doc)

        self.points = 0
        self.coins = 0
        self.passedLevel = 0
        self.items = []
        super().save(*args, **kwargs)

class UserDoc(models.Model):
    user_id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username      = models.CharField(max_length=150)
    created_at    = models.DateTimeField()
    version       = models.IntegerField(default=1)
    vk_id         = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        verbose_name = "Gamer"
        verbose_name_plural = "Gamers"

    def save(self, *args, **kwargs):
        # 1) Сохраняем локально
        super().save(*args, **kwargs)

        # 2) Upsert в Couchbase: берём существующий документ, обновляем поля
        try:
            full = CB.users_col.get(str(self.user_id)).content_as[dict]
        except:
            full = {}
        full.update({
            "user_id":    str(self.user_id),
            "username":   self.username,
            "created_at": self.created_at.isoformat(),
            "version":    self.version,
            # если vk_id не задан, пропускаем
        })
        if self.vk_id:
            full["vk_id"] = self.vk_id

        CB.users_col.upsert(str(self.user_id), full)

    def delete(self, *args, **kwargs):
        # 1) Удаляем документ из Couchbase
        CB.users_col.remove(str(self.user_id))
        # 2) Удаляем локально
        super().delete(*args, **kwargs)