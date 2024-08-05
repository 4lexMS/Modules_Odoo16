
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_discounts = fields.Boolean("Descuentos Clientes VIP", related="pos_config_id.customer_discounts", readonly=False)
    discount_birthday = fields.Float("Descuento por cumpleaños", related="pos_config_id.discount_birthday", readonly=False)
    discount_card_payment = fields.Float("Descuento pago con TC", related="pos_config_id.discount_card_payment", readonly=False)
    discount_cash_payment = fields.Float("Descuento pago en efectivo", related="pos_config_id.discount_cash_payment", readonly=False)

