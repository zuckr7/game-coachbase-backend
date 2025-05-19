from django.core.management.base import BaseCommand
from datetime import datetime
from dashboard.cb import CB
from dashboard.models import LevelDoc, UserProgressDoc, UserDoc

class Command(BaseCommand):
    help = "Import all documents from Couchbase into local SQLite tables"

    def handle(self, *args, **options):
        LevelDoc.objects.all().delete()
        UserProgressDoc.objects.all().delete()
        UserDoc.objects.all().delete()
        self.stdout.write("All local records deleted, starting fresh import…")
        
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

        # ——— Импорт самих пользователей ———
        # (LevelDoc и UserProgressDoc хранят только часть данных,
        #  здесь же мы создаём полные записи пользователей)
        query_all_users = f"SELECT u.* FROM `{CB.users_bucket.name}` AS u"
        rows = CB.cluster.query(query_all_users)
        for r in rows:
            doc = r
            # Попытка распарсить created_at ISO строку
            created_at_raw = doc.get("created_at")
            try:
                created_at = datetime.fromisoformat(created_at_raw)
            except Exception:
                created_at = datetime.now()

            user_obj, created = UserDoc.objects.update_or_create(
                user_id=doc["user_id"],
                defaults={
                    "username":   doc.get("username", ""),
                    "created_at": created_at,
                    "version":    doc.get("version", 1),
                    "vk_id":      doc.get("vk_id", None),
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} User {user_obj.user_id}")
