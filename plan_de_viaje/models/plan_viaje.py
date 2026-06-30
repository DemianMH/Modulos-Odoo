from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PlanViaje(models.Model):
    _name = 'plan.viaje'
    _description = 'Plan de Viaje'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Datos Generales
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    company_id = fields.Many2one('res.company', string='Empresa', default=lambda self: self.env.company, tracking=True)
    user_id = fields.Many2one('res.users', string='Ejecutivo / Vendedor', default=lambda self: self.env.user, tracking=True)
    
    # Planificación
    date_start = fields.Date(string='Fecha de Inicio', required=True, tracking=True)
    date_end = fields.Date(string='Fecha de Regreso', required=True, tracking=True)
    destination = fields.Char(string='Destino / Ciudad', required=True, tracking=True)
    motive = fields.Char(string='Motivo Principal', required=True)
    
    # Relaciones
    partner_ids = fields.Many2many(
        'res.partner', 
        string='Clientes a Visitar', 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    
    # Programas de Lealtad
    loyalty_program_ids = fields.Many2many(
        'loyalty.program',
        string='Programas de Lealtad y Descuentos',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    
    # Pestañas de Detalles
    schedule_notes = fields.Html(string='Cronograma y Citas Programadas')
    pre_analysis = fields.Html(string='Análisis Previo de los Clientes')
    route = fields.Html(string='Ruta y Logística')
    strategies = fields.Html(string='Notas de Estrategias y Activaciones')
    product_rotation = fields.Html(string='Rotación de Productos y Estudio de Campo')
    
    # Flujo de Aprobación
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('done', 'Viaje Finalizado')
    ], string='Estado', default='draft', tracking=True, copy=False)
    
    manager_id = fields.Many2one('res.users', string='Aprobado por', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nuevo')) == _('Nuevo'):
                vals['name'] = self.env['ir.sequence'].next_by_code('plan.viaje') or _('Nuevo')
        return super().create(vals_list)

    # 1. CANDADO ADUANERO PARA BORRAR (unlink)
    def unlink(self):
        for record in self:
            # Si NO es del grupo Director/Acceso Completo
            if not self.env.user.has_group('plan_de_viaje.group_plan_viaje_manager'):
                # Y el viaje NO está en borrador ni en revisión, lanzamos un error en pantalla
                if record.state not in ['draft', 'review']:
                    raise UserError(_('¡Atención! Como Vendedor solo puedes eliminar tus planes de viaje si están en estado "Borrador" o "En Revisión".'))
        return super(PlanViaje, self).unlink()

    # 2. CANDADO ADUANERO PARA EDITAR (write)
    def write(self, vals):
        # Si NO es del grupo Director/Acceso Completo
        if not self.env.user.has_group('plan_de_viaje.group_plan_viaje_manager'):
            for record in self:
                # Si el registro ya está aprobado, rechazado o terminado
                if record.state in ['approved', 'rejected', 'done']:
                    # Permitimos el cambio si ÚNICAMENTE se está modificando el estado (para que funcionen los botones del flujo)
                    if set(vals.keys()) == {'state'}:
                        continue
                    # Si intenta cambiar cualquier otro dato, lo bloqueamos
                    raise UserError(_('¡Acceso Denegado! Este plan de viaje ya fue revisado y sus datos no pueden ser modificados. Contacta a Dirección.'))
        return super(PlanViaje, self).write(vals)

    # Botones de acciones
    def action_submit(self):
        self.write({'state': 'review'})

    def action_approve(self):
        self.write({
            'state': 'approved',
            'manager_id': self.env.user.id
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_done(self):
        self.write({'state': 'done'})