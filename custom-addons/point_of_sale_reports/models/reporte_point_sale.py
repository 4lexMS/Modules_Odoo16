from odoo import api, fields, models, _

class PointSaleWizard(models.TransientModel):
    _name = 'wizard.point_sale'
    _description = 'Point Sale Wizard'

    start_date = fields.Date(required=True, default=fields.Datetime.now, string="Fecha Inicio")
    end_date = fields.Date(required=True, default=fields.Datetime.now, string="Fecha Fin")
    pos_ids = fields.Many2one('pos.config', string="Punto de Venta", required=True, default=lambda self: self._default_pos_id())
    sesion_ids = fields.Many2one('pos.session', string="Sesión")
    name_user = fields.Char(string="Usuario", default=lambda self: self.env.user.name)

    @api.onchange('pos_ids')
    def _onchange_pos_ids(self):
        if self.pos_ids:
            return {'domain': {'sesion_ids': [('config_id', '=', self.pos_ids.id)]}}
        else:
            return {'domain': {'sesion_ids': []}}

    @api.model
    def _default_pos_id(self):
        # Obtener el primer punto de venta
        pos = self.env['pos.config'].search([], limit=1)
        return pos and pos.id or False

    def action_generate_report(self):
        # Lógica para generar el reporte
        # Puedes personalizar esto según tus necesidades
        return {
            'type': 'ir.actions.report',
            'report_name': 'tu_modulo.report_template_name',  # Asegúrate de que este nombre sea correcto
            'context': self.env.context,
            'res_id': self.id,
        }
