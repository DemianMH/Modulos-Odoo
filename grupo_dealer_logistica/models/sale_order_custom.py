from odoo import models, fields, api
import urllib.request
import json
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    x_tipo_cambio = fields.Float(string='Tipo de Cambio', default=20.50, digits=(16, 4), readonly=False)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_porcentaje_importacion = fields.Float(string='% Importación', default=20.32)
    x_comision_banco = fields.Float(string='Comisión Banco ($)', digits=(16, 2))
    x_utilidad_esperada = fields.Float(string='% Utilidad', default=25.0)
    x_porcentaje_foraneo = fields.Float(string='% Incremento Foráneo', default=3.2)
    
    x_costo_total_pesos = fields.Float(string='Costo Total (MXN)', compute='_compute_line_cotizador', store=True)
    # Campo propio para costo contable, evita el error del sistema
    x_costo_venta_contable = fields.Float(string='Costo Contable', compute='_compute_line_cotizador', store=True)
    
    x_precio_local = fields.Float(string='Precio Local', compute='_compute_line_cotizador', store=True)
    x_precio_foraneo = fields.Float(string='Precio Foráneo', compute='_compute_line_cotizador', store=True)
    x_tipo_precio = fields.Selection([('local', 'Local'), ('foraneo', 'Foráneo')], string='Tipo de Precio', default='local')

    @api.depends('product_id', 'order_id.x_tipo_cambio', 'x_porcentaje_importacion', 'x_comision_banco', 'x_utilidad_esperada', 'x_porcentaje_foraneo', 'x_tipo_precio')
    def _compute_line_cotizador(self):
        for line in self:
            if not line.product_id: continue
            
            imp_factor = line.x_porcentaje_importacion / 100
            util_factor = line.x_utilidad_esperada / 100
            foraneo_factor = line.x_porcentaje_foraneo / 100
            
            costo_base = line.product_id.standard_price
            tc = line.order_id.x_tipo_cambio if line.product_id.x_moneda_costo == 'usd' else 1.0
            
            costo_mxn = (costo_base * tc) + line.product_id.x_extra_costo
            total_costo = (costo_mxn * (1 + imp_factor)) + line.x_comision_banco
            
            line.x_costo_total_pesos = total_costo
            line.x_costo_venta_contable = total_costo # Guardamos nuestro costo aquí
            
            precio_local = total_costo / (1.0 - util_factor) if util_factor < 1 else total_costo + util_factor
            line.x_precio_local = precio_local
            line.x_precio_foraneo = precio_local * (1.0 + foraneo_factor)
            
            if line.order_id.state == 'draft':
                line.price_unit = precio_local if line.x_tipo_precio == 'local' else line.x_precio_foraneo