from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import calendar
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

router = APIRouter(prefix="/calendar", tags=["Impressão"])

@router.get("/monthly")
def generate_monthly_calendar(year: int = None, month: int = None):
    # Se não passar data, pega o mês atual
    if not year or not month:
        now = datetime.now()
        year, month = now.year, now.month

    # Cria o PDF na memória RAM
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Margens (Esquerda maior para furação do fichário)
    margin_left = 1.0 * cm
    margin_right = 1.0 * cm
    margin_top = 1.0 * cm
    margin_bottom = 0.5 * cm

    # Título Localizado
    meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    title = f"{meses_pt[month]} {year}"
    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin_left, height - margin_top, title)

    # Matemática da Grade
    grid_width = width - margin_left - margin_right
    grid_height = height - margin_top - 1.5 * cm - margin_bottom 
    
    cols = 7
    cal = calendar.monthcalendar(year, month)
    rows = len(cal)

    col_width = grid_width / cols
    row_height = grid_height / rows

    # Cabeçalho dos Dias da Semana
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    c.setFont("Helvetica-Bold", 12)
    y_days = height - margin_top - 1.0 * cm
    
    for i, dia in enumerate(dias_semana):
        # Centraliza o texto no topo da coluna
        text_width = c.stringWidth(dia, "Helvetica-Bold", 12)
        x = margin_left + (i * col_width) + (col_width - text_width) / 2
        c.drawString(x, y_days, dia)

    # Desenhando as caixas e os números
    c.setFont("Helvetica", 14)
    c.setLineWidth(1)
    y_start_grid = y_days - 0.3 * cm

    for row_idx, week in enumerate(cal):
        for col_idx, day in enumerate(week):
            x_box = margin_left + (col_idx * col_width)
            y_box = y_start_grid - ((row_idx + 1) * row_height)
            
            # Desenha o quadrado
            c.rect(x_box, y_box, col_width, row_height)
            
            # Coloca o número do dia no canto superior esquerdo da caixa
            if day != 0:
                c.drawString(x_box + 5, y_box + row_height - 15, str(day))

    c.showPage()
    c.save()
    buffer.seek(0)
    
    # Devolve o arquivo direto para download/visualização no navegador
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"inline; filename=calendario_{year}_{month}.pdf"}
    )

@router.get("/annual")
def generate_annual_calendar(year: int = None):
    if not year:
        year = datetime.now().year

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    margin = 1.5 * cm
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - margin, f"Calendário Anual - {year}")

    cols = 3
    rows = 4
    month_width = (width - (2 * margin)) / cols
    month_height = (height - (2 * margin) - 1.5 * cm) / rows

    meses_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    for m in range(1, 13):
        col_idx = (m - 1) % cols
        row_idx = (m - 1) // cols 

        x_month = margin + (col_idx * month_width)
        y_month = height - margin - 2.0 * cm - ((row_idx + 1) * month_height)

        # Título do Mês (Aumentado para 14pt)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(x_month + 0.2 * cm, y_month + month_height - 0.5 * cm, meses_pt[m])

        cal = calendar.monthcalendar(year, m)
        
        # Cabeçalho dias (Aumentado para 11pt)
        c.setFont("Helvetica-Bold", 11)
        dias_sigla = ["S", "T", "Q", "Q", "S", "S", "D"]
        for i, sigla in enumerate(dias_sigla):
            if i >= 5:
                c.setFillColorRGB(0.7, 0, 0) 
            else:
                c.setFillColorRGB(0, 0, 0)
            
            # Espaçamento horizontal levemente ajustado para 0.6cm
            c.drawString(x_month + 0.2 * cm + (i * 0.6 * cm), y_month + month_height - 1.1 * cm, sigla)

        # Desenha os números (Aumentado para 12pt)
        c.setFont("Helvetica", 12)
        for r_idx, week in enumerate(cal):
            for c_idx, day in enumerate(week):
                if day != 0:
                    x_day = x_month + 0.2 * cm + (c_idx * 0.6 * cm)
                    y_day = y_month + month_height - 1.7 * cm - (r_idx * 0.5 * cm)
                    
                    if c_idx >= 5:
                        c.saveState()
                        c.setFillColorRGB(1, 0.9, 0.9) 
                        # Retângulo de fundo ajustado para a nova fonte
                        c.rect(x_day - 3, y_day - 3, 0.55 * cm, 0.45 * cm, fill=1, stroke=0)
                        c.restoreState()
                        c.setFillColorRGB(0.7, 0, 0)
                    else:
                        c.setFillColorRGB(0, 0, 0)
                        
                    c.drawString(x_day, y_day, str(day))
        
        c.setFillColorRGB(0, 0, 0)

    c.showPage()
    c.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"inline; filename=anual_{year}.pdf"}
    )