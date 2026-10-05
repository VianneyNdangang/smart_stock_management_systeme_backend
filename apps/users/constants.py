from django.utils.translation import gettext_lazy as _

ROLE_ADMIN = "ADMIN"
ROLE_MANAGER = "CATEGORY MANAGER"
ROLE_USER = "FOOT WORKER"
ROLE_MAINTAINER = "MAINTAINER"

class Form:
    ROLE_ADMIN = ROLE_ADMIN
    ROLE_MANAGER = ROLE_MANAGER
    ROLE_USER = ROLE_USER
    ROLE_MAINTAINER = ROLE_MAINTAINER
    
    ROLES = [
        (ROLE_ADMIN, _("Administrator")),
	    (ROLE_MANAGER, _("Category manager")),
        (ROLE_USER, _("Foot worker")),
        (ROLE_MAINTAINER, _("Maintainer")),
    ]
        