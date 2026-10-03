from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.cache import never_cache


REACT_INDEX = Path(settings.BASE_DIR) / 'smartq_static' / 'react' / 'index.html'


@never_cache
def spa_index(request):
    """Serve the React SPA index.html for any non-API, non-admin path."""
    if not REACT_INDEX.exists():
        raise Http404(
            'React build not found. Run `npm run build` inside smartq-frontend/.'
        )
    return HttpResponse(REACT_INDEX.read_text(), content_type='text/html')