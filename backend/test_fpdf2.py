from fpdf import FPDF

# Teste simples do fpdf2
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Hello World!", ln=True, align="C")
pdf.cell(200, 10, txt="Teste de PDF", ln=True, align="C")

output = bytes(pdf.output())
print(f'Tamanho: {len(output)} bytes')
print(f'Cabeçalho válido: {output[:5] == b"%PDF-"}')
print(f'Termina com EOF: {b"%%EOF" in output[-100:]}')
print(f'Blocos de texto: {output.count(b"BT")}')
print(f'Strings de texto: {output.count(b"string")}')
