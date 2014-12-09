# -*- coding:utf-8 -*-

# Core Django imports
from django import forms
from django.utils.translation import ugettext_lazy as _


# Thirdy Apps imports
from localflavor.br.forms import BRStateSelect, BRZipCodeField

# Realative imports of the 'app-name' package
from .models import Address, City


class CityForm(forms.ModelForm):
    u"""
    Class of model form City
    """

    class Meta:
        u"""
        Define attributes of this forms
        """

        model = City
        u"""
        Define model used
        """

        exclude = ['created', 'modified']
        u"""
        Remove these attributes
        """

        widgets = {
            'state': BRStateSelect(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


class AddressForm(forms.ModelForm):
    u"""
    Class of model form Adress
    """

    zip_code = BRZipCodeField(
        label=_(u'Zip Code'),
        help_text=_(u'Enter a zip code in the format XXXXX-XXX.'),
        max_length=9,
        required=True
    )

    class Meta:
        u"""
        Define attributes of this forms
        """

        model = Address
        u"""
        Define model used
        """

        exclude = ['created', 'modified']
        u"""
        Remove these attributes
        """
