
from odoo import models


class PosSession(models.Model):
    """""Load the field to pos.session"""""
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        """""Load the field birthday to pos.session"""""
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].extend(['is_vip_customer','birthday'])
        return result

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('journal_id')
        return result
