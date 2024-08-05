
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_vip_customer = fields.Boolean("Descuentos Clientes VIP")
    birthday = fields.Date(string="Fecha de nacimiento")
