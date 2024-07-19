from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
        if self.custom_quantity <= 0:
            raise UserError(_('You need to set a positive quantity.'))

        xml_id, data = super()._prepare_report_data()

        if 'report_cris' in self.print_format:
            xml_id = 'etiquetas.action_product_simple_label'

        active_model = ''
        if self.product_tmpl_ids:
            products = self.product_tmpl_ids
            active_model = 'product.template'
        elif self.product_ids:
            products = self.product_ids
            active_model = 'product.product'
        else:
            raise UserError(_("No product to print, if the product is archived please unarchive it before printing its label."))

        # Ensure products is a recordset
        products = self.env[active_model].browse(products.ids)

        data = {
            'active_model': active_model,
            'quantity_by_product': {p.id: self.custom_quantity for p in products},
            'layout_wizard': self.id,
            'products': products.ids,
            'price_included': 'xprice' in self.print_format,
        }

        _logger.debug("XML ID: %s", xml_id)
        _logger.debug("Data: %s", data)

        return xml_id, data

class ReportProductLabel(models.AbstractModel):
    _name = 'report.etiquetas.report_productlabel_cris'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.debug("Doc IDs: %s", docids)
        _logger.debug("Data: %s", data)

        model = self.env[data['active_model']]
        products = model.browse(docids)

        if not products:
            _logger.debug("No products found for IDs: %s", docids)

        quantity = data.get('quantity_by_product', {})
        barcode_and_qty = {product.id: (product.barcode, quantity.get(product.id, 0)) for product in products}

        print("Products Recordset: %s", products)
        print("Quantity: %s", quantity)
        print("Barcode and Quantity: %s", barcode_and_qty)

        _logger.debug("Products Recordset: %s", products)
        _logger.debug("Quantity: %s", quantity)
        _logger.debug("Barcode and Quantity: %s", barcode_and_qty)

        return {
            'docs': products,
            'quantity': quantity or {},
            'barcode_and_qty': barcode_and_qty,
        }
