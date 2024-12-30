from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Follow
import random
from django.db.models import Count
from django.db.models import Q
import matplotlib.pyplot as plt
import networkx as nx
from django.http import HttpResponse
from io import BytesIO

# Create your views here.
def get_recommended_users(current_user):
    followed_users = Follow.objects.filter(follower=current_user.username).values_list('followed', flat=True)
    all_users = User.objects.exclude(Q(username=current_user.username) | Q(username__in=followed_users))

    random_users = random.sample(list(all_users), min(5, all_users.count()))

    suggested_users = []
    seen_usernames = set()  

    following = Follow.objects.filter(follower=current_user.username)
    for follow_relation in following.order_by('-level')[:3]:  
        followed_user = follow_relation.followed
        followed_user_followings = Follow.objects.filter(follower=followed_user).exclude(
            Q(followed=current_user.username) | Q(followed__in=followed_users)
        )

        for user_relation in followed_user_followings:
            suggested_user = User.objects.get(username=user_relation.followed)
            if suggested_user.username not in seen_usernames:
                suggested_user.followed_by = followed_user
                suggested_users.append(suggested_user)
                seen_usernames.add(suggested_user.username)

        if len(suggested_users) >= 5:
            break

    random_users = [user for user in random_users if user.username not in seen_usernames]
    for user in random_users:
        user.followed_by = None
        seen_usernames.add(user.username)

    recommended_users = suggested_users[:5] + random_users[:5]

    for user in recommended_users:
        user.is_following = Follow.objects.filter(follower=current_user.username, followed=user.username).exists()

    return recommended_users

def index(request):
    users = User.objects.all()
    current_user = request.user
    
    current_user.followers_count = Follow.objects.filter(followed=current_user.username).count()
    current_user.following_count = Follow.objects.filter(follower=current_user.username).count()

   
    for user in users:
        user.followers_count = Follow.objects.filter(followed=user.username).count()  
        user.following_count = Follow.objects.filter(follower=user.username).count()  

        follow_relation = Follow.objects.filter(follower=current_user.username, followed=user.username).first()
        user.relationship_level = follow_relation.level if follow_relation else None

       
        user.is_following = follow_relation is not None

    recommended_users = get_recommended_users(current_user)

    return render(request, "index.html", {
        "users": users,
        "current_user": current_user,
        "recommended_users": recommended_users
    })


def followers_count(request):
    if request.method == 'POST':
        value = request.POST['value']
        user = request.POST['follower']
        followed = request.POST['followed']

        if value == 'follow':
            follower_cnt = Follow.objects.create(follower=user, followed=followed)
            follower_cnt.save()
            follower_cnt.update_level()
        else:
            follower_cnt = Follow.objects.get(follower=user, followed=followed)
            follower_cnt.delete()

        return redirect("index")





def draw_graph(request):
    relationships = Follow.objects.all()
    G = nx.DiGraph()

    current_user = request.user.username  

    for rel in relationships:
        G.add_edge(rel.follower, rel.followed, weight=rel.level)

    node_colors = ['red' if node == current_user else 'lightblue' for node in G.nodes()]

    pos = nx.shell_layout(G)



    nx.draw(G, pos, with_labels=True, node_size=1500, node_color=node_colors, font_size=10, font_weight="bold")
    nx.draw_networkx_edges(G, pos, width=1, alpha=0.7)
    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.5, font_size=8)


    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png")