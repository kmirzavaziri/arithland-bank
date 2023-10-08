from dataclasses import dataclass

from transaction import competition


@dataclass
class MenuItem:
    name: str
    display: str


def add_base_context(request):
    menu = [
        MenuItem('dashboard', 'Dashboard'),
        MenuItem('teams', 'Teams'),
    ]

    if request.user.is_superuser:
        menu.append(MenuItem('transactions', 'Transactions'))
        menu.append(MenuItem('manage', 'Manage'))
        menu.append(MenuItem('admin:index', 'Admin'))

    return {
        'base': {
            'menu': menu,
            'competition': {
                'current_time': competition.get_current_time(),
            },
        }
    }
