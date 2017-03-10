# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
import json
from odoo import http
from odoo.addons.web.controllers import main
from odoo.addons.mail.models import mail_template


class Reports(main.Reports):
    @http.route('/web/report', type='http', auth="user")
    @main.serialize_exception
    def index(self, action, token):
        result = super(Reports, self).index(action, token)
        action = json.loads(action)
        context = dict(http.request.context)
        context.update(action["context"])
        reports = http.request.env['ir.actions.report.xml'].search([
            ('report_name', '=', action['report_name']),
            ('download_filename', '!=', False)])
        for report in reports:
            objects = http.request.session.model(context['active_model'])\
                .browse(context['active_ids'])
            generated_filename = mail_template.mako_template_env\
                .from_string(report.download_filename)\
                .render({
                    'objects': objects,
                    'o': objects[0],
                    'object': objects[0],
                })
            result.headers['Content-Disposition'] = main.content_disposition(
                generated_filename)
        return result
