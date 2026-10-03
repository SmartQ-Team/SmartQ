from django.urls import re_path
from smartq.views_spa import spa_index

# Mounted LAST in the root URLconf — the catch-all for React Router.
# Any URL not matched earlier will fall through to the SPA index.
urlpatterns = [
    re_path(r'^(?!api/|admin/|static/|media/).*$', spa_index, name='spa'),
]