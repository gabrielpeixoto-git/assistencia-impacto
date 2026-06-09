from fpdf import FPDF

# Teste simples do fpdf2
pdf = FPDF()
pdf.add_page()
pdf.set_font("Helvetica", size=12)
pdf.cell(200, 10, text="Hello World!", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(200, 10, text="Teste de PDF", new_x="LMARGIN", new_y="NEXT", align="C")

output = bytes(pdf.output())
print(f'Tamanho: {len(output)} bytes')

# Tentar encontrar texto de outras formas
texto_comum = b"Hello"
if texto_comum in output:
    print(f'Texto "Hello" encontrado no PDF!')
else:
    print(f'Texto "Hello" NÃO encontrado')

# Verificar se há stream de dados
if b"stream" in output:
    print(f'Stream encontrado: {output.count(b"stream")} vezes')

# Salvar arquivo para inspeção manual
with open("/tmp/test_fpdf2.pdf", "wb") as f:
    f.write(output)
print("PDF salvo em /tmp/test_fpdf2.pdf")
