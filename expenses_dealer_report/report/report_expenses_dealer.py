import math
from odoo import models, api

class ReportExpensesDealerXml(models.AbstractModel):
    _name = 'report.expenses_dealer_report.report_expenses_dealer_xml'
    _description = 'Lógica matemática para el PDF de Gastos Dealer'

    @api.model
    def _get_report_values(self, docids, data=None):
        expenses = self.env['hr.expense'].browse(docids) if docids else self.env['hr.expense'].search([])
        total_general = sum(expenses.mapped('total_amount'))
        
        # 1. Agrupación y cálculo para "ANÁLISIS POR PESTAÑA"
        categories_dict = {}
        for exp in expenses:
            cat_name = exp.product_id.name or 'SIN CATEGORÍA'
            if cat_name not in categories_dict:
                categories_dict[cat_name] = 0.0
            categories_dict[cat_name] += exp.total_amount
        
        analysis_lines = []
        for cat, amount in categories_dict.items():
            percentage = (amount / total_general * 100) if total_general else 0
            analysis_lines.append({
                'categoria': cat,
                'importe': amount,
                'porcentaje': percentage,
                'svg_path': '',
                'color': '#FFFFFF'
            })
        
        analysis_lines = sorted(analysis_lines, key=lambda x: x['importe'], reverse=True)
        
        # 2. NUEVO CÁLCULO PARA EL GRÁFICO (Solución a valores negativos superpuestos)
        # Calculamos el tamaño del pastel basado en el volumen total absoluto
        total_absoluto = sum(abs(line['importe']) for line in analysis_lines)
        
        cx, cy, r = 160, 160, 130
        current_angle = 0.0
        
        colors = [
            '#1A365D', '#2980B9', '#34495E', '#E74C3C', '#2ECC71', 
            '#F1C40F', '#9B5DE5', '#F15BB5', '#00F5D4', '#EE9B00', 
            '#CA6702', '#BB3E03', '#AE2012', '#9B2226'
        ]
        
        for i, line in enumerate(analysis_lines):
            line['color'] = colors[i % len(colors)]
            
            if total_absoluto == 0:
                continue
                
            # Extraemos la proporción física (sin importar el signo) para la geometría
            share_grafico = abs(line['importe']) / total_absoluto
            
            if share_grafico >= 0.999:
                line['svg_path'] = f"M {cx} {cy} m 0 -{r} a {r} {r} 0 1 1 0 {2*r} a {r} {r} 0 1 1 0 -{2*r}"
            elif share_grafico > 0:
                angle = share_grafico * 2 * math.pi
                x1 = cx + r * math.sin(current_angle)
                y1 = cy - r * math.cos(current_angle)
                
                end_angle = current_angle + angle
                x2 = cx + r * math.sin(end_angle)
                y2 = cy - r * math.cos(end_angle)
                
                large_arc = 1 if share_grafico > 0.5 else 0
                
                line['svg_path'] = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
                current_angle = end_angle

        # 3. Obtener el TOP 15
        top_15 = expenses.sorted(key=lambda r: r.total_amount, reverse=True)[:15]
        
        return {
            'doc_ids': docids,
            'doc_model': 'hr.expense',
            'docs': expenses,
            'analysis_lines': analysis_lines,
            'total_general': total_general,
            'top_15': top_15,
        }