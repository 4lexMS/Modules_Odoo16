from odoo import api, fields, models
from datetime import datetime, time, timedelta

class PointSaleWizard(models.TransientModel):
    _name = 'wizard.point_sale'
    _description = 'Point Sale Wizard'

    fecha_apertura = fields.Date(string='Fecha de Apertura', required=True)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    caja = fields.Many2one('pos.config', string="Punto de Venta", required=True)
    sesion_caja = fields.Many2one('pos.session', string='Sesiones', required=True)
    usuario = fields.Many2one('res.users', string='Usuario', required=True)
    denominaciones = fields.Many2many('your.model.name', string='Denominaciones')

    @api.onchange('fecha_apertura')
    def _onchange_fecha_usuario(self):
        if self.fecha_apertura:
            start_date = datetime.combine(self.fecha_apertura, time.min)
            end_date = datetime.combine(self.fecha_apertura, time.max)

            sessions = self.env['pos.session'].search([
                ('start_at', '>=', start_date),
                ('start_at', '<=', end_date)
            ])

            if sessions:
                user_ids = sessions.mapped('user_id.id')
                session_ids = sessions.mapped('id')

                return {
                    'domain': {
                        'usuario': [('id', 'in', user_ids)],
                        'sesion_caja': [('id', 'in', session_ids)]
                    }
                }
            else:
                return {
                    'domain': {
                        'usuario': [('id', '=', False)],
                        'sesion_caja': [('id', '=', False)]
                    }
                }

    @api.onchange('usuario')
    def _onchange_usuario(self):
        if self.usuario and self.fecha_apertura:
            start_date = datetime.combine(self.fecha_apertura, time.min)
            end_date = datetime.combine(self.fecha_apertura, time.max)

            sessions = self.env['pos.session'].search([
                ('start_at', '>=', start_date),
                ('start_at', '<=', end_date),
                ('user_id', '=', self.usuario.id)
            ])

            if sessions:
                session_ids = sessions.mapped('id')
                return {
                    'domain': {
                        'sesion_caja': [('id', 'in', session_ids)]
                    }
                }
            else:
                return {
                    'domain': {
                        'sesion_caja': [('id', '=', False)]
                    }
                }

    @api.onchange('sesion_caja')
    def _onchange_sesion_caja(self):
        if self.sesion_caja:
            self.caja = self.sesion_caja.config_id.id
        else:
            self.caja = False

    def generate_report_arqueo(self):
        report1 = self.env.ref('point_of_sale_reports.report_arqueo').report_action(self)
        return report1

    def generate_report_egreso(self):
        return self.env.ref('point_of_sale_reports.report_egreso').report_action(self)

    @api.depends('sesion_caja')
    def _compute_saldo_final(self):
        for record in self:
            if record.sesion_caja:
                record.total_caja = record.sesion_caja.cash_register_balance_end_real
            else:
                record.total_caja = 0.0

    @api.depends('sesion_caja')
    def _compute_arqueo(self):
        for record in self:
            if record.sesion_caja:
                record.total_arqueo = record.sesion_caja.cash_register_balance_end
            else:
                record.total_arqueo = 0.0

    @api.depends('sesion_caja')
    def _compute_diferencia(self):
        for record in self:
            if record.sesion_caja:
                record.diferencia = record.sesion_caja.cash_register_difference
            else:
                record.diferencia = 0.0

    @api.depends('sesion_caja')
    def _compute_fondo_caja(self):
        for record in self:
            if record.sesion_caja:
                record.fondo_caja = record.sesion_caja.cash_register_balance_start
            else:
                record.fondo_caja = 0.0

    @api.depends('sesion_caja')
    def _compute_dep_sug(self):
        for record in self:
            if record.sesion_caja:
                record.dep_sug = record.sesion_caja.total_payments_amount
            else:
                record.dep_sug = 0.0
