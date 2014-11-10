from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from robokassa.forms import RobokassaForm


@login_required
def pay_with_robokassa(request):
    form = RobokassaForm(initial={
        'OutSum': '100.00',
        'InvId': '1',
        'Desc': 'Some item',
        'Email': request.user.email or 'user@example.com',

        # 'UserId': request.user.pk,
        # 'SiteId': 1
    })

    return render(request, 'robokassa/form.html', {'form': form})
