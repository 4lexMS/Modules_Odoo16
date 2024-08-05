from odoo import api, fields, models, _

class PointSaleWizard(models.TransientModel):
    _name = 'wizard.point_sale'
    _description = 'Point Sale Wizard'

    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company.id)
    fecha = fields.Datetime(required=True, default=fields.Datetime.now, string="Fecha de Apertura")
    caja = fields.Many2one('pos.config', string="Punto de Venta", required=True, default=lambda self: self._default_pos_id())
    sesion_caja = fields.Many2one('pos.session', string="Sesión")
    usuario = fields.Char(string="Usuario", default=lambda self: self.env.user.name)

    total_caja = fields.Float(string="Saldo Final", compute="_compute_saldo_final")
    total_arqueo = fields.Float(string="Total Arqueo")
    diferencia = fields.Float(string="Diferencia")
    monedas = fields.Float(string="Monedas")
    billetes = fields.Float(string="Billetes")
    fondo_caja = fields.Float(string="Fondo de Caja", compute="_compute_fondo_caja")
    dep_sug = fields.Float(string="Dep. Sugerido")
    observacion = fields.Text(string="Observación")
    denominaciones = fields.One2many('wizard.point_sale.line', 'arqueo_id', string="Denominaciones")

    @api.onchange('caja')
    def _onchange_pos_ids(self):
        if self.caja:
            return {'domain': {'sesion_caja': [('config_id', '=', self.caja.id)]}}
        else:
            return {'domain': {'sesion_caja': []}}

    @api.model
    def _default_pos_id(self):
        return self.env['pos.config'].browse(1).id or False

    def generate_report_arqueo(self):        
        return self.env.ref('point_of_sale_reports.report_arqueo').report_action(self)

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
    def _compute_fondo_caja(self):
        for record in self:
            if record.sesion_caja:
                record.fondo_caja = record.sesion_caja.cash_register_balance_start
            else:
                record.fondo_caja = 0.0

class PosArqueoLine(models.TransientModel):
    _name = 'wizard.point_sale.line'
    _description = 'Detalle de Arqueo de Caja'

    nombre = fields.Char(string="Denominación")
    cantidad = fields.Integer(string="Cantidad")
    total = fields.Float(string="Total")
    arqueo_id = fields.Many2one('wizard.point_sale', string="Arqueo")
