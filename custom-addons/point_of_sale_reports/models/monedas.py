from odoo import api, fields, models, _

class Moneda_Billetes(models.Model):
    _inherit = "pos.bill"

    denominacion = fields.Char(string="Denominación")
