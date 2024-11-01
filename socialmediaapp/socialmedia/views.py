from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Follow
# Create your views here.
def index(request):
    users = User.objects.all()
    current_user = request.user

    # Kullanıcılar için takipçi ve takip edilen sayısını hesaplayın
    for user in users:
        user.followers_count = Follow.objects.filter(followed=user.username).count()  # Kullanıcıyı takip edenler
        user.following_count = Follow.objects.filter(follower=user.username).count()  # Kullanıcıyı takip edenler
    
        user.is_following = Follow.objects.filter(follower=current_user.username, followed=user.username).exists()

    if user.is_following:
        follow_button_value='unfollow'
    else:
        follow_button_value='follow'
    

    return render(request, "index.html", {"users": users, "current_user": current_user,"follow_button_value":follow_button_value})

def followers_count(request):
    if request.method == 'POST':
        value = request.POST['value']
        user = request.POST['follower']
        followed = request.POST['followed']

        if value == 'follow':
            follower_cnt= Follow.objects.create(follower=user,followed=followed)
            follower_cnt.save()
            follower_cnt.update_level()
        else:
            follower_cnt= Follow.objects.get(follower=user,followed=followed)
            follower_cnt.delete()
        return redirect("index")