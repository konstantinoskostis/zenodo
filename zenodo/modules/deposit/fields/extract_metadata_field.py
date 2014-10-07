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
from invenio.modules.metadataextraction.utils import(
    DoiRegistrationAgency
)
from invenio.modules.metadataextraction.extractors import(
    CrossRefExtractor,
    DataciteExtractor,
    XmpExtractor
)
from invenio.modules.metadataextraction.metadata_extraction import (
    MetadataExtraction
)


__all__ = ['ExtractMetadataField']


def extract_metadata(form, field, submit=False, fields=None):
    # get the file path
    path = form.files[0].path
    if not path.endswith('.pdf'):
        msg = ('It seems that your file is NOT a PDF '
               '\nTherefore we cannot extract meta-data')
        field.add_message(msg, 'error')

    doi_given = form.doi.data
    metadata_retrieved = {}

    if (doi_given and not zenodo_doi(doi_given)):
        msg = ('A published doi was given '
               'We will try to fetch the meta-data.')
        field.add_message(msg, 'info')
        # decide the agency that DOI is registered with
        doi_reg_agency = DoiRegistrationAgency(doi=doi_given)
        agency = doi_reg_agency.agency_id()
        if agency == 'datacite':
            # get meta-data from DataCite
            dc_extractor = DataciteExtractor(doi=doi_given)
            metadata_retrieved = dc_extractor.get_datacite_metadata()
        elif agency == 'crossref':
            # get meta-data from CrossRef
            crossref_extractor = CrossRefExtractor(doi_given)
            if not crossref_extractor.problem_with_connection():
                crossref_extractor.parse_metadata()
                metadata_retrieved = crossref_extractor.get_crossref_metadata()

    elif (not doi_given):
        # (not zenodo_doi(doi_given)
        # run metadata extraction since no doi was given
        metadata_extraction = MetadataExtraction(file_path=path)
        metadata_retrieved = metadata_extraction.get_metadata()
    elif (doi_given and zenodo_doi(doi_given)):
        msg = ("A ZENODO doi was given!\n"
               "Therefore we will try "
               "to fetch the XMP meta-data of the PDF file.")
        field.add_message(msg, 'info')
        # call the XmpExtraction
        xmp_extraction = XmpExtractor(full_file_path=path)
        xmp_meta = xmp_extraction.get_xmp_metadata()
        if xmp_meta:
            # validate xmp_meta
            if xmp_extraction.validate_metadata(xmp_meta) is True:
                metadata_retrieved = xmp_extraction.get_metadata()

    if not metadata_retrieved:
        field.add_message('No meta-data were retrieved', 'warning')
    else:
        if agency == 'datacite':
            if 'title' in metadata_retrieved:
                form.title.data = metadata_retrieved['title']
            if 'description' in metadata_retrieved:
                form.description.data = metadata_retrieved['description']
            if 'creators' in metadata_retrieved:
                while len(form.creators.entries) > 0:
                    form.creators.pop_entry()
                for creator in metadata_retrieved['creators']:
                    form.creators.append_entry(data=dict(
                        name=creator,
                        affiliation='',
                    ))
                # add an empty entry
                form.creators._add_empty_entry()
            if 'subject' in metadata_retrieved:
                while len(form.keywords.entries) > 0:
                    form.keywords.pop_entry()
                keywords = set(metadata_retrieved['subject'])
                for k in keywords:
                    form.keywords.append_entry(data=k)
                # add an empty entry
                form.keywords._add_empty_entry()
        if agency == 'crossref':
            if 'type' in metadata_retrieved:
                doc_type = metadata_retrieved['type']
                if doc_type == 'journal-article':
                    form.upload_type.data = 'publication'
                    form.publication_type.data = 'article'
            if 'doi' in metadata_retrieved:
                form.doi.data = metadata_retrieved['doi']
            if 'title' in metadata_retrieved:
                if isinstance(metadata_retrieved['title'], list):
                    form.title.data = metadata_retrieved['title'][0]
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
            if 'subject' in metadata_retrieved:
                while len(form.keywords.entries) > 0:
                    form.keywords.pop_entry()
                keywords = set(metadata_retrieved['subject'])
                for k in keywords:
                    form.keywords.append_entry(data=k)
                # add an empty entry
                form.keywords._add_empty_entry()
            if 'issue' in metadata_retrieved:
                form.journal_issue.data = metadata_retrieved['issue']
            if 'volume' in metadata_retrieved:
                form.journal_volume.data = metadata_retrieved['volume']
            if 'journal' in metadata_retrieved:
                journal_title = metadata_retrieved['journal']['cref_journal-title']
                form.journal_title.data = journal_title

    # if ((not doi_given) or (not zenodo_doi(doi_given))):
    #     print('File path: {0}'.format(path))
    #     metadata_extraction = MetadataExtraction(file_path=path)
    #     metadata_retrieved = metadata_extraction.get_metadata()
    #     if not metadata_retrieved:
    #         # display message that nothing was found
    #         field.add_message('No meta-data were retrieved', 'warning')
    #     else:
    #         if 'doi' in metadata_retrieved:
    #             form.doi.data = metadata_retrieved['doi']
    #             print(form.doi.data)
    #         if 'title' in metadata_retrieved:
    #             if isinstance(metadata_retrieved['title'], list):
    #                 form.title.data = metadata_retrieved['title'][0]
    #             print(form.title.data)
    #         if 'author' in metadata_retrieved:
    #             while len(form.creators.entries) > 0:
    #                 form.creators.pop_entry()
    #             for author in metadata_retrieved['author']:
    #                 form.creators.append_entry(data=dict(
    #                     name=author,
    #                     affiliation='',
    #                 ))
    #             # add an empty entry
    #             form.creators._add_empty_entry()
    #             print(form.creators.data)
    #         if 'subject' in metadata_retrieved:
    #             while len(form.keywords.entries) > 0:
    #                 form.keywords.pop_entry()
    #             keywords = set(metadata_retrieved['subject'])
    #             for k in keywords:
    #                 form.keywords.append_entry(data=k)
    #             # add an empty entry
    #             form.keywords._add_empty_entry()
    #             print(form.keywords.data)


def zenodo_doi(doi_in):
    if (doi_in.startswith("10.5281") or doi_in.startswith("10.5072")):
        return True
    return False


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
