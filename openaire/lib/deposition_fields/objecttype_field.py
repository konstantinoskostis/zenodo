# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from wtforms import RadioField
from invenio.webdeposit_field import WebDepositField
from invenio.webdeposit_field_widgets import InlineListWidget,\
    BigIconRadioInput

__all__ = ['UploadTypeField']

UPLOAD_TYPES = [
    ('publication', 'Publication', [], 'file-alt'),
    ('poster', 'Poster', [], 'columns'),
    ('presentation', 'Presentation', [], 'group'),
    ('dataset', 'Dataset', [], 'table'),
    #('Software', []),
    ('image', 'Image', [], 'bar-chart'),
    ('video', 'Video/Audio', [], 'film'),
    ('software', 'Software', [], 'cogs'),
]

UPLOAD_TYPE_ICONS = dict([(t[0], t[3]) for t in UPLOAD_TYPES])


def subtype_processor(form, field, submit):
    form.image_type.flags.hidden = True
    form.image_type.flags.disabled = True
    form.publication_type.flags.hidden = True
    form.publication_type.flags.disabled = True
    if field.data == 'publication':
        form.publication_type.flags.hidden = False
        form.publication_type.flags.disabled = False
    elif field.data == 'image':
        form.image_type.flags.hidden = False
        form.image_type.flags.disabled = False


def set_license_processor(form, field, submit):
    if field.data == "dataset":
        # i.e user likely didn't change default
        if form.license.data == 'cc-by':
            form.license.data = 'cc-zero'
    else:
        # i.e user likely didn't change default
        if form.license.data in ['cc-zero', 'cc-by']:
            form.license.data = 'cc-by'


class UploadTypeField(WebDepositField, RadioField):

    """
    Field to render a list
    """
    widget = InlineListWidget()
    option_widget = BigIconRadioInput(icons=UPLOAD_TYPE_ICONS)

    def __init__(self, **kwargs):
        kwargs['choices'] = [(x[0], x[1]) for x in UPLOAD_TYPES]
        kwargs['processors'] = [
            subtype_processor,
            set_license_processor,
        ]

        super(UploadTypeField, self).__init__(**kwargs)
