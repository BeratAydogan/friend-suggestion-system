from django.db import models
from django.contrib.auth.models import User

class Follow(models.Model):
    follower = models.CharField(max_length=100)
    followed = models.CharField(max_length=100)
    level = models.IntegerField(default=1)  # Ortak takipçi sayısına göre güncellenecek.

    def __str__(self):
        return self.user

class Follow(models.Model):
    follower = models.CharField(max_length=100)
    followed = models.CharField(max_length=100)
    level = models.IntegerField(default=1)  # Ortak takipçi sayısına göre güncellenecek.

    def __str__(self):
        return f"{self.follower} follows {self.followed}"


    def update_level(self):
        # A'nın takip ettiği kullanıcılar
        direct_followed = Follow.objects.filter(follower=self.follower).values_list('followed', flat=True)

        # A'nın takip ettiği kullanıcılar arasında D'yi takip edenleri bul
        mutual_followers = Follow.objects.filter(
            follower__in=direct_followed,
            followed=self.followed
        )

        # Yeni takip edilen kişiyle ilişki seviyesini güncelle
        self.level = 1 + mutual_followers.count()
        
        # Eğer takip edilen de beni takip ediyorsa, level artır
        if Follow.objects.filter(follower=self.followed, followed=self.follower).exists():
            self.level += 1
        print(f"Updated level for {self.follower} following {self.followed}: {self.level}")

        self.save()
        print(f"Updated level for {self.follower} following {self.followed}: {self.level}")

        # Ortak takipçi olan kişilerin seviyelerini güncelley
        for mutual in mutual_followers:
            print(f"Updating level for mutual follower: {mutual.follower} -> {mutual.followed}")
            if mutual.level == 0:
                mutual.level = 1  # Başlangıç değeri 1
            else:
                mutual.level += 1  # Mevcut seviyeyi bir artır

            mutual.save()
            print(f"Saved updated level for mutual follower: {mutual.follower} -> {mutual.followed}: {mutual.level}")

        # D'yi takip eden A'nın takip ettiği kullanıcıların seviyelerini artır
        for followed_user in direct_followed:
            if Follow.objects.filter(follower=self.followed, followed=followed_user).exists():
                follow_relation = Follow.objects.get(follower=self.followed, followed=followed_user)
                follow_relation.level += 1
                follow_relation.save()
                print(f"Updated level for followed user: {followed_user}: {follow_relation.level}")


