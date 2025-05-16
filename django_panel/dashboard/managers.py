from django.db import models
from .cb import CB
from .models import LevelDoc, UserProgressDoc

class LevelManager(models.Manager):
    def get_queryset(self):
        rows = CB.cluster.query(
            f"SELECT `{CB.levels_col.bucket.name}`.* FROM `{CB.levels_col.bucket.name}`"
        )
        objs = []
        for r in rows:
            doc = r[CB.levels_col.bucket.name]
            objs.append(LevelDoc(
                level_id   = doc["level_id"],
                name       = doc["name"],
                difficulty = doc["difficulty"],
                data       = doc["data"],
            ))
        return objs  # не настоящий QuerySet, но ModelAdmin сможет по нему итерироваться

class UserProgressManager(models.Manager):
    def get_queryset(self):
        rows = CB.cluster.query(
            f"SELECT `{CB.users_col.bucket.name}`.* FROM `{CB.users_col.bucket.name}`"
        )
        objs = []
        for r in rows:
            doc = r[CB.users_col.bucket.name]
            prog = doc.get("progress", {})
            objs.append(UserProgressDoc(
                user_id     = doc["user_id"],
                username    = doc["username"],
                points      = prog.get("points", 0),
                coins       = prog.get("coins", 0),
                passedLevel = prog.get("passedLevel", 0),
                items       = prog.get("items", []),
            ))
        return objs

# Привяжем менеджеры
LevelDoc.add_to_class('objects', LevelManager())
UserProgressDoc.add_to_class('objects', UserProgressManager())
