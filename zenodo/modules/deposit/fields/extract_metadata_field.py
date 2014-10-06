# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
Button that when clicked will try to extract meta-data.
"""

from wtforms import Field
from invenio.modules.deposit.field_base import WebDepositField
from invenio.modules.deposit.field_widgets import ButtonWidget
from invenio.modules.metadataextraction.metadata_extraction import (
    MetadataExtraction
)

__all__ = ['ExtractMetadataField']


def extract_metadata(form, field, submit=False, fields=None):
    if not form.doi.data:
        # get path of the file
        path = form.files[0].path
        metadata_extraction = MetadataExtraction(file_path=path)
        metadata_retrieved = metadata_extraction.get_metadata()
        if not metadata_retrieved:
            # display message that nothing was found
            pass
        else:
            if 'doi' in metadata_retrieved:
                form.doi.data = metadata_retrieved['doi']
                print(form.doi.data)
            if 'title' in metadata_retrieved:
                if isinstance(metadata_retrieved['title'], list):
                    form.title.data = metadata_retrieved['title'][0]
                print(form.title.data)
            if 'author' in metadata_retrieved:
                while len(form.creators.entries) > 0:
                    form.creators.pop_entry()
                for author in metadata_retrieved['author']:
                    form.creators.append_entry(data=dict(
                        name=author,
                        affiliation='',
                    ))
                # add an empty entry
                form.creators._add_empty_entry()
                print(form.creators.data)
            if 'subject' in metadata_retrieved:
                while len(form.keywords.entries) > 0:
                    form.keywords.pop_entry()
                keywords = set(metadata_retrieved['subject'])
                for k in keywords:
                    form.keywords.append_entry(data=k)
                # add an empty entry
                form.keywords._add_empty_entry()
                print(form.keywords.data)


class ExtractMetadataField(WebDepositField, Field):
    widget = ButtonWidget(icon='icon-barcode')

    def __init__(self, **kwargs):
        defaults = dict(
            icon=None,
            processors=[
                extract_metadata
            ],
        )
        defaults.update(kwargs)
        super(ExtractMetadataField, self).__init__(**defaults)

    def _value(self):
        """
        Return true if button was pressed at some point
        """
        return bool(self.data)

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0] is True:
            # Button was pressed
            self.data = True
        else:
            # Reset data tp value of object data.
            self.data = self.object_data
