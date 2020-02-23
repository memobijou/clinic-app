from django.urls import path, include
from proposal.viewsets import ProposalViewset
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'proposals', ProposalViewset, basename="proposal")


urlpatterns = [
    path(r'users/<int:user_id>/', include(router.urls)),
]
