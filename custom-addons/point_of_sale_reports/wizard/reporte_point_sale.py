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
    total_arqueo = fields.Float(string="Total Arqueo", compute="_compute_arqueo")
    diferencia = fields.Float(string="Diferencia", compute="_compute_diferencia")
    monedas = fields.Float(string="Monedas")
    billetes = fields.Float(string="Billetes")
    fondo_caja = fields.Float(string="Fondo de Caja", compute="_compute_fondo_caja")
    dep_sug = fields.Float(string="Dep Sugerido", compute="_compute_dep_sug")
    observacion = fields.Text(string="Observación")
    denominaciones = fields.Many2many('pos.bill', string="Denominaciones", domain="[('pos_config_ids', 'in', caja)]")
    cash_details_start = fields.Text(string="Detalle de Inicio de Caja")
    cash_details_end = fields.Text(string="Detalle de Cierre de Caja")
    metodo_pago_ids = fields.Many2many('pos.payment.method', string="Métodos de Pago", compute="_compute_metodo_pago_ids")

    valor_pago = fields.Many2many('pos.payment', string="Valores pago", compute="_compute_valores_pago")

    def get_denominaciones(self):
        self.denominaciones = self.env['pos.bill'].search([('pos_config_ids', 'in', self.caja.id)]).mapped('denominacion')

    @api.onchange('caja')
    def _onchange_pos_ids(self):
        if self.caja:
            sesiones = self.env['pos.session'].search([('config_id', '=', self.caja.id)])
            self.sesion_caja = sesiones and sesiones[0] or False
            #denominaciones = self.env['pos.bill'].search([('pos_config_ids', '=', self.caja.id)]).mapped('denominacion')
            #self.denominaciones = denominaciones[:1] if denominaciones else False

        else:
            self.sesion_caja = False
            #self.denominaciones = False

    @api.model
    def _default_pos_id(self):
        return self.env['pos.config'].browse(1).id or False

    @api.depends('sesion_caja')
    def _compute_metodo_pago_ids(self):
        for record in self:
            if record.sesion_caja:
                pagos = self.env['pos.payment'].search([('session_id', '=', record.sesion_caja.id)])
                record.metodo_pago_ids = pagos.mapped('payment_method_id')
            else:
                record.metodo_pago_ids = False

    @api.depends('sesion_caja')
    def _compute_valores_pago(self):
        for record in self:
            if record.sesion_caja:
                pagos = self.env['pos.payment'].search([('session_id', '=', record.sesion_caja.id)])
                record.valor_pago = pagos
            else:
                record.valor_pago = False

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

class PosArqueoLine(models.TransientModel):
    _name = 'wizard.point_sale.line'
    _description = 'Detalle de Arqueo de Caja'

    nombre = fields.Char(string="Denominación")
    cantidad = fields.Integer(string="Cantidad")
    total = fields.Float(string="Total")
    arqueo_id = fields.Many2one('wizard.point_sale', string="Arqueo")
