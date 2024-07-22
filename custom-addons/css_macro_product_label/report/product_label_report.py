# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, models
from collections import defaultdict
from odoo.exceptions import UserError

def _prepare_data(env, data):
    if data.get('active_model') == 'product.template':
        Product = env['product.template'].with_context(display_default_code=False)
    elif data.get('active_model') == 'product.product':
        Product = env['product.product'].with_context(display_default_code=False)
    else:
        raise UserError(_('Product model not defined, Please contact your administrator.'))

    quantity_by_product = defaultdict(list)
    for p, q in data.get('quantity_by_product').items():
        product = Product.browse(int(p))
        product_info = {
            'name': product.name,
            'default_code': product.default_code if product.default_code else '',
            'list_price': product.list_price,
            'quantity': q,
        }
        quantity_by_product[product].append(product_info)
    return {
        'quantity': quantity_by_product,
    }

class ReportProductTemplateLabel(models.AbstractModel):
    _name = 'report.css_macro_product_label.report_producttemplatelabel_cris'
    _description = 'Product Label Report'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, data)
