
from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    customer_discounts = fields.Boolean("Descuentos Clientes VIP")
    discount_birthday = fields.Float("Descuento por cumpleaños")
    discount_card_payment = fields.Float("Descuento pago con TC")
    discount_cash_payment = fields.Float("Descuento pago en efectivo")
