from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Optional, List
import os
from io import BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Cores do sistema
COR_PRIMARIA = colors.HexColor('#6C63FF')
COR_SECUNDARIA = colors.HexColor('#00D4FF')
COR_TEXTO_ESCURO = colors.HexColor('#1A1D27')
COR_CINZA_CLARO = colors.HexColor('#F8F9FA')
COR_BRANCO = colors.white


class PDFService:
    """Service para geração de PDFs."""
    
    @staticmethod
    def gerar_orcamento_pdf(
        output_path: str,
        numero_orcamento: str,
        cliente_nome: str,
        cliente_email: str,
        cliente_telefone: str,
        cliente_endereco: str,
        titulo: str,
        descricao: str,
        itens: List[dict],
        subtotal: float,
        tipo_desconto: Optional[str],
        valor_desconto: float,
        taxa_imposto: float,
        total: float,
        condicoes_pagamento: Optional[str],
        garantia: Optional[str],
        valido_ate: str,
        empresa_nome: str,
        empresa_cnpj: str,
        empresa_telefone: str,
        empresa_email: str,
        empresa_endereco: str
    ) -> str:
        """Gera PDF de orçamento."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        style_title = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6C63FF'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        style_header = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        style_normal = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        style_bold = ParagraphStyle(
            'CustomBold',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#333333')
        )
        
        elements = []
        
        # Cabeçalho da empresa
        elements.append(Paragraph(empresa_nome, style_title))
        elements.append(Spacer(1, 0.1*inch))
        
        empresa_info = f"""
        <b>CNPJ:</b> {empresa_cnpj}<br/>
        <b>Telefone:</b> {empresa_telefone}<br/>
        <b>Email:</b> {empresa_email}<br/>
        <b>Endereço:</b> {empresa_endereco}
        """
        elements.append(Paragraph(empresa_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Linha separadora
        elements.append(Table([[Paragraph('', style_normal)]], colWidths=[6*inch], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#6C63FF'))
        ])))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informações do orçamento
        elements.append(Paragraph("ORÇAMENTO", style_header))
        
        orcamento_info = f"""
        <b>Número:</b> {numero_orcamento}<br/>
        <b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Válido até:</b> {valido_ate}
        """
        elements.append(Paragraph(orcamento_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informações do cliente
        elements.append(Paragraph("CLIENTE", style_header))
        
        cliente_info = f"""
        <b>Nome:</b> {cliente_nome}<br/>
        <b>Email:</b> {cliente_email}<br/>
        <b>Telefone:</b> {cliente_telefone}<br/>
        <b>Endereço:</b> {cliente_endereco}
        """
        elements.append(Paragraph(cliente_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Descrição do serviço
        elements.append(Paragraph("DESCRIÇÃO DO SERVIÇO", style_header))
        elements.append(Paragraph(titulo, style_bold))
        elements.append(Paragraph(descricao, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabela de itens
        elements.append(Paragraph("ITENS DO ORÇAMENTO", style_header))
        
        table_data = [['Item', 'Qtd', 'Un', 'Unitário', 'Total']]
        for item in itens:
            table_data.append([
                item['descricao'],
                str(item['quantidade']),
                item['unidade'],
                f"R$ {item['preco_unitario']:.2f}",
                f"R$ {item['preco_total']:.2f}"
            ])
        
        table = Table(table_data, colWidths=[3*inch, 0.5*inch, 0.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C63FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Totais
        totais_data = [
            ['Subtotal:', f"R$ {subtotal:.2f}"],
        ]
        
        if valor_desconto > 0:
            if tipo_desconto == "percentual":
                totais_data.append(['Desconto:', f"{valor_desconto}%"])
            else:
                totais_data.append(['Desconto:', f"R$ {valor_desconto:.2f}"])
        
        if taxa_imposto > 0:
            totais_data.append(['Imposto:', f"{taxa_imposto}%"])
        
        totais_data.append(['<b>TOTAL:</b>', f"<b>R$ {total:.2f}</b>"])
        
        totais_table = Table(totais_data, colWidths=[4*inch, 2*inch])
        totais_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#6C63FF'))
        ]))
        elements.append(totais_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Condições de pagamento e garantia
        if condicoes_pagamento:
            elements.append(Paragraph("CONDIÇÕES DE PAGAMENTO", style_header))
            elements.append(Paragraph(condicoes_pagamento, style_normal))
            elements.append(Spacer(1, 0.1*inch))
        
        if garantia:
            elements.append(Paragraph("GARANTIA", style_header))
            elements.append(Paragraph(garantia, style_normal))
            elements.append(Spacer(1, 0.1*inch))
        
        # Rodapé
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Table([[Paragraph('', style_normal)]], colWidths=[6*inch], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#6C63FF'))
        ])))
        elements.append(Spacer(1, 0.1*inch))
        
        footer = f"""
        <center>
        {empresa_nome} - {empresa_cnpj}<br/>
        {empresa_telefone} | {empresa_email}<br/>
        Este orçamento é válido até {valido_ate}
        </center>
        """
        elements.append(Paragraph(footer, style_normal))
        
        # Gerar PDF
        doc.build(elements)
        
        return output_path
    
    @staticmethod
    def gerar_ordem_servico_pdf(
        output_path: str,
        numero_os: str,
        cliente_nome: str,
        cliente_endereco: str,
        tecnico_nome: str,
        titulo: str,
        descricao: str,
        status: str,
        prioridade: str,
        valor_final: float,
        data_agendada: Optional[str],
        empresa_nome: str,
        empresa_cnpj: str
    ) -> str:
        """Gera PDF de ordem de serviço."""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        style_title = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6C63FF'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        style_header = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        style_normal = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        )
        
        elements = []
        
        # Cabeçalho
        elements.append(Paragraph(empresa_nome, style_title))
        elements.append(Spacer(1, 0.1*inch))
        
        # Informações da OS
        elements.append(Paragraph("ORDEM DE SERVIÇO", style_header))
        
        os_info = f"""
        <b>Número:</b> {numero_os}<br/>
        <b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Status:</b> {status.upper()}<br/>
        <b>Prioridade:</b> {prioridade.upper()}
        """
        elements.append(Paragraph(os_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Informações do cliente
        elements.append(Paragraph("CLIENTE", style_header))
        
        cliente_info = f"""
        <b>Nome:</b> {cliente_nome}<br/>
        <b>Endereço:</b> {cliente_endereco}
        """
        elements.append(Paragraph(cliente_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Técnico responsável
        elements.append(Paragraph("TÉCNICO RESPONSÁVEL", style_header))
        elements.append(Paragraph(tecnico_nome, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Descrição do serviço
        elements.append(Paragraph("DESCRIÇÃO DO SERVIÇO", style_header))
        elements.append(Paragraph(titulo, style_normal))
        elements.append(Paragraph(descricao, style_normal))
        elements.append(Spacer(1, 0.2*inch))
        
        # Data agendada
        if data_agendada:
            elements.append(Paragraph("DATA AGENDADA", style_header))
            elements.append(Paragraph(data_agendada, style_normal))
            elements.append(Spacer(1, 0.2*inch))
        
        # Valor
        elements.append(Paragraph("VALOR FINAL", style_header))
        elements.append(Paragraph(f"R$ {valor_final:.2f}", style_normal))
        elements.append(Spacer(1, 0.5*inch))
        
        # Rodapé
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Table([[Paragraph('', style_normal)]], colWidths=[6*inch], style=TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#6C63FF'))
        ])))
        elements.append(Spacer(1, 0.1*inch))
        
        footer = f"""
        <center>
        {empresa_nome} - {empresa_cnpj}<br/>
        OS {numero_os} - {datetime.now().strftime('%d/%m/%Y')}
        </center>
        """
        elements.append(Paragraph(footer, style_normal))
        
        # Gerar PDF
        doc.build(elements)
        
        return output_path


async def gerar_pdf_orcamento(orcamento_id: str, db: AsyncSession) -> bytes:
    """Gera PDF profissional do orçamento. Retorna bytes do PDF."""
    from loguru import logger
    from app.models.orcamento import Orcamento, ItemOrcamento
    from app.models.cliente import Cliente
    
    result = await db.execute(select(Orcamento).where(Orcamento.id == orcamento_id))
    orcamento = result.scalar_one_or_none()
    if not orcamento:
        raise ValueError(f"Orçamento {orcamento_id} não encontrado")
    
    cliente_result = await db.execute(select(Cliente).where(Cliente.id == orcamento.cliente_id))
    cliente = cliente_result.scalar_one_or_none()
    
    itens_result = await db.execute(
        select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id).order_by(ItemOrcamento.ordem)
    )
    itens = itens_result.scalars().all()
    
    logger.info(f"Gerando PDF para orçamento {orcamento.numero_orcamento}, {len(itens)} itens")
    
    # Usar BytesIO corretamente
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Estilos personalizados
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6C63FF'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    style_header = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6
    )
    
    style_bold = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333')
    )
    
    # Cabeçalho da empresa
    elements.append(Paragraph("Assistencia Impacto", style_title))
    elements.append(Spacer(1, 0.1*inch))
    
    empresa_info = """
    <b>Email:</b> contato@assistenciaimpacto.com.br<br/>
    <b>Telefone:</b> (51) 99999-9999<br/>
    """
    elements.append(Paragraph(empresa_info, style_normal))
    elements.append(Spacer(1, 0.2*inch))
    
    # Linha separadora
    elements.append(Table([[Paragraph('', style_normal)]], colWidths=[6*inch], style=TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#6C63FF'))
    ])))
    elements.append(Spacer(1, 0.2*inch))
    
    # Informações do orçamento
    elements.append(Paragraph("ORÇAMENTO", style_header))
    
    orcamento_info = f"""
    <b>Número:</b> {orcamento.numero_orcamento}<br/>
    <b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
    """
    if orcamento.valido_ate:
        orcamento_info += f"<b>Válido até:</b> {orcamento.valido_ate.strftime('%d/%m/%Y')}<br/>"
    elements.append(Paragraph(orcamento_info, style_normal))
    elements.append(Spacer(1, 0.2*inch))
    
    # Informações do cliente
    if cliente:
        elements.append(Paragraph("CLIENTE", style_header))
        
        cliente_info = f"""
        <b>Nome:</b> {cliente.nome}<br/>
        """
        if cliente.email:
            cliente_info += f"<b>Email:</b> {cliente.email}<br/>"
        if cliente.telefone:
            cliente_info += f"<b>Telefone:</b> {cliente.telefone}<br/>"
        elements.append(Paragraph(cliente_info, style_normal))
        elements.append(Spacer(1, 0.2*inch))
    
    # Tabela de itens
    elements.append(Paragraph("ITENS DO ORÇAMENTO", style_header))
    
    table_data = [['Descrição', 'Qtd', 'Un', 'Unitário', 'Total']]
    for item in itens:
        table_data.append([
            item.descricao or '',
            str(int(item.quantidade) if item.quantidade else 1),
            item.unidade or 'un',
            f"R$ {item.preco_unitario or 0:.2f}",
            f"R$ {item.preco_total or 0:.2f}"
        ])
    
    table = Table(table_data, colWidths=[3*inch, 0.5*inch, 0.5*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C63FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Totais
    subtotal = orcamento.subtotal or 0
    desconto = orcamento.valor_desconto or 0
    total = orcamento.total or subtotal
    
    totais_data = [['Subtotal:', f"R$ {subtotal:.2f}"]]
    
    if desconto > 0:
        totais_data.append(['Desconto:', f"R$ {desconto:.2f}"])
    
    totais_data.append(['<b>TOTAL:</b>', f"<b>R$ {total:.2f}</b>"])
    
    totais_table = Table(totais_data, colWidths=[4*inch, 2*inch])
    totais_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#6C63FF'))
    ]))
    elements.append(totais_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Condições de pagamento
    if orcamento.condicoes_pagamento:
        elements.append(Paragraph("CONDIÇÕES DE PAGAMENTO", style_header))
        elements.append(Paragraph(orcamento.condicoes_pagamento, style_normal))
        elements.append(Spacer(1, 0.1*inch))
    
    # Rodapé
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Table([[Paragraph('', style_normal)]], colWidths=[6*inch], style=TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#6C63FF'))
    ])))
    elements.append(Spacer(1, 0.1*inch))
    
    footer = """
    <center>
    Assistencia Impacto<br/>
    contato@assistenciaimpacto.com.br | (51) 99999-9999
    </center>
    """
    elements.append(Paragraph(footer, style_normal))
    
    # Gerar PDF
    doc.build(elements)
    
    # Ler o buffer corretamente
    buffer.seek(0)
    pdf_bytes = buffer.read()
    buffer.close()
    
    logger.info(f"PDF gerado com {len(pdf_bytes)} bytes")
    return pdf_bytes


async def gerar_pdf_ordem_servico(os_id: str, db: AsyncSession) -> bytes:
    """Gera PDF profissional da OS. Retorna bytes do PDF."""
    from app.models.ordem_servico import OrdemServico, ItemOrdemServico, ChecklistOrdemServico
    from app.models.cliente import Cliente
    from app.models.usuario import Usuario
    
    result = await db.execute(select(OrdemServico).where(OrdemServico.id == os_id))
    os_obj = result.scalar_one_or_none()
    if not os_obj:
        raise ValueError(f"OS {os_id} não encontrada")
    
    cliente_result = await db.execute(select(Cliente).where(Cliente.id == os_obj.cliente_id))
    cliente = cliente_result.scalar_one_or_none()
    
    tecnico = None
    if os_obj.tecnico_id:
        tec_result = await db.execute(select(Usuario).where(Usuario.id == os_obj.tecnico_id))
        tecnico = tec_result.scalar_one_or_none()
    
    itens_result = await db.execute(select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os_id))
    itens = itens_result.scalars().all()
    
    checklist_result = await db.execute(select(ChecklistOrdemServico).where(ChecklistOrdemServico.ordem_servico_id == os_id))
    checklist = checklist_result.scalars().all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=20, fontName='Helvetica-Bold', textColor=COR_PRIMARIA, spaceAfter=6)
    story.append(Paragraph("Assistência Impacto", header_style))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, textColor=colors.grey, spaceAfter=12)
    story.append(Paragraph("contato@assistenciaimpacto.com.br | (51) 99999-9999", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COR_PRIMARIA, spaceAfter=12))
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', textColor=COR_TEXTO_ESCURO, spaceAfter=4)
    story.append(Paragraph(f"ORDEM DE SERVIÇO Nº {os_obj.numero_os}", title_style))
    
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=10, spaceAfter=4)
    section_title = ParagraphStyle('SectionTitle', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=COR_PRIMARIA, spaceAfter=8)
    
    grid_data = [
        ['Cliente:', cliente.nome if cliente else 'N/A', 'Técnico:', tecnico.nome_completo if tecnico else 'N/A'],
        ['Status:', str(os_obj.status.value if hasattr(os_obj.status, 'value') else os_obj.status), 'Prioridade:', str(os_obj.prioridade.value if hasattr(os_obj.prioridade, 'value') else os_obj.prioridade)],
    ]
    if os_obj.data_agendada:
        grid_data.append(['Data Agendada:', os_obj.data_agendada.strftime('%d/%m/%Y'), '', ''])
    
    grid_table = Table(grid_data, colWidths=[3*cm, 6*cm, 3*cm, 5*cm])
    grid_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [COR_CINZA_CLARO, COR_BRANCO]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 12))
    
    if os_obj.descricao:
        story.append(Paragraph("DESCRIÇÃO DO SERVIÇO", section_title))
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333333'), spaceAfter=8)
        story.append(Paragraph(os_obj.descricao, body_style))
        story.append(Spacer(1, 8))
    
    if checklist:
        story.append(Paragraph("CHECKLIST", section_title))
        for item in checklist:
            marcador = "☑" if item.concluido else "☐"
            story.append(Paragraph(f"{marcador} {item.descricao}", info_style))
        story.append(Spacer(1, 12))
    
    if itens:
        story.append(Paragraph("MATERIAIS UTILIZADOS", section_title))
        mat_data = [['Descrição', 'Qtd', 'Unid.', 'Custo Unit.', 'Total']]
        for item in itens:
            mat_data.append([
                item.descricao or '',
                str(int(item.quantidade or 1)),
                item.unidade or 'un',
                f"R$ {item.custo_unitario or 0:,.2f}",
                f"R$ {item.custo_total or 0:,.2f}"
            ])
        mat_table = Table(mat_data, colWidths=[8*cm, 1.5*cm, 1.5*cm, 3*cm, 3*cm])
        mat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COR_PRIMARIA),
            ('TEXTCOLOR', (0, 0), (-1, 0), COR_BRANCO),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [COR_BRANCO, COR_CINZA_CLARO]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(mat_table)
        story.append(Spacer(1, 12))
    
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=8))
    assinatura_data = [
        ['_' * 40, '_' * 40],
        ['Técnico Responsável', 'Assinatura do Cliente'],
        [tecnico.nome_completo if tecnico else '', cliente.nome if cliente else ''],
    ]
    assinatura_table = Table(assinatura_data, colWidths=[8*cm, 8*cm])
    assinatura_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(assinatura_table)
    
    story.append(Spacer(1, 12))
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=4))
    story.append(Paragraph("Assistência Impacto — contato@assistenciaimpacto.com.br — (51) 99999-9999", rodape_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
