from odoo import models, fields, api
import math

# --- FASE 5: Definición de variables en Cliente ---
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    x_llantas_porc_envio = fields.Float(string='% Envío (Llantas)', default=0.0)
    x_llantas_porc_1 = fields.Float(string='% Extra 1 (Llantas)', default=0.0)
    x_llantas_porc_2 = fields.Float(string='% Extra 2 (Llantas)', default=0.0)
    x_llantas_ajuste_fijo = fields.Float(string='Ajuste Fijo Llantas ($)', default=0.0)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    x_tipo_cambio = fields.Float(string='TC Real', default=20.00, digits=(16, 4))
    x_tipo_cambio_teza = fields.Float(string='TC Teza / Pegasus', default=25.00, digits=(16, 4))

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_utilidad_manual = fields.Float(string='Utilidad', default=0.00, digits=(16, 4))
    x_costo_total_pesos = fields.Float(string='Costo Total (MXN)', compute='_compute_line_cotizador', store=True, digits=(16, 4))
    x_costo_venta_contable = fields.Float(string='Costo Contable', compute='_compute_line_cotizador', store=True, digits=(16, 4))
    x_precio_local = fields.Float(string='Precio Local', compute='_compute_line_cotizador', store=True, digits=(16, 4))
    x_precio_foraneo = fields.Float(string='Precio Foráneo', compute='_compute_line_cotizador', store=True, digits=(16, 4))

    @api.onchange('product_id', 'order_id.x_tipo_cambio', 'order_id.x_tipo_cambio_teza')
    def _onchange_utilidad_categoria(self):
        for line in self:
            if not line.product_id: continue
            categoria = line.product_id.categ_id.name
            
            if categoria == 'LLANTAS':
                line.x_utilidad_manual = 0.0
            elif categoria in ['Bolsa', 'Mochila Fashion', 'PAÑALERA', 'Set de 2 Piezas', 'Set de 3 piezas']:
                line.x_utilidad_manual = 105.00
            elif categoria == 'MOCHILA':
                tc_r = line.order_id.x_tipo_cambio or 20.00
                tc_t = line.order_id.x_tipo_cambio_teza or 25.00
                p_usd = line.product_id.x_extra_costo if line.product_id.x_extra_costo > 0 else line.product_id.standard_price
                c_teza = ((p_usd * 0.42) * 0.5) * tc_t
                c_ban = ((8.0 * tc_r) / 50.0)
                c_int = (p_usd * tc_r) + c_teza + c_ban + 10.0
                line.x_utilidad_manual = c_int * 0.27
            elif categoria in ['CARTERA', 'Mensajera']:
                line.x_utilidad_manual = 0.00

    @api.depends('product_id', 'order_id.x_tipo_cambio', 'order_id.x_tipo_cambio_teza', 'x_utilidad_manual', 
                 'order_id.partner_id.x_abisai_monto_extra', 'order_id.partner_id.x_abisai_porcentaje_extra',
                 'order_id.partner_id.x_llantas_porc_envio', 'order_id.partner_id.x_llantas_porc_1',
                 'order_id.partner_id.x_llantas_porc_2', 'order_id.partner_id.x_llantas_ajuste_fijo')
    def _compute_line_cotizador(self):
        for line in self:
            if not line.product_id: continue
            
            tc_r = line.order_id.x_tipo_cambio or 20.00
            tc_t = line.order_id.x_tipo_cambio_teza or 25.00
            p_usd = line.product_id.x_extra_costo if line.product_id.x_extra_costo > 0 else line.product_id.standard_price
            cat = line.product_id.categ_id.name
            partner = line.order_id.partner_id
            
            if cat == 'LLANTAS':
                # --- FASE 4: LÓGICA PEGASSUS ---
                comision_banco = (p_usd * 0.05) * tc_r
                costo_pegassus = p_usd * 1.0 * 0.2032 * tc_t
                c_base = (p_usd * tc_r) + comision_banco + costo_pegassus
                p_local = math.ceil(c_base + (c_base * 0.20) + 25.0)
                comision_foranea = (p_local - c_base) * 0.032
                p_foraneo_base = math.floor(p_local + comision_foranea)
                
                # --- FASE 5: CASCADA DE CLIENTE ---
                p_envio = partner.x_llantas_porc_envio or 0.0
                p_1 = partner.x_llantas_porc_1 or 0.0
                p_2 = partner.x_llantas_porc_2 or 0.0
                ajuste = partner.x_llantas_ajuste_fijo or 0.0
                
                precio_final = p_foraneo_base * (1.0 + (p_envio / 100.0)) * (1.0 + (p_1 / 100.0)) * (1.0 + (p_2 / 100.0)) + ajuste
            else:
                # --- LÓGICA ANTERIOR (FASES 2 Y 3) ---
                c_base = (p_usd * tc_r) + (p_usd * 0.42 * 0.5 * tc_t) + ((8.0 * tc_r) / 50.0) + 10.0
                p_local = c_base + line.x_utilidad_manual
                p_foraneo = p_local if cat == 'MOCHILA' else (p_local * 1.032)
                
                if cat == 'CARTERA': p_foraneo -= 40.0
                elif cat == 'Mensajera': p_foraneo -= 30.0
                
                monto_extra = partner.x_abisai_monto_extra or 0.0
                porc_extra = partner.x_abisai_porcentaje_extra or 0.0
                precio_final = (p_foraneo + monto_extra) * (1.0 + (porc_extra / 100.0))
            
            line.update({
                'x_costo_total_pesos': c_base,
                'x_costo_venta_contable': c_base,
                'x_precio_local': p_local,
                'x_precio_foraneo': precio_final,
            })
            if line.order_id.state == 'draft':
                line.price_unit = precio_final