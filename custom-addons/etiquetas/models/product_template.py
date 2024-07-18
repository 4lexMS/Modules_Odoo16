from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

class ProductLayout(models.TransientModel):
    _inherit = 'product.label.layout'
    confirm_report = fields.Boolean(string="Confirmar Reporte")

    print_format = fields.Selection([
        ('report_cris', 'Reporte Cristal'),
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price')], string="Format", default='2x7xprice', required=True)

    custom_quantity = fields.Integer('Quantity', default=1, required=True)

    def _prepare_report_data(self):

        if self.custom_quantity <= 0:
            raise UserError(_('You need to set a positive quantity.'))

        xml_id, data = super()._prepare_report_data()

        if 'report_cris' in self.print_format:
            xml_id = 'etiquetas.action_product_simple_label'

        products = []
        active_model = 'product.template'
        if self.product_tmpl_ids:
            products = self.product_tmpl_ids
        elif self.product_ids:
            products = self.product_ids
            active_model = 'product.product'
        else:
            raise UserError(_("No product to print, if the product is archived please unarchive it before printing its label."))

        quantity_by_product = {p.id: self.custom_quantity for p in products}

        updated_data = {
            'active_model': active_model,
            'quantity_by_product': quantity_by_product,
            'layout_wizard': self.id,
            'products': products,
            'price_included': 'xprice' in self.print_format,
        }

        if isinstance(data, tuple):
            data = data[1]  # Si data es un tuple, tomamos solo el segundo elemento

        data.update(updated_data)
        data['quantity'] = updated_data['quantity_by_product']  # Asegurarse de que 'quantity' esté en los datos

        return xml_id, data
