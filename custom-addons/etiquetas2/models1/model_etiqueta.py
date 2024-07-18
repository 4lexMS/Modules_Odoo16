# my_custom_module/models/product_template.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class ModelEtiqueta(models.Model):
    _inherit = 'product.template'

    name = fields.Char(string='Name', required=True)
    default_code = fields.Char(string='Internal Reference')
    list_price = fields.Float(string='Sales Price', default=1.0)

class ProductLayout(models.TransientModel):
    _inherit = 'product.label.layout'
    confirm_report = fields.Boolean(string="Confirmar Reporte")

    print_format = fields.Selection([
        ('dymo', 'Dymo'),
        ('2x7xprice', '2 x 7 with price'),
        ('4x7xprice', '4 x 7 with price'),
        ('4x12', '4 x 12'),
        ('4x12xprice', '4 x 12 with price')], string="Format",
        default='dymo', required=True)

    def process(self):
       for record in self:
            if not record.confirm_report:
                raise UserError(
                    "Debe confirmar el reportepara poder imprimir")
            self.print_format == 'dymo'
            return super(ProductLayout, self).process()
