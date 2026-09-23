from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdministrateurRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Réserve une vue aux collaborateurs connectés ET administrateurs."""

    def test_func(self):
        return self.request.user.administrateur