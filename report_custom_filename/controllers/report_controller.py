# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import http
from odoo.addons.mail.models import mail_template
from odoo.addons.report.controllers.main import ReportController
from odoo.addons.web.controllers.main import content_disposition


class ReportControllerCustom(ReportController):
    @http.route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ])
    def report_routes(self, reportname, docids=None, converter=None, **data):
        response = super(ReportControllerCustom, self).report_routes(
            reportname, docids=docids, converter=converter, **data)
        if docids:
            docids = [int(i) for i in docids.split(',')]
        report_ids = http.request.env['ir.actions.report.xml'].search(
            [('report_name', '=', reportname)])
        for report in report_ids:
            if not report.download_filename:
                continue
            objects = http.request.env[report.model]\
                .browse(docids or [])
            generated_filename = mail_template.mako_template_env\
                .from_string(report.download_filename)\
                .render({
                    'objects': objects,
                    'o': objects[:1],
                    'object': objects[:1],
                    'ext': report.report_type.replace('qweb-', ''),
                })
            response.headers['Content-Disposition'] = content_disposition(
                generated_filename)
        return response

    @http.route(['/report/download'])
    def report_download(self, data, token):
        response = super(ReportControllerCustom, self).report_download(data, token)
        # if we got another content disposition before, ditch the one added
        # by super()
        last_index = None
        for i in range(len(response.headers) - 1, -1, -1):
            if response.headers[i][0] == 'Content-Disposition':
                if last_index:
                    response.headers.pop(last_index)
                last_index = i
        return response
