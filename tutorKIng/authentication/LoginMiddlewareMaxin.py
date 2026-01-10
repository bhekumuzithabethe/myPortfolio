from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect

# =============================
# LoginCheckMiddleware
# =============================
# This middleware restricts authenticated users to access only their allowed views,
# and ensures unauthenticated users can't access protected routes.
class LoginCheckMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Allow media and static files to pass through
        if request.path.startswith('/media/') or request.path.startswith('/static/'):
            return None

        modulename = view_func.__module__  # Get the module where the view resides
        user = request.user

        if user.is_authenticated:
            # If the user is an Admin
            if user.user_type == 'Admin':
                # Allow Admin to access admin and auth views
                if modulename == 'administration.views':
                    pass
                elif modulename == 'authentication.views':
                    pass
                else:
                    # Redirect Admins trying to access unauthorized areas
                    return redirect(reverse('administrator'))

            # If the user is a Tutor
            elif user.user_type == 'Tutor':
                # Allow Tutor to access tutor and auth views
                if modulename == 'tutor.views':
                    pass
                elif modulename == 'authentication.views':
                    pass
                else:
                    # Redirect Tutors trying to access unauthorized areas
                    return redirect(reverse('tutor'))
             # If the user is a Learner
            elif user.user_type == 'Learner':
                # Allow Tutor to access tutor and auth views
                if modulename == 'learner.views':
                    pass
                elif modulename == 'authentication.views':
                    pass
                else:
                    # Redirect Tutors trying to access unauthorized areas
                    return redirect(reverse('learner'))

        else:
            # If the user is not authenticated
            # Allow access to login and auth views
            if request.path == reverse('dologin') or modulename.startswith('django.contrib.admin') or modulename == 'authentication.views' or  modulename.startswith('django.contrib.auth.views') or modulename.startswith('/media/') or modulename.startswith('/static/') :
                pass
            else:
                # Redirect unauthenticated users to login page
                return redirect(reverse('dologin'))
            