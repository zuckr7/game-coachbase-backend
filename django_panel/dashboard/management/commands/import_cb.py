from django.core.management.base import BaseCommand
from dashboard.cb import CB
from dashboard.models import LevelDoc, UserProgressDoc

class Command(BaseCommand):
    help = "Import all documents from Couchbase into local SQLite tables"

    def handle(self, *args, **options):
        # ——— Импорт уровней ———
        query_levels = f"SELECT l.* FROM `{CB.levels_bucket.name}` AS l"
        rows = CB.cluster.query(query_levels)
        for r in rows:
            doc = r
            obj, created = LevelDoc.objects.update_or_create(
                level_id=doc["level_id"],
                defaults={
                    "name":       doc["name"],
                    "difficulty": doc["difficulty"],
                    "data":       doc["data"],
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} Level {obj.level_id}")

        # ——— Импорт прогресса пользователей ———
        query_users = f"SELECT u.* FROM `{CB.users_bucket.name}` AS u"
        rows = CB.cluster.query(query_users)
        for r in rows:
            doc = r
            prog = doc.get("progress", {})
            obj, created = UserProgressDoc.objects.update_or_create(
                user_id=doc["user_id"],
                defaults={
                    "username":    doc.get("username", ""),
                    "points":      prog.get("points", 0),
                    "coins":       prog.get("coins", 0),
                    "passedLevel": prog.get("passedLevel", 0),
                    "items":       prog.get("items", []),
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} UserProgress {obj.user_id}")
