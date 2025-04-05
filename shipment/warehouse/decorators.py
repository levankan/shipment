from django.http import HttpResponseForbidden
from functools import wraps

def warehouse_employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'role', '') == 'warehouse':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("⛔ მხოლოდ საწყობის თანამშრომლებისთვისაა დაშვებული.")
    return _wrapped_view
