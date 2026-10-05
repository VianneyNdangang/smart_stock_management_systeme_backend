
from django.db import models
from django.utils.translation import gettext_lazy as _

class RegionChoices(models.TextChoices):
    ADAMAOUA = "CM-AD", _("Adamaoua")
    CENTRE = "CM-CE", _("Centre")
    EST = "CM-ES", _("Est")
    EXTREME_NORD = "CM-EN", _("Extrême-Nord")
    LITTORAL = "CM-LT", _("Littoral")
    NORD = "CM-NO", _("Nord")
    NORD_OUEST = "CM-NW", _("Nord-Ouest")
    OUEST = "CM-OU", _("Ouest")
    SUD = "CM-SU", _("Sud")
    SUD_OUEST = "CM-SW", _("Sud-Ouest")
    
    
    @classmethod
    def has_value(cls, value):
        """Vérifier si une valeur existe dans les choix"""
        return value in cls.values

    @classmethod
    def get_label(cls, code):
        """Retourne le label à partir du code"""
        return dict(cls.choices).get(code)

    @classmethod
    def as_dict(cls):
        """Retourne toutes les régions sous forme de dict code → label"""
        return {code: label for code, label in cls.choices}
    
    @classmethod
    def get_regions_for_api(cls):
        """Retourner les régions formatées pour l'API"""
        return [
            {"code": code, "name": str(label)} 
            for code, label in cls.choices
        ]
   