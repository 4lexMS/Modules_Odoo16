# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection([
        ('report_cris', 'Reporte Cristal'),
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price')], string="Format", default='2x7xprice', required=True)

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if 'report_cris' in self.print_format:
            xml_id = 'css_macro_product_label.action_product_simple_cris'
        return xml_id, data
