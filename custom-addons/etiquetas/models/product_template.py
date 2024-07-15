# my_custom_module/models/product_template.py
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ensamblado = fields.Boolean(string="Ensamblado")
    weight = fields.Float(string="Peso")
    manufacturer = fields.Char(string="Fabricante")
